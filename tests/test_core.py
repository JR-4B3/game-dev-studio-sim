"""Core rules that must hold whatever the balance numbers are.

    python3 -m unittest discover tests
"""
from datetime import date
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from core import Game  # noqa: E402
from core.balance import DEFAULT  # noqa: E402
from balance import STRATEGIES  # noqa: E402

START = date(2026, 3, 2)


def played(seed, days, strategy="smart"):
    game = Game.new(seed, START)
    for _ in range(days):
        STRATEGIES[strategy](game)
        if game.s.studio.closed:
            break
        game.advance_days(1)
    return game


class Determinism(unittest.TestCase):
    def test_same_seed_and_commands_give_the_same_campaign(self):
        a, b = played(5, 400), played(5, 400)
        self.assertEqual(json.dumps(a.to_save()), json.dumps(b.to_save()))

    def test_different_seeds_give_different_markets(self):
        a, b = Game.new(1, START), Game.new(2, START)
        self.assertNotEqual([r.name for r in a.s.rivals], [r.name for r in b.s.rivals])

    def test_a_save_continues_exactly_like_the_original(self):
        game = played(9, 300)
        copy = Game.from_save(json.loads(json.dumps(game.to_save())))
        for g in (game, copy):
            for _ in range(200):
                STRATEGIES["smart"](g)
                g.advance_days(1)
        self.assertEqual(json.dumps(game.to_save()), json.dumps(copy.to_save()))


class Money(unittest.TestCase):
    def test_the_books_explain_every_dollar(self):
        game = played(3, 900)  # longer than the 24 months of books that are kept
        s = game.s.studio
        flows = sum(sum(l.income.values()) - sum(l.expenses.values()) + sum(l.financing.values())
                    for l in game.s.ledgers)
        self.assertAlmostEqual(game.s.ledgers[0].opening + flows, s.cash, places=2)
        for month, following in zip(game.s.ledgers, game.s.ledgers[1:]):
            net = sum(month.income.values()) - sum(month.expenses.values()) + sum(month.financing.values())
            self.assertAlmostEqual(month.opening + net, following.opening, places=2)

    def test_idle_founder_goes_bankrupt_and_time_stops(self):
        game = Game.new(4, START)
        game.advance_days(800)
        self.assertEqual(game.s.studio.closed, "Bankrupt")
        day = game.s.day
        game.advance_days(30)
        self.assertEqual(game.s.day, day)
        with self.assertRaises(ValueError):
            game.command({"action": "research", "key": "tools"})


class Commands(unittest.TestCase):
    def test_bad_commands_are_refused_without_changing_state(self):
        game = Game.new(6, START)
        before = json.dumps(game.to_save())
        for data in ({"action": "nope"}, {"action": "hire", "id": -1}, {"action": "explore", "id": "x"},
                     {"action": "experiment", "key": "paper"}, {"action": "plan", "field": "scope", "value": "Huge"},
                     {"action": "loan", "name": "Growth loan"}, {"action": "price", "id": 1, "price": 3}):
            with self.assertRaises(ValueError, msg=data):
                game.command(data)
        self.assertEqual(before, json.dumps(game.to_save()))

    def test_concept_to_release(self):
        game = Game.new(8, START)
        s = game.s.studio
        game.command({"action": "explore", "id": s.ideas[0].id})
        game.command({"action": "experiment", "key": "paper"})
        while s.project.activity:
            game.advance_days(1)
        self.assertGreater(len(s.project.findings), 1)
        game.command({"action": "to_design"})
        game.command({"action": "plan", "field": "scope", "value": "Bite-size"})
        game.command({"action": "commit"})
        for _ in range(400):
            if s.project.decision is not None:
                game.command({"action": "decide", "index": 0})
            if s.project.stage == "polish":
                break
            game.advance_days(1)
        self.assertEqual(s.project.stage, "polish")
        game.command({"action": "release"})
        self.assertIsNone(s.project)
        mine = [p for p in game.s.products if p.studio_id == 0]
        self.assertEqual(len(mine), 1)
        game.advance_days(30)
        self.assertGreater(mine[0].units, 0)

    def test_estimates_always_contain_the_truth(self):
        game = played(10, 500)
        ideas = list(game.s.studio.ideas) + ([game.s.studio.project.idea] if game.s.studio.project else [])
        for idea in ideas:
            self.assertLessEqual(idea.fun_known.low, idea.fun + 1e-9)
            self.assertGreaterEqual(idea.fun_known.high, idea.fun - 1e-9)
            self.assertLessEqual(idea.complexity_known.low, idea.complexity + 1e-9)
            self.assertGreaterEqual(idea.complexity_known.high, idea.complexity - 1e-9)


class Market(unittest.TestCase):
    def test_rivals_and_player_sell_through_the_same_market(self):
        game = played(2, 500)
        rivals = {p.studio_id for p in game.s.products if p.studio_id}
        self.assertGreater(len(rivals), 10)
        self.assertTrue(any(p.studio_id == 0 for p in game.s.products))
        for p in game.s.products:
            self.assertGreaterEqual(p.units, 0)
            for key, owners in p.owners.items():
                self.assertLessEqual(owners, next(c["population"] for c in __import__("core.content", fromlist=["COHORTS"]).COHORTS if c["key"] == key))

    def test_every_strategy_runs_two_years(self):
        for name in STRATEGIES:
            game = played(13, 730, name)
            self.assertTrue(game.view()["date"])

    def test_balance_overrides(self):
        tweaked = DEFAULT.with_overrides({"market": {"word_of_mouth": 1.0}})
        self.assertEqual(tweaked.market.word_of_mouth, 1.0)
        with self.assertRaises(ValueError):
            DEFAULT.with_overrides({"market": {"nonsense": 1}})


if __name__ == "__main__":
    unittest.main()
