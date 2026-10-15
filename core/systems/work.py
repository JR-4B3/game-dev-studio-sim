"""Splits the team's working day between everything that needs people.

Fixed needs come first: supporting released games and running promotion or
community commitments. Flexible work shares the rest: client contracts take
the share the player set, research takes a fifth, updates a quarter, and the
game in development gets what remains (at least its reserve). With no game in
development, flexible work expands to fill the day.
"""
from . import contracts, liveops, people, projects, research


def allocation(game):
    s, w = game.s.studio, game.b.work
    fixed = {"support": liveops.support_need(game), "commitments": liveops.commitment_need(game)}
    flexible = {}
    if contracts.wants_work(game):
        flexible["contract"] = s.contract_share
    if research.wants_work(game):
        flexible["research"] = 0.2
    if liveops.wants_update_work(game):
        flexible["update"] = 0.25
    fixed_total = min(0.6, sum(fixed.values()))
    if fixed_total < sum(fixed.values()):
        fixed = {k: v * fixed_total / sum(fixed.values()) for k, v in fixed.items()}
    room = 1 - fixed_total
    shares = dict(fixed)
    if projects.wants_work(game):
        flexible_total = sum(flexible.values())
        limit = room * (1 - w.project_reserve)
        scale = min(1.0, limit / flexible_total) if flexible_total else 1.0
        for key, value in flexible.items():
            shares[key] = value * scale
        shares["project"] = room - sum(v for k, v in shares.items() if k in flexible)
    else:
        flexible_total = sum(flexible.values())
        for key, value in flexible.items():
            shares[key] = room * value / flexible_total
    return {k: v for k, v in shares.items() if v > 0.0001}


def on_day(game):
    if not game.is_workday():
        return
    shares = allocation(game)
    workload = sum(shares.values())
    busiest, best = "", 0.0
    jobs = (
        ("project", lambda: projects.skill_weights(game.s.studio.project), projects.work),
        ("contract", lambda: contracts.skill_weights(game), contracts.work),
        ("research", lambda: "research", research.work),
        ("update", lambda: (30, 15, 10, 45), liveops.update_work),
    )
    for key, weights_of, handler in jobs:
        share = shares.get(key, 0.0)
        if not share:
            continue
        weights = weights_of()
        output, average_skill = people.team_output(game, weights)
        if output:
            handler(game, output * share, average_skill)
        if share > best:
            best = share
            busiest = "research" if weights == "research" else ("design", "art", "audio", "code")[max(range(4), key=lambda i: weights[i])]
    people.add_experience(game, busiest, workload)
    people.tire(game, workload)


def view(game):
    return {"allocation": {k: round(v, 3) for k, v in allocation(game).items()}}
