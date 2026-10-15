"""The shared Market. Every Product, the player's and every Rival's, sells to
the same audience cohorts under the same rules.

Each week, in every cohort, a share of people go shopping. A game can only be
bought by people who know about it (awareness), can reach it (platform and
storefront), and do not own it yet. Among those, games compete on taste,
quality, price, greed and freshness against the option of buying nothing.
Word of mouth and charts make successful games better known; forgetting
makes everything else fade.
"""
import math

from ..content import (BUSINESS_MODEL, COHORT, COHORTS, FORMAT, GENRE_FAMILIES, PRESENTATION, SCOPE, SCOPES,
                       STOREFRONT, SUPPORT)
from ..genres import GENRES
from ..state import Market, Product


def setup(game):
    rng = game.rng
    game.s.market = Market(heat={g: round(rng.uniform(0.75, 1.3), 3) for g in GENRES},
                           recent_releases={g: 0.0 for g in GENRES})


# --- Owners: the player's Studio is id 0, Rivals have their own ids -------------

def owner(game, studio_id):
    if studio_id == 0:
        return game.s.studio
    return next(r for r in game.s.rivals if r.id == studio_id)


def credit(game, studio_id, category, amount):
    if studio_id == 0:
        game.earn(category, amount)
    else:
        rival = owner(game, studio_id)
        rival.cash += amount
        if rival.revenue_history:
            rival.revenue_history[-1] += amount


def charge(game, studio_id, category, amount):
    if studio_id == 0:
        game.spend(category, amount)
    else:
        owner(game, studio_id).cash -= amount


# --- Taste and awareness ------------------------------------------------------

def taste(cohort, genre, format_name="Offline solo"):
    tastes = cohort["tastes"]
    value = max(tastes.get(f, 0) for f in GENRE_FAMILIES[genre])
    for family, bonus in FORMAT[format_name]["tastes"].items():
        value += bonus * tastes.get(family, 0)
    return value


def add_awareness(game, awareness, people, genre, format_name="Offline solo", only=None):
    """Make `people` more people aware, spread by population and taste."""
    cohorts = [c for c in COHORTS if only is None or c["key"] in only]
    weights = {c["key"]: c["population"] * taste(c, genre, format_name) ** 2 for c in cohorts}
    total = sum(weights.values()) or 1
    for c in cohorts:
        share = people * weights[c["key"]] / total
        current = awareness.get(c["key"], 0.0)
        # Each new contact may reach someone who already knew.
        awareness[c["key"]] = current + (1 - current) * share / c["population"]


def aware_people(awareness):
    return sum(COHORT[k]["population"] * v for k, v in awareness.items())


def platform_access(product, cohort):
    reach = {}
    for name in product.storefronts:
        store = STOREFRONT[name]
        reach[store["platform"]] = 1 - (1 - reach.get(store["platform"], 0)) * (1 - store["reach"])
    return sum(cohort["platforms"][p] * r for p, r in reach.items())


# --- Release ---------------------------------------------------------------------

def release_quality(game, fun, craft, bugs, work_total, bonus):
    q = game.b.quality
    penalty = min(q.max_bug_penalty, bugs / max(1, work_total / 1000) * q.bugs_per_point)
    value = fun * q.fun_weight + craft * q.craft_weight + bonus - penalty
    return round(max(5, min(99, value)), 1)


def bug_penalty(game, product):
    q = game.b.quality
    work = SCOPE[product.scope]["work"]
    return min(q.max_bug_penalty, product.bugs / max(1, work / 1000) * q.bugs_per_point)


def launch(game, studio_id, studio_name, title, genre, secondary, topic, plan, quality, appeal, bugs, marketing,
           awareness, franchise, deal=None):
    m, market, rng = game.b.market, game.s.market, game.rng
    maker = owner(game, studio_id)
    novelty = 1 / (1 + market.recent_releases.get(genre, 0) / 6)
    model = BUSINESS_MODEL[plan.model]
    product = Product(
        id=game.new_id(), title=title, studio_id=studio_id, studio_name=studio_name, genre=genre,
        secondary=secondary, topic=topic, scope=plan.scope, format=plan.format, presentation=plan.presentation,
        model=plan.model, storefronts=list(plan.storefronts), price=plan.price, quality=quality, review=0,
        rating=quality, released_day=game.s.day, appeal=round(appeal, 3), novelty=round(novelty, 3),
        greed=model["greed"], bugs=bugs, awareness=dict(awareness), franchise=franchise, deal=deal,
    )
    # Players expect more from studios with a big name.
    expected = 35 + maker.reputation * 0.5
    product.rating = quality - max(0, expected - quality) * game.b.quality.expectation_weight
    product.rating -= model["greed"] * 12 + bug_penalty(game, product) * 0.3
    product.rating = round(max(5, min(99, product.rating)), 1)
    product.sentiment = max(10, min(90, 45 + product.rating * 0.3 - model["greed"] * 20))
    # Who notices the launch.
    for name in plan.storefronts:
        store = STOREFRONT[name]
        for cohort in COHORTS:
            share = cohort["platforms"][store["platform"]] * store["reach"]
            gain = m.store_visibility * store["visibility"] * share * taste(cohort, genre, plan.format) * (0.5 + novelty)
            current = product.awareness.get(cohort["key"], 0.0)
            product.awareness[cohort["key"]] = current + (1 - current) * gain
    fans = getattr(maker, "fans", {})
    # Fans pay more attention to a studio's big releases than to its side projects.
    size = 0.3 + 0.7 * min(1.0, SCOPE[plan.scope]["content"] / 3)
    for cohort in COHORTS:
        attention = fans.get(cohort["key"], 0) * m.fan_attention * size * min(1.0, taste(cohort, genre, plan.format))
        current = product.awareness.get(cohort["key"], 0.0)
        product.awareness[cohort["key"]] = current + (1 - current) * attention / cohort["population"]
    if marketing:
        add_awareness(game, product.awareness, marketing * m.marketing_people_per_dollar, genre, plan.format)
    if deal:
        from ..content import PUBLISHER
        add_awareness(game, product.awareness, PUBLISHER[deal.publisher]["people"], genre, plan.format)
    # The press covers games that are visible enough to matter.
    visible = aware_people(product.awareness)
    coverage = 0.1 + maker.reputation / 120 + math.log10(1 + visible) / 8
    if rng.random() < coverage:
        hype_gap = max(0, math.log10(1 + visible) - 5) * 2
        product.review = round(max(5, min(99, quality + rng.gauss(0, 4) - hype_gap)), 0)
    market.recent_releases[genre] = market.recent_releases.get(genre, 0) + 1
    weight = 0.12 + SCOPES.index(SCOPE[plan.scope]) * 0.04
    score = product.review or product.rating
    maker.reputation = round(max(0, min(100, maker.reputation + (score - maker.reputation) * weight)), 2)
    game.s.products.append(product)
    if studio_id != 0 and SCOPES.index(SCOPE[plan.scope]) >= 5:
        game.news(f"{studio_name} released {title} ({genre}). Press score {product.review or '–'}.")
    return product


# --- Weekly sales ------------------------------------------------------------

def utility(game, product, cohort, age_years):
    m = game.b.market
    u = taste(cohort, product.genre, product.format) * m.taste_weight
    u += math.log(max(0.2, game.s.market.heat.get(product.genre, 1.0)))
    u += cohort["quality_sensitivity"] * m.quality_weight * (product.rating - 55) / 20
    u += product.appeal + PRESENTATION[product.presentation]["appeal"].get(cohort["key"], 0)
    model = BUSINESS_MODEL[product.model]
    if model["free"]:
        u += 0.5
    else:
        price = sale_price(game, product, age_years)
        u -= cohort["price_sensitivity"] * m.price_weight * math.log(1 + price / cohort["budget"])
        expected = SCOPE[product.scope]["price"]
        u -= 0.3 * max(0, price / expected - 1)
        u += m.content_weight * math.log(SCOPE[product.scope]["content"])
    u -= product.greed * (1 - cohort["monetization_tolerance"]) * m.greed_weight
    u += cohort["novelty"] * product.novelty * m.novelty_weight
    u += (product.sentiment - 50) / 100
    u -= age_years * m.age_decay
    return u


def sale_price(game, product, age_years):
    """Older games sell mostly in store sales, at a discount."""
    return product.price * max(game.b.market.lowest_discount, 1 - age_years * game.b.market.yearly_discount)


def interest(game, u):
    """Share of aware people who want the game, from its utility."""
    m = game.b.market
    return m.interest_cap / (1 + math.exp(-(u - m.interest_midpoint) * m.interest_slope))


def can_sell(product):
    """An online game whose servers are shut down can't be bought anymore."""
    return not (product.support == "Sunset" and FORMAT[product.format]["server_rent"])


def on_week(game):
    m, market = game.b.market, game.s.market
    products = [p for p in game.s.products if not p.retired]
    weekly = {p.id: 0.0 for p in products}
    by_cohort = {p.id: {} for p in products}
    for cohort in COHORTS:
        key = cohort["key"]
        budget = cohort["population"] * cohort["shopping"] * market.confidence
        wants = []
        for p in products:
            if not can_sell(p):
                continue
            reachable = p.awareness.get(key, 0.0) * platform_access(p, cohort)
            if reachable <= 0:
                continue
            age = (game.s.day - p.released_day) / 365
            # Buyers: people who know the game, can get it, like it enough and don't own it yet.
            pool = cohort["population"] * reachable * interest(game, utility(game, p, cohort, age))
            remaining = pool - p.owners.get(key, 0.0)
            if remaining > 0:
                wants.append((p, remaining * m.weekly_conversion))
        total = sum(w for _, w in wants)
        # A crowded week splits a limited number of purchases.
        scale = min(1.0, budget / total) if total else 1.0
        for p, w in wants:
            units = w * scale
            p.owners[key] = p.owners.get(key, 0.0) + units
            weekly[p.id] += units
            by_cohort[p.id][key] = units
    ranked = sorted(products, key=lambda p: weekly[p.id], reverse=True)
    leader = weekly[ranked[0].id] if ranked else 0
    for rank, p in enumerate(ranked):
        # Only real sellers chart: a game needs a meaningful share of the leader's sales.
        charted = rank < 20 and weekly[p.id] >= leader * 0.05
        settle_week(game, p, weekly[p.id], by_cohort[p.id], rank if charted else None)
    update_trends(game)


def settle_week(game, p, units, by_cohort, rank):
    m = game.b.market
    model = BUSINESS_MODEL[p.model]
    p.weekly_units = units
    p.units += units
    p.sales_history.append(round(units))
    del p.sales_history[:-104]
    cut = sum(STOREFRONT[s]["cut"] for s in p.storefronts) / len(p.storefronts)
    gross = 0.0
    if not model["free"] and units:
        refund = min(0.4, m.refund_base + bug_penalty(game, p) / 100 + max(0, 50 - p.rating) / 300)
        gross += units * sale_price(game, p, (game.s.day - p.released_day) / 365) * (1 - refund)
    # Players and recurring revenue.
    quality_retention = m.retention + (p.rating - 50) / 400 - p.greed * 0.05
    weekly_retention = max(0.3, min(0.99, quality_retention)) ** (1 / 4.33)
    p.players = p.players * weekly_retention + units
    if model["payers"] and p.support != "Sunset":
        gross += p.players * model["payers"] * model["arppu"] / 4.33
    if gross:
        net = gross * (1 - cut)
        if p.deal:
            net -= publisher_take(p, net)
        p.revenue += net
        credit(game, p.studio_id, "Game sales" if not model["payers"] else "Game revenue", net)
    # Servers for online games.
    fmt = FORMAT[p.format]
    hosting = SUPPORT[p.support]["hosting"]
    if fmt["server_rent"] and hosting:
        cost = (fmt["server_rent"] * (1 + min(4, p.players / 50_000)) + p.players * fmt["hosting"]) * hosting
        p.costs += cost
        charge(game, p.studio_id, "Servers", cost)
    if p.support == "Sunset" and fmt["server_rent"]:
        p.players *= 0.5
    # Awareness: word of mouth, charts, forgetting.
    talk = units * m.word_of_mouth * max(0.0, min(1.2, (p.rating - 45) / 45))
    if talk:
        add_awareness(game, p.awareness, talk, p.genre, p.format)
    if rank is not None:
        boost = m.chart_awareness / (1 + rank) ** 0.8
        for cohort in COHORTS:
            gain = boost * taste(cohort, p.genre, p.format) * platform_access(p, cohort)
            current = p.awareness.get(cohort["key"], 0.0)
            p.awareness[cohort["key"]] = current + (1 - current) * gain
    browsing = m.store_browsing * max(0.0, p.rating - 30) / 70 if can_sell(p) else 0.0
    for cohort in COHORTS:
        key = cohort["key"]
        owned = p.owners.get(key, 0.0) / cohort["population"]
        aware = p.awareness.get(key, 0.0)
        # People keep stumbling on a listed game while browsing stores, a little each week.
        aware += (1 - aware) * browsing * platform_access(p, cohort) * taste(cohort, p.genre, p.format)
        p.awareness[key] = owned + max(0.0, aware - owned) * (1 - m.forgetting)
    # Opinion.
    target = p.quality - bug_penalty(game, p) - p.greed * 18 + (p.sentiment - 60) * 0.15
    p.rating = round(p.rating + (max(5, min(99, target)) - p.rating) * 0.08, 2)
    sentiment_target = 40 + p.rating * 0.4 - p.greed * 25 - bug_penalty(game, p)
    p.sentiment += (sentiment_target - p.sentiment) * 0.08 + SUPPORT[p.support]["sentiment"]
    p.sentiment = max(0, min(100, p.sentiment))
    # Buyers who loved it follow the studio.
    maker = owner(game, p.studio_id)
    for key, n in by_cohort.items():
        maker.fans[key] = maker.fans.get(key, 0.0) + n * m.fan_conversion * (p.rating / 100) ** 2
    age_weeks = (game.s.day - p.released_day) / 7
    if age_weeks > 52 and units < 2 and p.players < 20:
        p.retired = True


def publisher_take(product, net):
    deal = product.deal
    owed = max(0.0, deal.advance - deal.recouped)
    take_recoup = min(owed, net * deal.recoup_share)
    deal.recouped += take_recoup
    rest = net - take_recoup / deal.recoup_share if deal.recoup_share else net
    return take_recoup + max(0.0, rest) * deal.share


def update_trends(game):
    m, market, rng = game.b.market, game.s.market, game.rng
    for genre in GENRES:
        heat = market.heat.get(genre, 1.0)
        recent = market.recent_releases.get(genre, 0.0)
        heat += m.heat_drift * (1.0 - heat) + rng.gauss(0, 0.025) - m.heat_saturation * max(0, recent - 3) / 10
        market.heat[genre] = round(max(0.4, min(1.9, heat)), 3)
        market.recent_releases[genre] = recent * 0.97
    for p in game.s.products:
        if p.weekly_units > 100_000 and not p.retired:
            market.heat[p.genre] = min(1.9, market.heat[p.genre] + 0.01)
    market.confidence += (1.0 - market.confidence) * 0.05 + rng.gauss(0, 0.01)
    if rng.random() < 0.002:
        market.confidence *= 0.85
        game.news("A recession hits. People are spending less on games.")
    market.confidence = max(0.6, min(1.3, market.confidence))


def on_month(game):
    decay = game.b.market.fan_decay
    for maker in [game.s.studio] + game.s.rivals:
        for key in maker.fans:
            maker.fans[key] *= 1 - decay


# --- View ------------------------------------------------------------------------

def product_view(game, p):
    return {"id": p.id, "title": p.title, "studio": p.studio_name, "mine": p.studio_id == 0, "genre": p.genre,
            "scope": p.scope, "format": p.format, "model": p.model, "storefronts": p.storefronts,
            "price": p.price, "quality": round(p.quality) if p.studio_id == 0 else None,
            "review": p.review, "rating": round(p.rating), "sentiment": round(p.sentiment),
            "weekly_units": round(p.weekly_units), "units": round(p.units), "players": round(p.players),
            "revenue": round(p.revenue), "costs": round(p.costs), "profit": round(p.revenue - p.costs),
            "bugs": round(p.bugs), "support": p.support, "version": p.version,
            "aware": round(aware_people(p.awareness)), "history": p.sales_history[-26:],
            "weeks": (game.s.day - p.released_day) // 7, "deal": p.deal.publisher if p.deal else "",
            "retired": p.retired, "franchise": p.franchise}


def view(game):
    market = game.s.market
    products = [p for p in game.s.products if not p.retired]
    chart = sorted(products, key=lambda p: p.weekly_units, reverse=True)[:30]
    detailed = game.has("market_research")
    heat = sorted(market.heat.items(), key=lambda kv: kv[1], reverse=True)
    return {
        "chart": [{"id": p.id, "title": p.title, "studio": p.studio_name, "mine": p.studio_id == 0,
                   "genre": p.genre, "weekly_units": round(p.weekly_units), "rating": round(p.rating)} for p in chart],
        "catalog": [product_view(game, p) for p in game.s.products if p.studio_id == 0],
        "trends": [{"genre": g, "heat": round(h, 2) if detailed else None,
                    "label": "Hot" if h > 1.3 else "Rising" if h > 1.08 else "Cooling" if h < 0.8 else "Steady"}
                   for g, h in heat],
        "confidence": round(market.confidence, 2),
        "cohorts": [{"key": c["key"], "name": c["name"], "population": c["population"]} for c in COHORTS],
        "fans": round(sum(game.s.studio.fans.values())),
        "fans_by_cohort": {k: round(v) for k, v in game.s.studio.fans.items()} if game.has("analytics") else {},
    }
