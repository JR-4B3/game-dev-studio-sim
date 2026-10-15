"""Research: one-off investments that unlock options or change the rules.
Some carry a monthly running cost once done."""
from ..content import RESEARCH, RESEARCH_NODE
from ..game import str_arg


def on_month(game):
    running = sum(RESEARCH_NODE[k].get("monthly", 0) for k in game.s.studio.research_done)
    if running:
        game.spend("Research running costs", running)


def wants_work(game):
    return bool(game.s.studio.research_active)


def work(game, output, average_skill):
    s = game.s.studio
    s.research_work += output * (1.25 if game.has("research_lab") else 1)
    node = RESEARCH_NODE[s.research_active]
    if s.research_work >= node["work"]:
        s.research_done.append(node["key"])
        s.research_active, s.research_work = "", 0.0
        game.log(f"Research complete: {node['name']}. {node['effect']}.")
        if s.research_queue:
            s.research_active = s.research_queue.pop(0)


def queue(game, data):
    s = game.s.studio
    key = str_arg(data, "key", RESEARCH_NODE)
    node = RESEARCH_NODE[key]
    if key in s.research_done or key == s.research_active or key in s.research_queue:
        raise ValueError(f"{node['name']} is already done or planned.")
    planned = set(s.research_done) | set(s.research_queue) | {s.research_active}
    missing = [RESEARCH_NODE[p]["name"] for p in node["prereq"] if p not in planned]
    if missing:
        raise ValueError(f"{node['name']} needs {', '.join(missing)} first.")
    if s.cash < node["cost"]:
        raise ValueError(f"{node['name']} costs ${node['cost']:,.0f}.")
    if node["cost"]:
        game.spend("Research", node["cost"])
    if s.research_active:
        s.research_queue.append(key)
    else:
        s.research_active = key
    game.log(f"Research planned: {node['name']} (${node['cost']:,.0f}).")


def cancel(game, data):
    s = game.s.studio
    key = str_arg(data, "key", RESEARCH_NODE)
    if key in s.research_queue:
        s.research_queue.remove(key)
    elif key == s.research_active:
        s.research_active, s.research_work = (s.research_queue.pop(0) if s.research_queue else ""), 0.0
    else:
        raise ValueError("That research is not planned.")
    game.log(f"Dropped research: {RESEARCH_NODE[key]['name']}. The money is spent.")


COMMANDS = {"research": queue, "cancel_research": cancel}


def view(game):
    s = game.s.studio
    rows = []
    for node in RESEARCH:
        key = node["key"]
        status = ("done" if key in s.research_done else "active" if key == s.research_active
                  else "queued" if key in s.research_queue else "open")
        rows.append({**{k: v for k, v in node.items()}, "prereq": [RESEARCH_NODE[p]["name"] for p in node["prereq"]],
                     "status": status})
    active = RESEARCH_NODE.get(s.research_active)
    return {"research": rows, "research_progress": s.research_work / active["work"] if active else 0}
