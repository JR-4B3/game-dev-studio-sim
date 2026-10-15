"""The simulation engine: a Campaign's state plus the systems that change it.

The engine knows about days, money, ids and commands. Everything else lives in
systems (core/systems/*.py). A system is a module that may define:

    on_month(game)  runs on the first day of every month, before on_day
    on_day(game)    runs every day
    on_week(game)   runs every Sunday, after on_day
    COMMANDS        {"action name": handler(game, data)}
    view(game)      returns a dict merged into the frontend view

Systems run in the order of SYSTEMS. Adding a feature such as offices means
writing one module and adding it to that list.
"""
from datetime import date, timedelta
import random

from . import codec
from .balance import DEFAULT
from .state import Ledger, State, Studio

SAVE_VERSION = 1


class Game:
    def __init__(self, state, balance=DEFAULT):
        self.s = state
        self.b = balance
        self.rng = random.Random()
        version, internal, gauss = state.rng
        self.rng.setstate((version, tuple(internal), gauss))

    # --- Lifecycle --------------------------------------------------------

    @classmethod
    def new(cls, seed, start, ironman=False, balance=DEFAULT):
        from .systems import SYSTEMS
        rng = random.Random(seed)
        state = State(
            version=SAVE_VERSION, seed=seed, rng=list(rng.getstate()), start=start.isoformat(), day=0,
            ironman=ironman, next_id=1, studio=Studio(name="Your studio", cash=balance.start.cash),
            rivals=[], products=[], market=None, ledgers=[], log=[],
        )
        game = cls(state, balance)
        state.ledgers.append(Ledger(month=game.month_key()))
        for system in SYSTEMS:
            if hasattr(system, "setup"):
                system.setup(game)
        game.log(f"You quit your job to make games. Savings: ${state.studio.cash:,.0f}. "
                 f"Living costs: ${balance.start.living_costs:,.0f} a month.")
        return game

    @classmethod
    def from_save(cls, data, balance=DEFAULT):
        if data.get("version") != SAVE_VERSION:
            raise ValueError(f"This save is version {data.get('version')}; this build reads version {SAVE_VERSION}.")
        return cls(codec.load(State, data), balance)

    def to_save(self):
        self.s.rng = list(self.rng.getstate())
        return codec.dump(self.s)

    # --- Time -------------------------------------------------------------

    @property
    def date(self):
        return date.fromisoformat(self.s.start) + timedelta(days=self.s.day)

    def month_key(self):
        return self.date.strftime("%Y-%m")

    def is_workday(self):
        return self.date.weekday() < 5

    def blocked(self):
        """Why time can't run right now, or an empty string."""
        studio = self.s.studio
        if studio.closed:
            return "Campaign over"
        if studio.project and studio.project.decision is not None:
            return "Decision required"
        return ""

    def advance_days(self, days):
        from .systems import SYSTEMS
        for _ in range(days):
            if self.blocked():
                return
            self.s.day += 1
            today = self.date
            if today.day == 1:
                for system in SYSTEMS:
                    if hasattr(system, "on_month"):
                        system.on_month(self)
            for system in SYSTEMS:
                if hasattr(system, "on_day"):
                    system.on_day(self)
            if today.weekday() == 6:
                for system in SYSTEMS:
                    if hasattr(system, "on_week"):
                        system.on_week(self)

    # --- Commands and views -----------------------------------------------

    def command(self, data):
        from .systems import COMMANDS
        action = data.get("action")
        if self.s.studio.closed:
            raise ValueError("This Campaign is over. Start a new one.")
        if action not in COMMANDS:
            raise ValueError(f"Unknown action: {action!r}")
        COMMANDS[action](self, data)

    def view(self):
        from .systems import SYSTEMS
        view = {"date": self.date.isoformat(), "day": self.s.day, "seed": self.s.seed,
                "ironman": self.s.ironman, "held": self.blocked(), "closed": self.s.studio.closed,
                "log": self.s.log[:40], "news": self.s.news[:40]}
        for system in SYSTEMS:
            if hasattr(system, "view"):
                view.update(system.view(self))
        return view

    # --- Shared helpers ---------------------------------------------------

    def new_id(self):
        self.s.next_id += 1
        return self.s.next_id

    def log(self, text):
        self.s.log.insert(0, f"{self.date:%d %b %Y}: {text}")
        del self.s.log[200:]

    def news(self, text):
        self.s.news.insert(0, f"{self.date:%d %b %Y}: {text}")
        del self.s.news[200:]

    def has(self, research_key):
        return research_key is None or research_key in self.s.studio.research_done

    @property
    def ledger(self):
        return self.s.ledgers[-1]

    def earn(self, category, amount):
        """Operating income."""
        amount = float(amount)
        self.s.studio.cash += amount
        self.s.studio.tax_base += amount
        self.s.studio.lifetime_revenue += amount
        self.ledger.income[category] = self.ledger.income.get(category, 0) + amount

    def spend(self, category, amount):
        """Operating expense."""
        amount = float(amount)
        self.s.studio.cash -= amount
        self.s.studio.tax_base -= amount
        self.ledger.expenses[category] = self.ledger.expenses.get(category, 0) + amount

    def finance(self, category, amount):
        """Cash that moves without being income or expense: loans, advances, repayments."""
        amount = float(amount)
        self.s.studio.cash += amount
        self.ledger.financing[category] = self.ledger.financing.get(category, 0) + amount


def int_arg(data, name, low=0, high=None):
    value = data.get(name)
    if type(value) is not int or value < low or (high is not None and value > high):
        raise ValueError(f"Invalid {name}.")
    return value


def str_arg(data, name, choices=None):
    value = data.get(name)
    if not isinstance(value, str) or (choices is not None and value not in choices):
        raise ValueError(f"Invalid {name}.")
    return value
