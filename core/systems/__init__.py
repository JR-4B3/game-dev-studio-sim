"""The systems that make up the game, in the order they run each day.

The engine opens each month's books before any system runs. Market runs after
the studio's own systems so a week's sales see that week's work. Finance runs
last so bankruptcy is judged after the week's sales are in.
"""
from . import contracts, finance, ideas, liveops, market, people, projects, research, rivals, work

SYSTEMS = (people, research, ideas, market, contracts, work, projects, liveops, rivals, finance)

COMMANDS = {}
for _system in SYSTEMS:
    for _name, _handler in getattr(_system, "COMMANDS", {}).items():
        if _name in COMMANDS:
            raise RuntimeError(f"Two systems define the command {_name!r}")
        COMMANDS[_name] = _handler
