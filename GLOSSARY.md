# Game Dev Studio Sim

A studio-management game: the player runs a game-development company, makes and
sells games, takes contract work and tries to keep the company solvent. It aims to
be the most realistic depiction of what it's like to become an indie developer.

Each concept has exactly one name, and code, UI and docs all use it. The _Avoid_
lines list the names this glossary retires.

## Playthrough

**Campaign**:
One playthrough, fixed at creation by its seed, start date and mode (normal or Ironman). It has exactly one Studio and ends for good when that Studio goes bankrupt or the player retires.
_Avoid_: Run, game, save (a save is a stored copy of a Campaign)

**Studio**:
The in-world company the player runs: its cash, people, reputation and catalogue. A Campaign never gets a second Studio; to start a new company, the player starts a new Campaign.
_Avoid_: Company (in type names), player, GameState

**Founder**:
The person who starts the Studio. A Campaign begins with the Founder alone: small savings, monthly living costs, no employees, no office.
_Avoid_: Player (the player is the human at the keyboard), owner

**Bankruptcy**:
The Studio's failure through insolvency. It ends the Campaign; play continues only in a new Campaign.
_Avoid_: Game over (as a type or state name), insolvency (that's the cause, not the outcome)

**Normal mode**:
A Campaign mode in which the player may reload an earlier save, including one from before a Bankruptcy.
_Avoid_: Easy mode, casual

**Ironman**:
A Campaign mode, chosen at creation, with no reloading: a Bankruptcy is final.
_Avoid_: Permadeath, hardcore

**Pause**:
The player stopping time. Only the player starts or ends a Pause.
_Avoid_: Hold, freeze

**Decision**:
A choice the game requires before time can continue; while one is unresolved, time stays stopped.
_Avoid_: Event, prompt, popup, hold

## Work and output

**Opportunity**:
Anything the Studio can choose to take on: an Idea, a Contract, a jam or a commission.
_Avoid_: Offer, lead

**Idea**:
An Opportunity pitched by the Studio's own team as the seed of an original Project.
_Avoid_: Concept, pitch (as a type name)

**Stage**:
Where a Project stands in its development. The list of Stages is not settled yet: it gets designed together with how Ideas grow into Products through iterations and experiments. Each Stage will have one name.
_Avoid_: Phase, step

**Project**:
Work in progress with a stage and a plan. A Project produces a new Product, changes an existing one (a port or a major update) or fulfils a Contract.
_Avoid_: Game, draft, development

**Product**:
A shipped thing that earns money; it belongs to an IP and can have several Releases.
_Avoid_: Game, title, ReleasedGame

**Release**:
One launch of a Product: a specific platform build on a specific store.
_Avoid_: Launch (as a noun for the object), listing

**Game**:
Casual word only, for player-facing text. Never a type or domain term; say Project, Product or Release.

## Money and obligations

**Contract**:
A work-for-hire deal the Studio accepts from a client: bounded pay for delivered work, with no Product for the Studio.
_Avoid_: Job (outside UI labels), commission. Do not use "contract" for technical specifications.

**Obligation**:
A dated payment the Studio owes or is owed. Contracts, loans and other deals can create Obligations, but an Obligation is not a deal.
_Avoid_: Bill, debt (debt is one source of Obligations)

## Market

**Market**:
The one shared economy of a Campaign. The Studio and every Rival sell to the same audiences on every Storefront, so each sale one makes is a sale another doesn't.
_Avoid_: Store (a Storefront is one channel in the Market), economy (in type names)

**Storefront**:
A channel where Releases are sold, such as a PC store, a console's shop or a mobile app store. Each has its own fees, cut and audience.
_Avoid_: Channel (in type names), platform (a platform is the hardware a Release runs on)

**Rival**:
Another studio in the market. Rivals are founded, grow, merge and collapse under the same market rules as the Studio; only their internal production is simplified. Rivals make their own business decisions, such as what to build and how hard to monetize, and bad ones can sink them. Size buys resilience but not immunity: a giant can fall after years of mismanagement or a string of disappointing releases, and whether any giant falls varies from Campaign to Campaign.
_Avoid_: Competitor (in type names), AI company, NPC studio

**Reach**:
How many people get to see the Studio's Releases. It starts tiny and grows with track record, fans and relationships with stores and press.
_Avoid_: Visibility, exposure, marketing (marketing is one way to raise Reach)

**Insight**:
How much the Studio can see of the market beyond its own sales: audiences, trends, how Rivals perform. It starts at gut feeling and grows with experience, tools and people.
_Avoid_: Intel, data, fog of war

**Standing**:
How seriously publishers, platforms and big clients take the Studio. Nothing is formally locked; with low Standing, offers are almost always turned down.
_Avoid_: Level, rank, unlock, tier
