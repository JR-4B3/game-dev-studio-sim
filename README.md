# Game Dev Studio Sim

Working title. A studio-management game about running a game-development company,
aiming to be the most realistic depiction of what it's like to become an indie
developer.

This repo is a clean rebuild of
[Indie-Game-Dev-Simulator](https://github.com/JR-4B3/Indie-Game-Dev-Simulator).
The old game grew over months of sessions with different models and competing
ideas. This one is built once, from the ground up, with the vision settled first.
The old repo stays as the reference for how each system behaved.

## What changes from the old game

Everything the player could see and do in the old game comes back. These parts
change:

1. **One shared market.** The player's studio and every Rival act under the same
   market rules. Any studio can fall through bad decisions, including the biggest.
2. **The core doesn't know how it's drawn.** The simulation core takes commands and
   returns plain data. The first frontend is a 2D table interface. A Godot, 2D,
   isometric or 3D frontend can later drive the same core.
3. **Extensions don't break the economy.** New systems such as offices, rooms or
   buildings add costs and income. Adding one, and rebalancing after it, should
   be a local change that leaves the rest of the economy intact.
4. **Simpler code, the same or richer market dynamics.**
5. **Deeper product development.** A Product starts as an Idea from the team and
   grows through iterations and experiments. This part is still being designed.

## Docs

- [GLOSSARY.md](GLOSSARY.md) has one name for each concept. Code, UI and docs use
  those names.

No language, engine or licence has been chosen yet.
