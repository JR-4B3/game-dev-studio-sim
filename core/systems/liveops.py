"""Released games: updates, support, prices, promotion and community work."""
from ..content import (BUSINESS_MODEL, COMMUNITY, PRICE_POINTS, PROMOTION, STOREFRONT, SUPPORT, UPDATE_SIZE,
                       UPDATE_SIZES)
from ..game import int_arg, str_arg
from ..state import Commitment, Update
from . import market


def mine(game, product_id):
    for product in game.s.products:
        if product.id == product_id and product.studio_id == 0:
            return product
    raise ValueError("That game is not yours.")


def target_of(game, target):
    """A commitment target: 0 is the game in development, anything else a release."""
    if target == 0:
        project = game.s.studio.project
        if not project or project.stage not in ("production", "polish"):
            raise ValueError("Only a game in production can be promoted before release.")
        return project
    return mine(game, target)


# --- Capacity --------------------------------------------------------------------

def support_need(game):
    total = sum(SUPPORT[p.support]["capacity"] for p in game.s.products if p.studio_id == 0 and not p.retired)
    return min(0.3, total)


def commitment_need(game):
    return sum(c.capacity for c in game.s.studio.commitments)


def wants_update_work(game):
    return bool(game.s.studio.updates)


def update_work(game, output, average_skill):
    s = game.s.studio
    update = s.updates[0]
    update.done += output * (1.25 if game.has("automated_deployment") else 1)
    if update.done < update.work:
        return
    s.updates.pop(0)
    product = next((p for p in game.s.products if p.id == update.product_id), None)
    if not product:
        return
    rule = UPDATE_SIZE[update.size]
    product.bugs = product.bugs * (1 - rule["fixes"]) + update.work * rule["new_bugs"] * 0.2
    product.appeal = min(0.6, product.appeal + rule["appeal"])
    product.sentiment = min(100, product.sentiment + 2 + rule["appeal"] * 30)
    major, minor = (int(x) for x in product.version.split(".")[:2])
    product.version = f"{major + 1}.0" if rule.get("dlc") or update.size == "Expansion" else f"{major}.{minor + 1}"
    if rule["awareness"]:
        for key in product.awareness:
            product.awareness[key] = min(1.0, product.awareness[key] + rule["awareness"] * product.awareness[key] * 10)
    message = f"Shipped {update.size.lower()} {product.version} for \"{product.title}\"."
    if rule.get("dlc"):
        m = game.b.market
        buyers = product.units * m.dlc_attach * (product.rating / 100) ** 2 * (1 - product.greed)
        cut = sum(STOREFRONT[x]["cut"] for x in product.storefronts) / len(product.storefronts)
        income = buyers * m.dlc_price * (1 - cut)
        product.dlc_owners += buyers
        product.revenue += income
        game.earn("DLC sales", income)
        message += f" {buyers:,.0f} players bought the DLC (${income:,.0f})."
    game.log(message)


def on_day(game):
    s = game.s.studio
    for c in list(s.commitments):
        c.days_left -= 1
        if c.days_left <= 0:
            s.commitments.remove(c)


# --- Commands -----------------------------------------------------------------

def queue_update(game, data):
    s = game.s.studio
    product = mine(game, int_arg(data, "id"))
    size = str_arg(data, "size", UPDATE_SIZE)
    rule = UPDATE_SIZE[size]
    if not game.has(rule["research"]):
        raise ValueError(f"{size} needs more research.")
    if len(s.updates) >= 3:
        raise ValueError("Three updates are already planned.")
    if s.cash < rule["cost"]:
        raise ValueError(f"A {size.lower()} costs ${rule['cost']:,.0f} up front.")
    if rule["cost"]:
        game.spend("Updates", rule["cost"])
        product.costs += rule["cost"]
    s.updates.append(Update(product_id=product.id, size=size, work=rule["work"]))
    game.log(f"Planned a {size.lower()} for \"{product.title}\".")


def set_support(game, data):
    product = mine(game, int_arg(data, "id"))
    product.support = str_arg(data, "level", SUPPORT)
    game.log(f"\"{product.title}\" support: {product.support}.")


def set_price(game, data):
    product = mine(game, int_arg(data, "id"))
    if BUSINESS_MODEL[product.model]["free"]:
        raise ValueError("This game is free to download.")
    price = data.get("price")
    if price not in PRICE_POINTS:
        raise ValueError("Invalid price.")
    if price > product.price * 1.2:
        product.sentiment = max(0, product.sentiment - 10)
        game.log(f"Players grumble about the price rise on \"{product.title}\".")
    product.price = float(price)


def promote(game, data):
    s = game.s.studio
    key = str_arg(data, "key", PROMOTION)
    rule = PROMOTION[key]
    target_id = int_arg(data, "target")
    target = target_of(game, target_id)
    if not game.has(rule["research"]):
        raise ValueError(f"{rule['name']} needs more research.")
    if any(c.kind == "promotion" and c.key == key and c.target == target_id for c in s.commitments):
        raise ValueError("That campaign is already running.")
    if s.cash < rule["cost"]:
        raise ValueError(f"{rule['name']} costs ${rule['cost']:,.0f}.")
    if rule["cost"]:
        game.spend("Marketing", rule["cost"])
    effectiveness = 1 - rule["reputation_weight"] * (1 - s.reputation / 100)
    people = rule["people"] * effectiveness * game.rng.uniform(0.8, 1.2)
    if target_id == 0:
        target.costs += rule["cost"]
        market.add_awareness(game, target.awareness, people, target.idea.genre, target.plan.format)
    else:
        target.costs += rule["cost"]
        market.add_awareness(game, target.awareness, people, target.genre, target.format)
    s.commitments.append(Commitment(key=key, kind="promotion", target=target_id, days_left=rule["weeks"] * 7,
                                    capacity=rule["capacity"]))
    name = target.idea.title if target_id == 0 else target.title
    game.log(f"{rule['name']} for \"{name}\": about {people:,.0f} more people heard of it.")


def community(game, data):
    s = game.s.studio
    key = str_arg(data, "key", COMMUNITY)
    rule = COMMUNITY[key]
    target_id = int_arg(data, "target")
    target = target_of(game, target_id)
    if rule.get("project_only") and target_id:
        raise ValueError(f"{rule['name']} is for games in development.")
    if rule.get("release_only") and not target_id:
        raise ValueError(f"{rule['name']} is for released games.")
    if s.cash < rule["cost"]:
        raise ValueError(f"{rule['name']} costs ${rule['cost']:,.0f}.")
    if rule["cost"]:
        game.spend("Community", rule["cost"])
    if target_id == 0:
        recent = False
        if rule.get("reveals_bugs"):
            target.bugs_known += (target.bugs - target.bugs_known) * rule["reveals_bugs"]
        market.add_awareness(game, target.awareness, rule["people"], target.idea.genre, target.plan.format)
        name = target.idea.title
    else:
        last = target.last_community.get(key, -10_000)
        recent = game.s.day - last < rule["cooldown"] * 7
        strength = 0.25 if recent else 1.0
        target.sentiment = min(100, target.sentiment + rule["sentiment"] * strength)
        target.last_community[key] = game.s.day
        market.add_awareness(game, target.awareness, rule["people"] * strength, target.genre, target.format)
        name = target.title
    s.commitments.append(Commitment(key=key, kind="community", target=target_id, days_left=rule["weeks"] * 7,
                                    capacity=rule["capacity"]))
    game.log(f"{rule['name']} for \"{name}\"." + (" Players have heard this recently; it lands softer." if recent else ""))


COMMANDS = {"update": queue_update, "support": set_support, "price": set_price, "promote": promote,
            "community": community}


def view(game):
    s = game.s.studio
    titles = {p.id: p.title for p in game.s.products}
    if s.project:
        titles[0] = s.project.idea.title
    return {
        "updates": [{"product": titles.get(u.product_id, "?"), "product_id": u.product_id, "size": u.size,
                     "progress": u.done / u.work} for u in s.updates],
        "commitments": [{"name": (PROMOTION.get(c.key) if c.kind == "promotion" else COMMUNITY.get(c.key))["name"],
                         "kind": c.kind, "target": titles.get(c.target, "?"), "weeks_left": round(c.days_left / 7, 1),
                         "capacity": c.capacity} for c in s.commitments],
        "update_sizes": [{"name": u["name"], "cost": u["cost"], "work": u["work"],
                          "lock": "" if game.has(u["research"]) else "Needs research"} for u in UPDATE_SIZES],
        "promotions": [{**p, "lock": "" if game.has(p["research"]) else "Needs research"} for p in PROMOTION.values()],
        "community_actions": list(COMMUNITY.values()),
        "support_levels": [s_["name"] for s_ in SUPPORT.values()],
    }
