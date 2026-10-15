# Game Dev Studio Sim

Working title. A studio-management game about running a game-development company,
aiming to be the most realistic depiction of what it's like to become an indie
developer.

This repo is a clean rebuild of
[Indie-Game-Dev-Simulator](https://github.com/JR-4B3/Indie-Game-Dev-Simulator).
The old game grew over months of sessions with different models and competing
ideas. This one is built once, from the ground up, with the vision settled first.
The old repo stays as the reference for how each system behaved.

## Play

Python 3.10 or newer, no packages to install.

```
python3 server.py
```

The game opens in your browser at http://127.0.0.1:8765. Saves go to
`saves/studio.json`. Time only runs while the tab is open and visible.

| Key | Does |
|---|---|
| H G T B S | Studio, Projects, People, Business, Market |
| Space | Pause or resume |
| < > or ← → | Slower or faster |
| Ctrl+S | Save |
| Esc | Menu, or close a dialog |

You start as a Founder with $15,000 in savings and $2,000 a month in living costs.
Client contracts pay the rent. Your own games are where the upside is, but only if
you find out honestly whether an Idea is fun before you spend months building it.

## What changes from the old game

Everything the player could see and do in the old game comes back. These parts
change:

1. **One shared market.** The player's studio and every Rival sell to the same
   audiences under the same rules. Rivals hire, borrow, lay off, get bought and go
   bankrupt from their own decisions. Any studio can fall, including the biggest.
2. **The core doesn't know how it's drawn.** `core/` takes commands and returns
   plain data, with no files, network or clock. `server.py` and `web/` are one
   frontend. A Godot, 2D, isometric or 3D frontend can drive the same core.
3. **Extensions don't break the economy.** A new system (offices, rooms,
   buildings) is one module in `core/systems/` that hooks into days, weeks and
   months. Its numbers go in `core/balance.py`, and `tools/balance.py` shows what
   it changed.
4. **Simpler code, the same or richer market dynamics.**
5. **Deeper product development.** An Idea hides how fun it is, how hard it is to
   build and who it appeals to. Experiments narrow honest ranges around the truth.
   Iterations make the core more fun. Discoveries let you pivot. Then you plan,
   commit, build through milestone decisions, polish and release.

## In this first playable version

- Ideas from the team, six kinds of experiments, iteration, pivots, shelving.
- Planning: scope, format, look, storefronts, business model, price, launch
  marketing, announcement; publisher pitches with advances and recoup.
- Production with bugs and milestone decisions, then open-ended polish.
- A market of eight audience cohorts, eight storefronts and around 40 Rival
  studios, with charts, word of mouth, genre heat, store sales over time and a
  recession now and then.
- Released games: price, support level, updates up to paid DLC, promotion and
  community actions, servers for online games.
- Contracts with deadlines, quality checks and client trust.
- Hiring, salaries, fatigue, morale, vacations, training, burnout, resignations.
- 29 research nodes, each with an effect the rules apply.
- Loans, monthly books, quarterly taxes, bankruptcy after eight weeks of
  negative cash; normal and Ironman Campaigns.

Not rebuilt yet from the old game: Early Access, franchise ranks and media
ventures (merchandise, film, series), ports and sequels as their own project
types, contract automation, and work priorities.

## For developers

```
python3 -m unittest discover tests     # core rules: determinism, saves, books, commands
python3 tools/balance.py               # scripted strategies across 30 seeds, 5 years
python3 tools/balance.py --market 25   # watch the Rivals for 25 years
```

- `core/game.py` is the engine: days, money, commands, views, saves.
- `core/systems/` holds one module per system, run in the order in
  `core/systems/__init__.py`.
- `core/content.py` lists what exists (scopes, storefronts, cohorts, research);
  `core/balance.py` holds how strongly things react.
- [GLOSSARY.md](GLOSSARY.md) gives one name for each concept.

No licence has been chosen yet.
