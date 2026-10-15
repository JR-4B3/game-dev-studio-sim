"""Plays scripted strategies across many seeds and reports how the economy treats them.

    python3 tools/balance.py                  # every strategy, 30 seeds, 5 years
    python3 tools/balance.py --years 3 --seeds 50 --strategy mixed
    python3 tools/balance.py --overrides tweaks.json
    python3 tools/balance.py --market 20      # watch the Rivals for 20 years

Compare a run before and after a change to see what the change moved.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import Game  # noqa: E402
from core.balance import DEFAULT  # noqa: E402

START = date(2026, 1, 5)


def try_command(game, **data):
    try:
        game.command(data)
        return True
    except ValueError:
        return False


def best_idea(game):
    ideas = game.s.studio.ideas
    return max(ideas, key=lambda i: (i.fun_known.low + i.fun_known.high) / 2) if ideas else None


def run_project(game, scope, experiments=("paper",), iterate=0, stores=("Steem",), marketing="Word of mouth"):
    """Drive the current game one step. Returns nothing; call it every day."""
    s = game.s.studio
    project = s.project
    if project is None:
        idea = best_idea(game)
        if idea:
            try_command(game, action="explore", id=idea.id)
        return
    if project.decision is not None:
        try_command(game, action="decide", index=game.rng.randrange(2))
        return
    if project.stage == "concept":
        if project.activity:
            return
        done = len(project.findings) - 1
        if done < len(experiments):
            try_command(game, action="experiment", key=experiments[done])
        elif project.iterations < iterate:
            try_command(game, action="iterate")
        else:
            try_command(game, action="to_design")
        return
    if project.stage == "design":
        try_command(game, action="plan", field="scope", value=scope)
        for store in stores:
            if store not in project.plan.storefronts:
                try_command(game, action="plan", field="storefront", value=store)
        try_command(game, action="plan", field="marketing", value=marketing)
        if not try_command(game, action="commit"):
            try_command(game, action="plan", field="scope", value="Bite-size")
            try_command(game, action="commit")
        return
    if project.stage == "polish" and project.bugs_known < 1 and project.polish_done > project.work_total * 0.05:
        try_command(game, action="release")


def take_contracts(game, limit=1):
    s = game.s.studio
    if len(s.contracts) < limit and s.contract_offers:
        from core.systems.contracts import estimate
        def fits(c):
            weeks, quality = estimate(game, c)
            return weeks is not None and weeks * 7 < c.days * 0.8 and quality >= c.quality_target
        offer = max((c for c in s.contract_offers if c.trust_needed <= s.client_trust + 10 and fits(c)),
                    key=lambda c: c.pay / c.work, default=None)
        if offer:
            try_command(game, action="accept_contract", id=offer.id)


def hire_when_rich(game, months=12, limit=4):
    s = game.s.studio
    if len(s.team) >= limit or not s.applicants:
        return
    from core.systems.finance import monthly_costs
    burn = sum(monthly_costs(game).values())
    best = max(s.applicants, key=lambda p: p.design + p.art + p.code - p.salary / 2000)
    if s.cash > (burn + best.salary / 12 * 1.13) * months:
        try_command(game, action="hire", id=best.id)


def smart(game):
    """What a thoughtful player does: tests ideas, drops weak ones, iterates, promotes."""
    s = game.s.studio
    take_contracts(game, 1)
    if "promotion_basics" not in s.research_done and not s.research_active and s.cash > 4_000:
        try_command(game, action="research", key="promotion_basics")
    project = s.project
    if project and project.stage == "concept" and not project.activity:
        known = project.idea.fun_known
        tested = len(project.findings) > 2
        if tested and known.high < 50:
            try_command(game, action="shelve")
            for idea in list(s.ideas):
                if idea.id == project.idea.id:
                    s.ideas.remove(idea)  # don't pick it again
            return
        if project.discoveries and game.rng.random() < 0.5 and "excited" in project.discoveries[0].text:
            try_command(game, action="pivot", index=0)
            return
    if project and project.stage in ("production", "polish"):
        if game.s.day % 30 == 0:
            try_command(game, action="promote", key="social", target=0)
        if project.stage == "polish" and "festival" not in [c.key for c in s.commitments] and not getattr(project, "_fest", False):
            if try_command(game, action="promote", key="festival", target=0):
                project._fest = True
    run_project(game, "Micro", experiments=("paper", "playable", "pitch"), iterate=3, stores=("Steem", "Scratch.io"),
                marketing="Social posts")


STRATEGIES = {
    "smart": smart,
    "idle": lambda g: None,
    "contracts": lambda g: take_contracts(g, 2),
    "games": lambda g: run_project(g, "Micro"),
    "mixed": lambda g: (take_contracts(g, 1), run_project(g, "Micro", experiments=("paper", "playable"), iterate=1)),
    "careful": lambda g: (take_contracts(g, 1), run_project(g, "Micro", experiments=("paper", "playable", "pitch"), iterate=2,
                                                             stores=("Steem", "Scratch.io"), marketing="Social posts")),
    "growth": lambda g: (take_contracts(g, 1), hire_when_rich(g),
                         run_project(g, "Compact" if g.s.studio.reputation > 30 else "Micro",
                                     experiments=("paper", "playable"), iterate=2, marketing="Small ad budget"
                                     if g.s.studio.cash > 30_000 else "Social posts")),
    "all-in": lambda g: run_project(g, "Compact", experiments=("playable",)),
}


def play(seed, strategy, years, balance):
    game = Game.new(seed, START, balance=balance)
    act = STRATEGIES[strategy]
    snapshots = {}
    for day in range(int(years * 365)):
        act(game)
        if game.s.studio.closed:
            break
        game.advance_days(1)
        if game.s.day % 365 == 0:
            snapshots[game.s.day // 365] = game.s.studio.cash
    s = game.s.studio
    mine = [p for p in game.s.products if p.studio_id == 0]
    return {"survived": not s.closed, "days": game.s.day, "cash": s.cash, "snapshots": snapshots,
            "releases": len(mine), "units": [p.units for p in mine], "ratings": [p.rating for p in mine],
            "revenue": s.lifetime_revenue, "game_revenue": sum(p.revenue for p in mine),
            "team": len(s.team), "reputation": s.reputation, "trust": s.client_trust,
            "fans": sum(s.fans.values())}


def pct(values, q):
    values = sorted(values)
    return values[min(len(values) - 1, int(q * len(values)))] if values else 0


def report(strategy, results, years):
    survived = [r for r in results if r["survived"]]
    first = [r["units"][0] for r in results if r["units"]]
    all_units = [u for r in results for u in r["units"]]
    print(f"\n== {strategy} ({len(results)} seeds, {years} years)")
    print(f"  survival {len(survived) / len(results):.0%}   median months lived {statistics.median(r['days'] for r in results) / 30.4:.0f}")
    for year in range(1, years + 1):
        cash = [r["snapshots"][year] for r in results if year in r["snapshots"]]
        if cash:
            print(f"  cash after year {year}: p25 ${pct(cash, .25):,.0f}  median ${pct(cash, .5):,.0f}  p75 ${pct(cash, .75):,.0f}  ({len(cash)} alive)")
    print(f"  releases per run: {statistics.mean(r['releases'] for r in results):.1f}   "
          f"first game units: p25 {pct(first, .25):,.0f}  median {pct(first, .5):,.0f}  p90 {pct(first, .9):,.0f}")
    if all_units:
        print(f"  all games units: median {pct(all_units, .5):,.0f}  p90 {pct(all_units, .9):,.0f}  best {max(all_units):,.0f}")
        ratings = [x for r in results for x in r["ratings"]]
        print(f"  ratings: median {pct(ratings, .5):.0f}  range {min(ratings):.0f}-{max(ratings):.0f}")
    print(f"  revenue: median ${pct([r['revenue'] for r in results], .5):,.0f}   from games ${pct([r['game_revenue'] for r in results], .5):,.0f}"
          f"   team {statistics.mean(r['team'] for r in results):.1f}   reputation {statistics.mean(r['reputation'] for r in results):.0f}"
          f"   fans {pct([r['fans'] for r in results], .5):,.0f}")


def watch_market(seed, years, balance):
    game = Game.new(seed, START, balance=balance)
    game.s.studio.cash = 1e15  # keep the idle player from going bankrupt and stopping time
    giants = sorted(game.s.rivals, key=lambda r: -r.staff)[:6]
    print(f"Market over {years} years, seed {seed}")
    for year in range(1, years + 1):
        game.advance_days(365)
        alive = [r for r in game.s.rivals if r.closed_day < 0]
        top = sorted((p for p in game.s.products if not p.retired), key=lambda p: -p.weekly_units)[:3]
        print(f"  year {year:2}: {len(alive)} studios open, {len(game.s.products)} games, "
              f"top: {', '.join(f'{p.title} ({p.studio_name}, {p.weekly_units:,.0f}/wk)' for p in top)}")
        print("           giants: " + ", ".join(
            f"{g.name} {g.staff} staff ${g.cash / 1e6:,.0f}M{' CLOSED' if g.closed_day >= 0 else ''} greed {g.greed:.2f}" for g in giants))
    for line in reversed(game.s.news[:40]):
        print("   ", line)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strategy", choices=sorted(STRATEGIES), action="append")
    parser.add_argument("--seeds", type=int, default=30)
    parser.add_argument("--years", type=int, default=5)
    parser.add_argument("--overrides", type=Path)
    parser.add_argument("--market", type=int, metavar="YEARS", help="watch the Rival market instead")
    args = parser.parse_args()
    balance = DEFAULT.with_overrides(json.loads(args.overrides.read_text())) if args.overrides else DEFAULT
    if args.market:
        watch_market(1, args.market, balance)
        return
    for strategy in args.strategy or STRATEGIES:
        report(strategy, [play(seed, strategy, args.years, balance) for seed in range(1, args.seeds + 1)], args.years)


if __name__ == "__main__":
    main()
