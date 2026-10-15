"""Rival studios. They sell through the same Market as the player, pay their
staff, borrow, grow, shrink, sell out and go bankrupt.

Only their production is abstract: a Rival project is a team, a budget and a
countdown, not a day-by-day simulation. Nothing is scripted. A giant falls
when its own decisions (bad management, squeezing players for money, a run of
weak games) drain its cash faster than its size can absorb.
"""
import math

from ..content import (BUSINESS_MODEL, COHORTS, GENRE_FAMILIES, RIVALS, SCOPES, STUDIO_NAME_PARTS)
from ..genres import GENRES, GOOD_MATCHES
from ..state import Plan, Rival, RivalProject
from . import ideas as idea_rules
from . import market

SOCIAL_FAMILIES = {"social", "action"}


def setup(game):
    rng = game.rng
    for spec in RIVALS:
        create(game, spec["name"], spec["staff"], spec["skill"], spec["reputation"], spec["fans"], spec["greed"],
               list(spec["genres"]), management=rng.uniform(0.55, 0.9))
    for _ in range(18):
        found(game, quiet=True)
    for rival in game.s.rivals:
        seed_catalog(game, rival)
        for _ in range(3):
            start_project(game, rival, head_start=True)
    # Settle one week of sales so the charts aren't empty on day one.
    market.on_week(game)


def create(game, name, staff, skill, reputation, fans, greed, genres, management, cash=None):
    rng = game.rng
    burn = staff * salary(game, staff) / 12
    rival = Rival(id=game.new_id(), name=name, staff=staff, skill=skill, reputation=reputation,
                  fans=spread_fans(fans, genres), greed=greed, genres=genres,
                  cash=cash if cash is not None else burn * rng.uniform(8, 30), management=round(management, 3),
                  founded_day=game.s.day, revenue_history=[0.0])
    game.s.rivals.append(rival)
    return rival


def spread_fans(total, genres):
    weights = {c["key"]: c["population"] * max(market.taste(c, g) for g in genres) ** 2 for c in COHORTS}
    norm = sum(weights.values())
    return {k: total * w / norm for k, w in weights.items()}


def studio_name(rng, taken):
    for _ in range(50):
        name = f"{rng.choice(STUDIO_NAME_PARTS[0])} {rng.choice(STUDIO_NAME_PARTS[1])}"
        if name not in taken:
            return name
    return f"Studio {rng.randint(100, 999)}"


def found(game, quiet=False):
    rng = game.rng
    taken = {r.name for r in game.s.rivals}
    staff = rng.choice((1, 1, 2, 2, 3, 4, 6))
    rival = create(game, studio_name(rng, taken), staff, rng.uniform(48, 72), rng.uniform(20, 50),
                   rng.uniform(0, 3_000), 0.05, rng.sample(GENRES, 3), management=rng.uniform(0.35, 0.85),
                   cash=rng.uniform(15_000, 150_000))
    if not quiet:
        game.news(f"A new studio, {rival.name}, opened its doors.")
    return rival


def active(game):
    return [r for r in game.s.rivals if r.closed_day < 0]


def salary(game, staff):
    b = game.b.rivals
    return b.salary + (b.salary_large - b.salary) * min(1.0, staff / 200)


def burn(game, rival):
    return rival.staff * salary(game, rival.staff) / 12


def scope_index(name):
    return next(i for i, s in enumerate(SCOPES) if s["name"] == name)


# --- Projects -------------------------------------------------------------------

def pick_genre(game, rival):
    rng = game.rng
    weights = []
    for genre in GENRES:
        heat = game.s.market.heat.get(genre, 1.0)
        own = 3.0 if genre in rival.genres else 0.15
        # Well-run studios follow their strengths; badly run ones chase trends.
        weights.append(own * heat ** (1 + 2 * (1 - rival.management)))
    return rng.choices(GENRES, weights)[0]


def start_project(game, rival, head_start=False):
    b, rng = game.b.rivals, game.rng
    free = rival.staff - sum(p.staff for p in rival.projects)
    room = rival.cash + max(0.0, b.debt_limit_months * burn(game, rival) * 0.5 - rival.debt)
    choice = None
    for index in range(len(SCOPES) - 1, -1, -1):
        staff = b.scope_staff[index]
        if staff > free:
            continue
        monthly = SCOPES[index]["setup"] / b.scope_months[index] + staff * salary(game, rival.staff) / 12
        if monthly * 6 <= room or index <= 1:
            choice = index
            break
    if choice is None:
        return False
    if choice > 1 and rng.random() < 0.25:
        choice -= 1  # a smaller, safer game now and then
    scope = SCOPES[choice]
    staff = b.scope_staff[choice]
    genre = pick_genre(game, rival)
    families = set(GENRE_FAMILIES[genre])
    online = families & SOCIAL_FAMILIES and choice >= 3 and rng.random() < 0.45
    fmt = ("Competitive online" if "social" in families and choice >= 4 else "Online co-op") if online else "Offline solo"
    if rival.greed > 0.6 and choice >= 4 and families & SOCIAL_FAMILIES:
        model = "Free with loot boxes"
    elif rival.greed > 0.35 and online:
        model = "Free with cosmetics"
    else:
        model = "Premium"
    topics = sorted(GOOD_MATCHES.get(genre, ())) or ["Fantasy"]
    months = b.scope_months[choice] * rng.uniform(0.85, 1.3)
    project = RivalProject(
        title=idea_rules.title(rng), genre=genre, secondary=rng.choice(GENRES), topic=rng.choice(topics),
        scope=scope["name"], format=fmt, model=model, staff=staff,
        months_left=months * (rng.uniform(0.05, 0.95) if head_start else 1),
        fun=round(max(15, min(92, rng.gauss(48 + (rival.skill - 60) * 0.4 + rival.management * 8, 11))), 1),
        budget=scope["setup"] + staff * salary(game, rival.staff) / 12 * months, monthly_cost=scope["setup"] / months)
    rival.projects.append(project)
    return True


def finish_project(game, rival, project):
    rng, q = game.rng, game.b.quality
    index = scope_index(project.scope)
    work = SCOPES[index]["work"]
    craft = max(20, min(98, rival.skill + rng.gauss(0, 5)))
    bug_rate = max(0.012, 0.11 - rival.skill / 900) * (1.5 - rival.management) * 0.45
    bugs = work * bug_rate * rng.uniform(0.6, 1.4)
    quality = market.release_quality(game, project.fun, craft, bugs, work, 0)
    marketing = min(max(0.0, rival.cash) * 0.5, project.budget * game.b.rivals.marketing_share)
    rival.cash -= marketing
    model = BUSINESS_MODEL[project.model]
    price = 0.0 if model["free"] else SCOPES[index]["price"]
    stores = ["Steem", "Epoch Store"] if index < 3 else ["Steem", "Epoch Store", "Paystation Store", "YBox Store", "Nintendu eShop"]
    if index < 2:
        stores = ["Scratch.io", "Steem"]
    if "family" in GENRE_FAMILIES[project.genre] or "cozy" in GENRE_FAMILIES[project.genre]:
        stores = stores + ["Pear App Store", "Gooble Play"]
    look = ("Realistic 3D" if index >= 5 else "Stylized 3D" if index >= 3 else
            rng.choice(("Pixel art", "Hand-drawn 2D", "Minimal 2D")))
    plan = Plan(scope=project.scope, format=project.format, presentation=look, storefronts=stores,
                model=project.model, price=price)
    return market.launch(game, rival.id, rival.name, project.title, project.genre, project.secondary, project.topic,
                         plan, quality, rng.gauss(0.02, 0.06), bugs, marketing, {}, project.title)


def seed_catalog(game, rival):
    """Give every Rival a few games that came out before the Campaign started."""
    rng = game.rng
    reputation = rival.reputation
    for _ in range(rng.randint(1, 3)):
        before = len(rival.projects)
        start_project(game, rival, head_start=True)
        if len(rival.projects) == before:
            return
        project = rival.projects.pop()
        product = finish_project(game, rival, project)
        age = rng.randint(30, 900)
        product.released_day = -age
        fade = math.exp(-age / 400)
        for cohort in COHORTS:
            key = cohort["key"]
            aware = product.awareness.get(key, 0.0)
            product.owners[key] = cohort["population"] * aware * 0.25 * (1 - fade)
            product.awareness[key] = aware * (0.5 + 0.5 * fade) + product.owners[key] / cohort["population"]
        product.units = sum(product.owners.values())
    rival.reputation = reputation
    rival.cash = burn(game, rival) * rng.uniform(8, 30) if rival.staff > 10 else rival.cash


# --- Monthly business ---------------------------------------------------------------

def on_month(game):
    b, rng = game.b.rivals, game.rng
    for rival in active(game):
        monthly = burn(game, rival) + sum(p.monthly_cost for p in rival.projects)
        rival.cash -= monthly + rival.debt * 0.01
        pace = 0.6 + 0.5 * rival.management
        for project in list(rival.projects):
            project.months_left -= pace
            if project.months_left <= 0:
                rival.projects.remove(project)
                finish_project(game, rival, project)
        start_project(game, rival)
        manage(game, rival, monthly)
        rival.revenue_history.append(0.0)
        del rival.revenue_history[:-36]
    if rng.random() < b.founding_chance * game.s.market.confidence:
        found(game)
    if game.date.month == 1:
        acquisitions(game)


def manage(game, rival, monthly):
    b, rng = game.b.rivals, game.rng
    big = rival.staff >= 100
    if rival.cash < 0:
        rival.debt += -rival.cash
        rival.cash = 0.0
    if rival.debt > b.debt_limit_months * monthly + 50_000:
        close(game, rival, "went bankrupt")
        return
    if rival.cash > 6 * monthly and rival.debt:
        repay = min(rival.debt, rival.cash - 6 * monthly)
        rival.debt -= repay
        rival.cash -= repay
    history = rival.revenue_history
    recent, before = sum(history[-6:]), sum(history[-12:-6])
    profit = recent - 6 * monthly
    idle = rival.staff - sum(p.staff for p in rival.projects)
    if rival.cash > b.hire_months * monthly and profit > 0 and idle < max(2, rival.staff * 0.1):
        # Big organisations grow slower: hiring, onboarding and management all get harder.
        rival.staff += max(1, round(rival.staff * rng.uniform(0.03, 0.08) / (1 + rival.staff / 1500)))
    elif rival.staff > 1 and (rival.debt > 3 * monthly or (rival.cash < b.layoff_months * monthly and profit < 0)):
        deep = rival.debt > 3 * monthly
        cut = max(1, round(rival.staff * rng.uniform(0.12, 0.25) if deep else rival.staff * rng.uniform(0.04, 0.1)))
        rival.staff = max(1, rival.staff - cut)
        for project in rival.projects:
            project.staff = max(1, min(project.staff, rival.staff))
        if deep:
            for project in sorted(rival.projects, key=lambda p: -p.months_left)[:1]:
                rival.projects.remove(project)  # cancel the project furthest from release
        if big:
            game.news(f"{rival.name} lays off {cut} people.")
    # Management changes, and with it greed and craft.
    rival.management = max(0.1, min(0.98, rival.management + rng.gauss(0, b.management_drift)))
    if rng.random() < 0.01:
        rival.management = rng.uniform(0.3, 0.95)
        if big:
            game.news(f"{rival.name} has new leadership.")
    if before and recent < before * 0.7 and rival.management < 0.6 and len(history) >= 12:
        rival.greed = min(0.95, rival.greed + 0.05)
        if big and rival.greed > 0.5:
            game.news(f"{rival.name} is under pressure and leans harder on monetization.")
    elif rival.management > 0.75:
        rival.greed = max(0.0, rival.greed - 0.01)
    rival.skill += (45 + rival.management * 45 - rival.skill) * 0.02
    rival.reputation = max(0.0, rival.reputation - rival.greed * 0.25)


def close(game, rival, reason, buyer=None):
    rival.closed_day = game.s.day
    rival.projects.clear()
    if buyer:
        rival.owner = buyer.id
        for product in game.s.products:
            if product.studio_id == rival.id:
                product.studio_id = buyer.id
    if rival.staff >= 20 or buyer:
        game.news(f"{rival.name} {reason}.")


def acquisitions(game):
    rng = game.rng
    rivals = active(game)
    buyers = sorted(rivals, key=lambda r: r.cash, reverse=True)[:5]
    for buyer in buyers:
        targets = [r for r in rivals if r is not buyer and r.closed_day < 0 and r.reputation > 55
                   and r.cash < 3 * burn(game, r) and r.staff * 60_000 < buyer.cash / 3]
        if targets and rng.random() < 0.5:
            target = rng.choice(targets)
            price = target.staff * 60_000 + target.debt
            buyer.cash -= price
            buyer.staff += int(target.staff * 0.7)
            for key, value in target.fans.items():
                buyer.fans[key] = buyer.fans.get(key, 0.0) + value * 0.6
            close(game, target, f"was bought by {buyer.name} for ${price / 1e6:,.1f}M", buyer)
            rivals.remove(target)


# --- View ------------------------------------------------------------------------

def view(game):
    insight = game.has("analytics")
    names = {r.id: r.name for r in game.s.rivals}
    rows = []
    for r in sorted(game.s.rivals, key=lambda r: (r.closed_day >= 0, -sum(r.fans.values()))):
        products = sorted((p for p in game.s.products if p.studio_id == r.id), key=lambda p: -p.released_day)[:3]
        status = ("Independent" if r.closed_day < 0 else f"Owned by {names.get(r.owner, '?')}" if r.owner else "Closed")
        rows.append({"id": r.id, "name": r.name, "status": status, "staff": r.staff, "reputation": round(r.reputation),
                     "fans": round(sum(r.fans.values())), "in_development": len(r.projects),
                     "revenue_year": round(sum(r.revenue_history[-12:])) if insight else None,
                     "recent": [{"title": p.title, "genre": p.genre, "units": round(p.units),
                                 "rating": round(p.rating)} for p in products]})
    return {"rivals": rows[:60]}
