# Game Dev Studio Sim

A studio-management game: the player runs a game-development company, makes and
sells games, takes contract work and tries to keep the company solvent. It aims to
be the most realistic depiction of what it's like to become an indie developer.

Each concept has exactly one name, and code, UI and docs all use it. The _Avoid_
lines list the names this glossary retires.

## Playthrough

**Campaign**:
One playthrough, fixed at creation by its seed, start date and mode (normal or Ironman). It has exactly one Studio and ends for good when that Studio goes bankrupt.
_Avoid_: Run, game, save (a save is a stored copy of a Campaign)

**Studio**:
The in-world company the player runs: its cash, team, Reputation, Fans and catalogue. A Campaign never gets a second Studio; to start a new company, the player starts a new Campaign.
_Avoid_: Company (in type names), player, GameState

**Founder**:
The person who starts the Studio. A Campaign begins with the Founder alone: small savings, monthly living costs, no employees, no office.
_Avoid_: Player (the player is the human at the keyboard), owner

**Bankruptcy**:
The Studio's failure through insolvency: eight weeks of negative cash. It ends the Campaign; play continues only in a new Campaign.
_Avoid_: Game over (as a type or state name), insolvency (that's the cause, not the outcome)

**Normal mode**:
A Campaign mode in which the player saves by hand and may reload an earlier save, including one from before a Bankruptcy.
_Avoid_: Easy mode, casual

**Ironman**:
A Campaign mode, chosen at creation, with one save that updates itself and no reloading: a Bankruptcy is final.
_Avoid_: Permadeath, hardcore

**Pause**:
The player stopping time. Only the player starts or ends a Pause. Opening a view or dialog does not pause.
_Avoid_: Hold, freeze

**Decision**:
A choice the game requires before time can continue; while one is unresolved, time stays stopped. Production milestones create Decisions.
_Avoid_: Event, prompt, popup, hold

## Making games

**Idea**:
A rough pitch from someone on the team: a fantasy, an activity, a setting and sometimes a twist. It hides three true values (fun, build effort and audience appeal); the studio only sees ranges that always contain the truth.
_Avoid_: Concept (as a type name), pitch (as a type name)

**Project**:
The one original game the Studio is developing, from the moment an Idea is explored until it is released, shelved or cancelled.
_Avoid_: Game, draft, development

**Stage**:
Where a Project stands: concept, design, production or polish. Concept is for learning and improving the Idea, design for the plan, production for building and polish for fixing bugs until release.
_Avoid_: Phase, step, Idea Shelf

**Experiment**:
Concept work that measures an Idea: a paper prototype, playable prototype, technical spike, look and sound study, pitch test or hook exploration. Each narrows some of the Idea's ranges.
_Avoid_: Test (alone), research (research is a separate system)

**Finding**:
What an Experiment, Iteration, Pivot or Decision taught the team, kept on the Project in order.
_Avoid_: Result, note, GDD entry

**Iteration**:
Concept work that rebuilds the core loop to make an Idea more fun, with diminishing returns.
_Avoid_: Polish (that's a Stage), prototype

**Discovery**:
A new direction an Experiment turned up. The team's mood hints whether it is better, but only a Pivot finds out.
_Avoid_: Twist (that's part of an Idea), insight

**Pivot**:
Turning a Project toward a Discovery. The genre changes and much of what the team knew becomes uncertain again.
_Avoid_: Reboot, rework

**Plan**:
The choices made in the design Stage: scope, format, look, Storefronts, business model, price, launch marketing and announcement.
_Avoid_: GDD, design document, production plan

**Product**:
A released game in the Market, made by the Studio or a Rival. It keeps selling, earning and changing (updates, price, support) after release.
_Avoid_: Title, ReleasedGame, catalog entry

**Release**:
The moment a Project becomes a Product on its Storefronts. A verb and an event, not an object.
_Avoid_: Launch (as a noun for the object)

**Game**:
Casual word only, for player-facing text. Never a type or domain term; say Idea, Project or Product.

## Money

**Contract**:
A work-for-hire deal the Studio accepts from a client: pay for delivered work by a deadline, with no Product for the Studio.
_Avoid_: Job (outside UI labels), commission. Do not use "contract" for technical specifications.

**Client trust**:
How much clients trust the Studio to deliver. It grows with delivered Contracts and opens bigger, better-paid offers.
_Avoid_: Contractor reputation, CTrust

**Ledger**:
The monthly books: income, expenses and financing (loans, publisher advances), by category. Every change in cash appears in it.
_Avoid_: Transactions, accounts

**Business model**:
How a Product makes money: premium, pay what you want, free with cosmetics, free with loot boxes or subscription.
_Avoid_: Monetization model, revenue model

**Greed**:
How hard a business model pushes players to pay. More Greed earns more per player and costs goodwill, for every studio alike.
_Avoid_: Monetization friction, aggressiveness

## Market

**Market**:
The one shared economy of a Campaign. The Studio and every Rival sell to the same Cohorts on every Storefront, so each sale one makes is a sale another doesn't.
_Avoid_: Store (a Storefront is one channel in the Market), economy (in type names)

**Cohort**:
One audience in the Market, such as core PC players or mobile casual players. Each has a size, tastes, a budget and the platforms it plays on.
_Avoid_: Segment, demographic, audience (in type names)

**Storefront**:
A channel where Products are sold, such as Steem, Scratch.io or the Paystation Store. Each has its own fees, cut, reach and visibility.
_Avoid_: Channel (in type names), platform (a platform is the hardware a Product runs on)

**Rival**:
Another studio in the Market. Rivals are founded, grow, merge and collapse under the same market rules as the Studio; only their internal production is simplified. Rivals make their own business decisions, such as what to build and how hard to monetize, and bad ones can sink them. Size buys resilience but not immunity: a giant can fall after years of mismanagement or a string of disappointing releases, and whether any giant falls varies from Campaign to Campaign.
_Avoid_: Competitor (in type names), AI company, NPC studio

**Awareness**:
The share of a Cohort that knows a Product exists. Only aware people can buy. Launch visibility, Fans, marketing, word of mouth and the charts raise it; time lowers it.
_Avoid_: Reach, visibility (that's a Storefront value), hype

**Fans**:
People who follow a studio because they loved one of its games. They notice its next releases.
_Avoid_: Followers, community (community actions are a live-ops tool)

**Reputation**:
A studio's track record from its reviews. Players expect more from a studio with high Reputation, and press, publishers and good applicants take it more seriously. Nothing is formally locked; with low Reputation, most say no.
_Avoid_: Standing, PTrust, prestige

**Insight**:
How much the Studio can see of the Market beyond its own sales: genre trends, which Cohorts buy, how Rivals earn. It starts at gut feeling and grows with research.
_Avoid_: Intel, data, fog of war

**Heat**:
How much the Market currently wants a genre. It drifts, rises after hits and falls when too many games in that genre come out.
_Avoid_: Trend score, popularity
