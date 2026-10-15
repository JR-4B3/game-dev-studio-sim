"""The systems that make up the game, in the order they run each day.

Finance runs first so a new month's books are open before anything is billed.
Market runs after the studio's own systems so a week's sales see that week's
work. Rivals run last.
"""
from . import contracts, finance, ideas, liveops, market, people, projects, research, rivals, work

SYSTEMS = (finance, people, research, ideas, market, contracts, work, projects, liveops, rivals)

COMMANDS = {}
for _system in SYSTEMS:
    for _name, _handler in getattr(_system, "COMMANDS", {}).items():
        if _name in COMMANDS:
            raise RuntimeError(f"Two systems define the command {_name!r}")
        COMMANDS[_name] = _handler
