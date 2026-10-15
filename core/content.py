"""Rule tables: what exists in the game world and what it costs.

Numbers that tune how strongly systems react live in balance.py. This file
lists the things themselves: scopes, storefronts, audiences, research and so
on. A frontend or a mod can read these tables to show options; the core only
ever refers to rows by their name or key.
"""
from .genres import GENRES

SKILLS = ("design", "art", "audio", "code")

# --- Genres -------------------------------------------------------------------
# Every genre belongs to one or more taste families. Audiences like families,
# so a new genre only needs a family to be understood by the whole market.
GENRE_FAMILIES = {
    "Action": ("action",), "Adventure": ("story",), "Building Game": ("systems", "cozy"),
    "Economic Simulation": ("systems",), "Fighting Game": ("action", "social"),
    "First-Person Shooter": ("action", "social"), "Interactive Movie": ("story",),
    "Platformer": ("action", "family"), "Puzzle Game": ("cozy", "family"),
    "Racing": ("action", "social", "family"), "Real-Time Strategy": ("systems",),
    "Role-Playing Game": ("story", "systems"), "Simulation": ("systems", "cozy"),
    "Skill Game": ("action", "cozy"), "Sports Game": ("social", "family"),
    "Strategy": ("systems",), "Survival Game": ("systems", "action"),
    "Third-Person Shooter": ("action",), "Visual Novel": ("story", "cozy"),
    "Battle Royale": ("social", "action"), "Extraction Shooter": ("action", "social"),
    "Survivors-like": ("action",), "Roguelike": ("systems",), "Roguelite": ("action", "systems"),
    "Deckbuilder": ("systems", "cozy"), "Automation": ("systems",), "Cozy Game": ("cozy", "family"),
    "Social Deduction": ("social",), "Immersive Sim": ("story", "systems"),
    "Soulslike": ("action",), "Metroidvania": ("action", "story"),
}
assert set(GENRE_FAMILIES) == set(GENRES)

# Skill mix a genre needs, as (design, art, audio, code) weights summing to 100.
from .genres import _GENRE_PROFILES  # noqa: E402
GENRE_SKILLS = {genre: profile[1] for genre, profile in _GENRE_PROFILES.items()}

# --- Audiences ----------------------------------------------------------------
# The Market is these cohorts. Population is in people. Shopping is the share
# of the cohort that looks for a new game in a given week. Budget is the price
# that feels normal to them. Platform shares say where they play.
COHORTS = (
    {"key": "core_pc", "name": "Core PC players", "population": 110_000_000, "shopping": 0.030,
     "budget": 30, "price_sensitivity": 0.9, "quality_sensitivity": 1.25, "monetization_tolerance": 0.30,
     "novelty": 0.6, "platforms": {"PC": 0.85, "Console": 0.12, "Mobile": 0.03},
     "tastes": {"action": 1.0, "story": 0.8, "systems": 0.75, "cozy": 0.3, "social": 0.6, "family": 0.15}},
    {"key": "console", "name": "Console players", "population": 140_000_000, "shopping": 0.022,
     "budget": 45, "price_sensitivity": 0.8, "quality_sensitivity": 1.0, "monetization_tolerance": 0.45,
     "novelty": 0.35, "platforms": {"PC": 0.08, "Console": 0.88, "Mobile": 0.04},
     "tastes": {"action": 1.0, "story": 0.9, "systems": 0.35, "cozy": 0.45, "social": 0.75, "family": 0.4}},
    {"key": "enthusiasts", "name": "Strategy & sim fans", "population": 38_000_000, "shopping": 0.030,
     "budget": 30, "price_sensitivity": 0.7, "quality_sensitivity": 1.35, "monetization_tolerance": 0.15,
     "novelty": 0.55, "platforms": {"PC": 0.9, "Console": 0.07, "Mobile": 0.03},
     "tastes": {"action": 0.25, "story": 0.6, "systems": 1.0, "cozy": 0.45, "social": 0.2, "family": 0.1}},
    {"key": "indie", "name": "Indie explorers", "population": 30_000_000, "shopping": 0.045,
     "budget": 15, "price_sensitivity": 1.0, "quality_sensitivity": 1.1, "monetization_tolerance": 0.10,
     "novelty": 1.0, "platforms": {"PC": 0.85, "Console": 0.12, "Mobile": 0.03},
     "tastes": {"action": 0.7, "story": 0.9, "systems": 0.8, "cozy": 0.85, "social": 0.3, "family": 0.3}},
    {"key": "cozy", "name": "Cozy & casual", "population": 110_000_000, "shopping": 0.018,
     "budget": 15, "price_sensitivity": 1.2, "quality_sensitivity": 0.8, "monetization_tolerance": 0.5,
     "novelty": 0.4, "platforms": {"PC": 0.35, "Console": 0.3, "Mobile": 0.35},
     "tastes": {"action": 0.2, "story": 0.5, "systems": 0.4, "cozy": 1.0, "social": 0.35, "family": 0.6}},
    {"key": "social", "name": "Competitive & social", "population": 95_000_000, "shopping": 0.020,
     "budget": 25, "price_sensitivity": 1.0, "quality_sensitivity": 0.95, "monetization_tolerance": 0.7,
     "novelty": 0.3, "platforms": {"PC": 0.45, "Console": 0.4, "Mobile": 0.15},
     "tastes": {"action": 0.85, "story": 0.2, "systems": 0.3, "cozy": 0.2, "social": 1.0, "family": 0.3}},
    {"key": "mobile", "name": "Mobile casual", "population": 380_000_000, "shopping": 0.012,
     "budget": 3, "price_sensitivity": 1.6, "quality_sensitivity": 0.6, "monetization_tolerance": 0.8,
     "novelty": 0.3, "platforms": {"PC": 0.02, "Console": 0.01, "Mobile": 0.97},
     "tastes": {"action": 0.5, "story": 0.3, "systems": 0.45, "cozy": 0.9, "social": 0.6, "family": 0.6}},
    {"key": "family", "name": "Kids & families", "population": 75_000_000, "shopping": 0.015,
     "budget": 30, "price_sensitivity": 1.1, "quality_sensitivity": 0.8, "monetization_tolerance": 0.35,
     "novelty": 0.3, "platforms": {"PC": 0.15, "Console": 0.5, "Mobile": 0.35},
     "tastes": {"action": 0.55, "story": 0.35, "systems": 0.2, "cozy": 0.85, "social": 0.4, "family": 1.0}},
)
COHORT_KEYS = tuple(c["key"] for c in COHORTS)
COHORT = {c["key"]: c for c in COHORTS}

# --- Storefronts ----------------------------------------------------------------
# Reach is the share of a platform's players who shop there. Visibility is how
# much a new release on that store gets noticed without any marketing.
STOREFRONTS = (
    {"name": "Scratch.io", "platform": "PC", "fee": 0, "cut": 0.10, "reach": 0.12, "visibility": 1.0, "research": None},
    {"name": "Epoch Store", "platform": "PC", "fee": 100, "cut": 0.12, "reach": 0.30, "visibility": 1.5, "research": None},
    {"name": "Steem", "platform": "PC", "fee": 100, "cut": 0.30, "reach": 0.95, "visibility": 1.0, "research": None},
    {"name": "Pear App Store", "platform": "Mobile", "fee": 99, "cut": 0.30, "reach": 0.45, "visibility": 0.6, "research": "mobile_distribution"},
    {"name": "Gooble Play", "platform": "Mobile", "fee": 25, "cut": 0.30, "reach": 0.60, "visibility": 0.5, "research": "mobile_distribution"},
    {"name": "YBox Store", "platform": "Console", "fee": 8_000, "cut": 0.30, "reach": 0.30, "visibility": 2.0, "research": "console_certification"},
    {"name": "Paystation Store", "platform": "Console", "fee": 12_500, "cut": 0.30, "reach": 0.45, "visibility": 2.0, "research": "console_certification"},
    {"name": "Nintendu eShop", "platform": "Console", "fee": 10_000, "cut": 0.30, "reach": 0.35, "visibility": 2.0, "research": "console_certification"},
)
STOREFRONT = {s["name"]: s for s in STOREFRONTS}

# --- Project plan options ---------------------------------------------------------
# Work is in work points; one average developer produces about 50 a week.
# Price is what players expect to pay for that much game.
SCOPES = (
    {"name": "Bite-size", "work": 150, "setup": 0, "price": 2.99, "content": 0.35, "decisions": 0},
    {"name": "Micro", "work": 800, "setup": 300, "price": 4.99, "content": 0.55, "decisions": 1},
    {"name": "Compact", "work": 3_000, "setup": 3_000, "price": 9.99, "content": 0.75, "decisions": 2},
    {"name": "Small", "work": 11_000, "setup": 25_000, "price": 14.99, "content": 1.0, "decisions": 2},
    {"name": "Mid-size", "work": 55_000, "setup": 250_000, "price": 24.99, "content": 1.4, "decisions": 3},
    {"name": "Ambitious", "work": 125_000, "setup": 900_000, "price": 39.99, "content": 1.9, "decisions": 3},
    {"name": "Large", "work": 340_000, "setup": 5_000_000, "price": 59.99, "content": 3.0, "decisions": 4},
    {"name": "Blockbuster", "work": 800_000, "setup": 25_000_000, "price": 69.99, "content": 4.5, "decisions": 4},
)
SCOPE = {s["name"]: s for s in SCOPES}

FORMATS = (
    {"name": "Offline solo", "work": 1.0, "setup": 0, "server_rent": 0, "hosting": 0.0, "research": None, "tastes": {}},
    {"name": "Online co-op", "work": 1.45, "setup": 20_000, "server_rent": 120, "hosting": 0.004, "research": "online_coop", "tastes": {"social": 0.25, "action": 0.1}},
    {"name": "Competitive online", "work": 2.1, "setup": 150_000, "server_rent": 450, "hosting": 0.006, "research": "competitive_online", "tastes": {"social": 0.45}},
    {"name": "Persistent world", "work": 3.4, "setup": 1_000_000, "server_rent": 900, "hosting": 0.010, "research": "persistent_worlds", "tastes": {"social": 0.35, "systems": 0.2}},
    {"name": "MMO", "work": 8.5, "setup": 8_000_000, "server_rent": 1_600, "hosting": 0.015, "research": "mmo_technology", "tastes": {"social": 0.5, "story": 0.2}},
)
FORMAT = {f["name"]: f for f in FORMATS}

PRESENTATIONS = (
    {"name": "Minimal 2D", "work": 0.8, "skills": (55, 15, 10, 20), "appeal": {"indie": 0.1, "mobile": 0.1, "console": -0.2, "core_pc": -0.1}},
    {"name": "Pixel art", "work": 1.0, "skills": (35, 35, 10, 20), "appeal": {"indie": 0.2, "core_pc": 0.05}},
    {"name": "Hand-drawn 2D", "work": 1.25, "skills": (25, 50, 10, 15), "appeal": {"indie": 0.15, "cozy": 0.15, "family": 0.1}},
    {"name": "Stylized 3D", "work": 1.35, "skills": (25, 40, 10, 25), "appeal": {"console": 0.1, "family": 0.1, "social": 0.1}},
    {"name": "Realistic 3D", "work": 1.8, "skills": (15, 50, 15, 20), "appeal": {"console": 0.25, "core_pc": 0.2, "indie": -0.15, "mobile": -0.2}},
)
PRESENTATION = {p["name"]: p for p in PRESENTATIONS}

# Greed is how hard the model pushes players to pay. It earns more per player
# and costs goodwill, the same way for every studio in the Market.
BUSINESS_MODELS = (
    {"name": "Premium", "work": 1.0, "setup": 0, "free": False, "payers": 0.0, "arppu": 0.0, "greed": 0.0, "research": None},
    {"name": "Pay what you want", "work": 0.9, "setup": 0, "free": True, "payers": 0.03, "arppu": 4.0, "greed": 0.0, "research": None},
    {"name": "Free with cosmetics", "work": 1.25, "setup": 5_000, "free": True, "payers": 0.04, "arppu": 9.0, "greed": 0.2, "research": "content_updates"},
    {"name": "Free with loot boxes", "work": 1.3, "setup": 10_000, "free": True, "payers": 0.07, "arppu": 16.0, "greed": 0.75, "research": "live_operations"},
    {"name": "Subscription", "work": 1.4, "setup": 50_000, "free": False, "payers": 1.0, "arppu": 11.99, "greed": 0.25, "research": "live_operations"},
)
BUSINESS_MODEL = {m["name"]: m for m in BUSINESS_MODELS}

PRICE_POINTS = (0.99, 1.99, 2.99, 4.99, 7.99, 9.99, 14.99, 19.99, 24.99, 29.99, 39.99, 49.99, 59.99, 69.99)

# Launch marketing paid at release. Reach is extra people made aware per dollar.
LAUNCH_MARKETING = (
    {"name": "Word of mouth", "cost": 0},
    {"name": "Social posts", "cost": 500},
    {"name": "Small ad budget", "cost": 5_000},
    {"name": "Creator keys", "cost": 20_000},
    {"name": "Launch campaign", "cost": 150_000},
    {"name": "Global campaign", "cost": 2_000_000},
)
LAUNCH = {m["name"]: m for m in LAUNCH_MARKETING}

# Announcing early builds awareness during production but makes delays visible.
ANNOUNCEMENTS = (
    {"name": "Stealth", "weekly_awareness": 0.0, "decay": 0.0},
    {"name": "Late reveal", "weekly_awareness": 0.5, "decay": 0.01},
    {"name": "Open development", "weekly_awareness": 1.0, "decay": 0.025},
)
ANNOUNCEMENT = {a["name"]: a for a in ANNOUNCEMENTS}

# --- Concept work -------------------------------------------------------------
# Experiments spend work on learning about an Idea. "reveals" names the hidden
# values they measure; "discovery" is the chance to find a new direction.
EXPERIMENTS = (
    {"key": "paper", "name": "Paper prototype", "work": 25, "skill": "design", "reveals": {"fun": 0.35},
     "discovery": 0.15, "blurb": "Play the rules on paper. Cheap, rough read on whether the core is fun."},
    {"key": "playable", "name": "Playable prototype", "work": 70, "skill": "code", "reveals": {"fun": 0.65, "complexity": 0.3},
     "discovery": 0.3, "blurb": "Build the core loop for real. The best evidence of fun there is."},
    {"key": "spike", "name": "Technical spike", "work": 45, "skill": "code", "reveals": {"complexity": 0.7},
     "discovery": 0.05, "blurb": "Build the riskiest technical piece first and see how hard it really is."},
    {"key": "look", "name": "Look & sound study", "work": 30, "skill": "art", "reveals": {"appeal": 0.3},
     "discovery": 0.1, "blurb": "Mock up how it looks and sounds. Tests the first impression."},
    {"key": "pitch", "name": "Pitch test", "work": 20, "skill": "research", "reveals": {"appeal": 0.7},
     "discovery": 0.1, "blurb": "Show the pitch to players and read which audiences light up."},
    {"key": "hook", "name": "Hook exploration", "work": 40, "skill": "design", "reveals": {"fun": 0.2},
     "discovery": 0.45, "needs_hook": True, "blurb": "Push the unusual idea to its limits and see what falls out."},
)
EXPERIMENT = {e["key"]: e for e in EXPERIMENTS}

# Iterating on the core loop raises fun with diminishing returns.
ITERATION = {"work": 60, "skill": "design"}

# --- Production decisions -------------------------------------------------------
PRODUCTION_DECISIONS = (
    {"at": 0.15, "title": "Vertical slice review", "question": "The core loop works, but it is not distinctive yet.",
     "options": (
         {"name": "Commit to the proven loop", "effect": "-6% remaining work, steadier quality", "work": 0.94, "quality": 2, "appeal": -0.05},
         {"name": "Fund the standout mechanic", "effect": "+14% remaining work, stronger appeal, more bugs", "work": 1.14, "quality": 1, "appeal": 0.12, "bugs": 0.15, "fatigue": 3},
     )},
    {"at": 0.35, "title": "Scope lock", "question": "The full feature list no longer fits the schedule.",
     "options": (
         {"name": "Cut the weakest feature", "effect": "-12% remaining work, slightly less game", "work": 0.88, "quality": 1, "appeal": -0.04},
         {"name": "Honor the full plan", "effect": "+16% remaining work, more quality, team fatigue", "work": 1.16, "quality": 3, "appeal": 0.05, "fatigue": 5},
     )},
    {"at": 0.70, "title": "Alpha review", "question": "There is time for either stability or one more content push.",
     "options": (
         {"name": "Run a stabilization sprint", "effect": "+8% remaining work, find and fix a quarter of the bugs", "work": 1.08, "quality": 1, "bug_fix": 0.25},
         {"name": "Add the late content beat", "effect": "+18% remaining work, more appeal, more bugs", "work": 1.18, "appeal": 0.08, "bugs": 0.25},
     )},
    {"at": 0.90, "title": "Release candidate", "question": "Reviews could improve, but every extra week burns runway.",
     "options": (
         {"name": "Delay for polish", "effect": "+40% remaining work, fix almost half the bugs, more quality", "work": 1.4, "quality": 3, "bug_fix": 0.45},
         {"name": "Hold the plan", "effect": "-20% remaining work, quality risk", "work": 0.8, "quality": -2},
     )},
)

# --- Live operations ---------------------------------------------------------
UPDATE_SIZES = (
    {"name": "Hotfix", "work": 25, "cost": 0, "fixes": 0.35, "new_bugs": 0.02, "appeal": 0.0, "awareness": 0.0, "research": None},
    {"name": "Patch", "work": 70, "cost": 0, "fixes": 0.6, "new_bugs": 0.05, "appeal": 0.02, "awareness": 0.002, "research": None},
    {"name": "Content update", "work": 220, "cost": 2_000, "fixes": 0.2, "new_bugs": 0.1, "appeal": 0.06, "awareness": 0.01, "research": "content_updates"},
    {"name": "Expansion", "work": 600, "cost": 15_000, "fixes": 0.2, "new_bugs": 0.15, "appeal": 0.12, "awareness": 0.025, "research": "expansion_pipeline"},
    {"name": "Paid DLC", "work": 900, "cost": 30_000, "fixes": 0.1, "new_bugs": 0.15, "appeal": 0.05, "awareness": 0.02, "dlc": True, "research": "paid_dlc"},
)
UPDATE_SIZE = {u["name"]: u for u in UPDATE_SIZES}

SUPPORT_LEVELS = (
    {"name": "Active", "capacity": 0.04, "sentiment": 0.6, "hosting": 1.0},
    {"name": "Maintenance", "capacity": 0.015, "sentiment": 0.0, "hosting": 0.6},
    {"name": "Sunset", "capacity": 0.0, "sentiment": -0.8, "hosting": 0.0},
)
SUPPORT = {s["name"]: s for s in SUPPORT_LEVELS}

# Paid promotion: cost buys awareness. Press and creators pay attention to
# Reputation, so an unknown studio gets less for the same money.
PROMOTIONS = (
    {"key": "social", "name": "Social media push", "cost": 300, "weeks": 1, "capacity": 0.04, "people": 6_000, "reputation_weight": 0.0, "research": None,
     "effect": "Post clips and screenshots. Small, but costs almost nothing."},
    {"key": "festival", "name": "Digital festival demo", "cost": 1_500, "weeks": 3, "capacity": 0.15, "people": 60_000, "reputation_weight": 0.3, "research": "promotion_basics",
     "effect": "Ship a demo into a store festival. Takes real team time."},
    {"key": "press", "name": "Press outreach", "cost": 4_000, "weeks": 2, "capacity": 0.05, "people": 120_000, "reputation_weight": 0.8, "research": "targeted_marketing",
     "effect": "Send builds and pitches to the press. They mostly answer reputable studios."},
    {"key": "creators", "name": "Creator key campaign", "cost": 12_000, "weeks": 2, "capacity": 0.05, "people": 350_000, "reputation_weight": 0.5, "research": "creator_relations",
     "effect": "Keys to relevant creators. Their audiences trust them."},
    {"key": "streamer", "name": "Sponsored stream", "cost": 40_000, "weeks": 1, "capacity": 0.02, "people": 1_200_000, "reputation_weight": 0.2, "research": "creator_relations",
     "effect": "Pay a large streamer to play it live."},
    {"key": "event", "name": "Games event booth", "cost": 90_000, "weeks": 4, "capacity": 0.18, "people": 2_500_000, "reputation_weight": 0.4, "research": "event_marketing",
     "effect": "Booth, travel and demo stations. Takes a big share of the team."},
    {"key": "showcase", "name": "Showcase slot", "cost": 600_000, "weeks": 2, "capacity": 0.05, "people": 18_000_000, "reputation_weight": 0.3, "research": "event_marketing",
     "effect": "A trailer slot in a major showcase."},
)
PROMOTION = {p["key"]: p for p in PROMOTIONS}

COMMUNITY_ACTIONS = (
    {"key": "diary", "name": "Dev diary", "cost": 0, "weeks": 1, "capacity": 0.06, "sentiment": 2, "people": 1_500, "cooldown": 4,
     "effect": "Share progress honestly. Builds goodwill slowly."},
    {"key": "beta", "name": "Open beta", "cost": 2_000, "weeks": 3, "capacity": 0.2, "sentiment": 3, "people": 15_000, "cooldown": 12, "reveals_bugs": 0.5, "project_only": True,
     "effect": "Let players in early. Finds bugs and builds an audience."},
    {"key": "event", "name": "Community event", "cost": 1_000, "weeks": 2, "capacity": 0.12, "sentiment": 5, "people": 5_000, "cooldown": 8,
     "effect": "Run a tournament, contest or challenge week."},
    {"key": "apology", "name": "Public apology", "cost": 0, "weeks": 1, "capacity": 0.04, "sentiment": 8, "people": 0, "cooldown": 12, "release_only": True,
     "effect": "Own the mistakes. Works once in a while, not every month."},
)
COMMUNITY = {c["key"]: c for c in COMMUNITY_ACTIONS}

# --- Business ---------------------------------------------------------------------
LOANS = (
    {"name": "Small business loan", "principal": 10_000, "weeks": 52, "rate": 0.12},
    {"name": "Production loan", "principal": 60_000, "weeks": 104, "rate": 0.10},
    {"name": "Growth loan", "principal": 300_000, "weeks": 156, "rate": 0.09},
)
LOAN = {l["name"]: l for l in LOANS}

# Publishers judge a pitch by its evidence and the studio's Reputation. Their
# bar is a soft one: anyone can pitch, few unknowns get a yes.
PUBLISHERS = (
    {"name": "Northstar Publishing", "bar": 45, "advance": 1.2, "recoup_share": 0.5, "share": 0.30, "people": 40_000},
    {"name": "Cinder House", "bar": 60, "advance": 1.6, "recoup_share": 0.5, "share": 0.25, "people": 250_000},
    {"name": "Atlas Interactive", "bar": 75, "advance": 2.2, "recoup_share": 0.55, "share": 0.22, "people": 2_000_000},
)
PUBLISHER = {p["name"]: p for p in PUBLISHERS}

# --- People -------------------------------------------------------------------------
ROLES = (
    {"name": "Game Designer", "skills": (70, 35, 30, 40, 45)},
    {"name": "Programmer", "skills": (40, 25, 25, 72, 45)},
    {"name": "Artist", "skills": (40, 72, 30, 25, 30)},
    {"name": "Audio Designer", "skills": (35, 35, 72, 30, 30)},
    {"name": "Generalist", "skills": (50, 45, 40, 50, 40)},
    {"name": "Producer", "skills": (50, 30, 25, 35, 60)},
)
SENIORITY = (("Junior", 0.35, -14), ("Mid-level", 0.45, 0), ("Senior", 0.20, 14))

TRAITS = {
    "Steady": {"output": 1.0, "bugs": 0.85, "fatigue": 0.9, "ideas": 1.0},
    "Fast": {"output": 1.15, "bugs": 1.2, "fatigue": 1.0, "ideas": 1.0},
    "Perfectionist": {"output": 0.9, "bugs": 0.75, "fatigue": 1.15, "ideas": 1.0, "craft": 4},
    "Creative": {"output": 1.0, "bugs": 1.05, "fatigue": 1.0, "ideas": 1.8},
    "Mentor": {"output": 0.95, "bugs": 1.0, "fatigue": 1.0, "ideas": 1.0, "team_xp": 0.15},
    "Night owl": {"output": 1.08, "bugs": 1.1, "fatigue": 1.25, "ideas": 1.2},
    "Calm": {"output": 1.0, "bugs": 1.0, "fatigue": 0.75, "ideas": 0.9},
    "Curious": {"output": 0.97, "bugs": 1.0, "fatigue": 1.0, "ideas": 1.3, "research": 1.25},
}

FIRST_NAMES = ("Alex", "Sam", "Robin", "Kim", "Jo", "Mika", "Noa", "Ari", "Lee", "Rene", "Toni", "Yuki", "Sasha", "Elia",
               "Kai", "Nico", "Luca", "Mara", "Ida", "Finn", "Lena", "Omar", "Priya", "Chen", "Zoe", "Ines", "Hana", "Leo",
               "Maya", "Tariq", "Sofia", "Jonas", "Amir", "Lina", "Ravi", "Eva", "Malik", "Nora", "Theo", "Ayla")
LAST_NAMES = ("Berg", "Novak", "Okafor", "Silva", "Tanaka", "Weber", "Kowalski", "Haddad", "Laine", "Moreau", "Ivanova",
              "Costa", "Park", "Nguyen", "Fischer", "Rossi", "Jensen", "Ortiz", "Sato", "Brandt", "Kaya", "Lund", "Mehta")

# --- Contracts -------------------------------------------------------------------
CONTRACT_CLIENTS = ("Brightside Apps", "Kestrel Media", "Northwind Toys", "Hollow Pine Agency", "Granite Bank",
                    "Pixelmint", "Orbit Learning", "Tidewater Museum", "Lumen Health", "Copperleaf Games",
                    "Bluefin Studios", "Arcturus Publishing", "Saffron Retail", "Vantage Sports")
CONTRACT_JOBS = (
    ("Port a mobile puzzle game", "code"), ("Build an advergame", "design"), ("Make a museum kiosk game", "design"),
    ("Draw sprite sheets", "art"), ("Compose a jingle pack", "audio"), ("Fix a buggy multiplayer lobby", "code"),
    ("Prototype a learning game", "design"), ("Animate store mascots", "art"), ("Sound design for a trailer", "audio"),
    ("Optimize a console build", "code"), ("Level design for a sequel", "design"), ("UI art for a strategy game", "art"),
)

# --- Research ------------------------------------------------------------------------
# Every node here has an effect the rules actually apply. "monthly" is the
# running cost once researched.
RESEARCH = (
    # Product
    {"key": "online_coop", "branch": "Product", "name": "Connected Games", "cost": 6_000, "work": 300, "prereq": (), "effect": "Make online co-op games"},
    {"key": "competitive_online", "branch": "Product", "name": "Competitive Networking", "cost": 60_000, "work": 1_200, "prereq": ("online_coop", "qa"), "effect": "Make competitive online games"},
    {"key": "persistent_worlds", "branch": "Product", "name": "Persistent Worlds", "cost": 400_000, "work": 3_500, "prereq": ("competitive_online", "live_operations"), "effect": "Make persistent-world games"},
    {"key": "mmo_technology", "branch": "Product", "name": "Massive Online Technology", "cost": 3_000_000, "work": 9_000, "prereq": ("persistent_worlds", "advanced_coordination"), "effect": "Make MMOs"},
    # Operations
    {"key": "hardware", "branch": "Operations", "name": "Current Workstations", "cost": 3_000, "work": 120, "monthly": 60, "prereq": (), "effect": "+10% work output"},
    {"key": "tools", "branch": "Operations", "name": "Professional Toolchain", "cost": 5_000, "work": 200, "monthly": 150, "prereq": (), "effect": "+3 quality on every release"},
    {"key": "qa", "branch": "Operations", "name": "QA Device Library", "cost": 12_000, "work": 400, "monthly": 250, "prereq": ("tools",), "effect": "25% fewer bugs, found sooner"},
    {"key": "production_pipeline", "branch": "Operations", "name": "Production Pipeline", "cost": 25_000, "work": 600, "prereq": ("hardware",), "effect": "Teams above five lose less output to coordination"},
    {"key": "research_lab", "branch": "Operations", "name": "Research Lab", "cost": 40_000, "work": 800, "monthly": 500, "prereq": ("production_pipeline",), "effect": "+25% research output"},
    {"key": "advanced_coordination", "branch": "Operations", "name": "Advanced Coordination", "cost": 300_000, "work": 3_000, "monthly": 2_500, "prereq": ("production_pipeline",), "effect": "Teams above twelve lose much less output"},
    # People
    {"key": "mentorship", "branch": "People", "name": "Mentorship", "cost": 2_000, "work": 150, "prereq": (), "effect": "+25% experience"},
    {"key": "structured_training", "branch": "People", "name": "Structured Training", "cost": 4_000, "work": 250, "prereq": (), "effect": "Training takes three weeks instead of four"},
    {"key": "paid_leave", "branch": "People", "name": "Paid Leave Program", "cost": 6_000, "work": 300, "monthly": 40, "prereq": ("structured_training",), "effect": "Vacations remove more fatigue and lift morale"},
    {"key": "health", "branch": "People", "name": "Health Plan", "cost": 15_000, "work": 500, "monthly": 300, "prereq": ("paid_leave",), "effect": "Fatigue builds 20% slower"},
    {"key": "auto_leave", "branch": "People", "name": "Sustainable Scheduling", "cost": 30_000, "work": 900, "prereq": ("health",), "effect": "Very tired people take vacation automatically"},
    {"key": "academy", "branch": "People", "name": "Internal Academy", "cost": 200_000, "work": 3_000, "monthly": 3_000, "prereq": ("mentorship", "structured_training"), "effect": "+35% experience; training takes two weeks"},
    # Business
    {"key": "promotion_basics", "branch": "Business", "name": "Community Marketing", "cost": 1_500, "work": 120, "prereq": (), "effect": "Festival demos"},
    {"key": "market_research", "branch": "Business", "name": "Market Research", "cost": 3_000, "work": 200, "prereq": (), "effect": "See genre trends as numbers; sharper pitch tests"},
    {"key": "targeted_marketing", "branch": "Business", "name": "Targeted Marketing", "cost": 10_000, "work": 400, "prereq": ("promotion_basics",), "effect": "Press outreach"},
    {"key": "mobile_distribution", "branch": "Business", "name": "Mobile Distribution", "cost": 5_000, "work": 250, "prereq": (), "effect": "Release on mobile storefronts"},
    {"key": "creator_relations", "branch": "Business", "name": "Creator Relations", "cost": 40_000, "work": 1_000, "prereq": ("targeted_marketing",), "effect": "Creator and streamer campaigns"},
    {"key": "console_certification", "branch": "Business", "name": "Console Certification", "cost": 60_000, "work": 1_200, "prereq": ("qa",), "effect": "Release on console storefronts"},
    {"key": "analytics", "branch": "Business", "name": "Store Analytics", "cost": 25_000, "work": 700, "monthly": 200, "prereq": ("market_research",), "effect": "See which audiences buy your games and how rivals sell"},
    {"key": "event_marketing", "branch": "Business", "name": "Events & Showcases", "cost": 120_000, "work": 2_000, "prereq": ("creator_relations",), "effect": "Event booths and showcase slots"},
    # Live ops
    {"key": "content_updates", "branch": "Live Ops", "name": "Content Updates", "cost": 4_000, "work": 250, "prereq": (), "effect": "Content updates; free-to-play with cosmetics"},
    {"key": "expansion_pipeline", "branch": "Live Ops", "name": "Expansion Pipeline", "cost": 25_000, "work": 700, "prereq": ("content_updates",), "effect": "Expansions"},
    {"key": "paid_dlc", "branch": "Live Ops", "name": "Paid DLC Pipeline", "cost": 50_000, "work": 1_200, "prereq": ("expansion_pipeline",), "effect": "Paid DLC"},
    {"key": "live_operations", "branch": "Live Ops", "name": "Live Operations", "cost": 150_000, "work": 2_500, "monthly": 2_000, "prereq": ("paid_dlc",), "effect": "Subscriptions and loot boxes"},
    {"key": "automated_deployment", "branch": "Live Ops", "name": "Automated Deployment", "cost": 80_000, "work": 1_800, "prereq": ("qa", "expansion_pipeline"), "effect": "+25% update output"},
)
RESEARCH_NODE = {r["key"]: r for r in RESEARCH}

# --- Rivals -------------------------------------------------------------------------
# Parody versions of the studios a real market would have. Staff is head count.
RIVALS = (
    {"name": "Nintari", "staff": 960, "skill": 82, "reputation": 90, "fans": 30_000_000, "greed": 0.1, "genres": ("Platformer", "Cozy Game", "Racing", "Puzzle Game")},
    {"name": "Sunny Interactive", "staff": 800, "skill": 80, "reputation": 86, "fans": 26_000_000, "greed": 0.25, "genres": ("Action", "Adventure", "Third-Person Shooter", "Role-Playing Game")},
    {"name": "Macrohard Games", "staff": 1_040, "skill": 72, "reputation": 74, "fans": 24_000_000, "greed": 0.35, "genres": ("First-Person Shooter", "Racing", "Strategy", "Simulation")},
    {"name": "Electronic Frontiers", "staff": 880, "skill": 70, "reputation": 60, "fans": 22_000_000, "greed": 0.75, "genres": ("Sports Game", "First-Person Shooter", "Racing")},
    {"name": "Ubicore", "staff": 720, "skill": 68, "reputation": 60, "fans": 14_000_000, "greed": 0.55, "genres": ("Action", "Adventure", "Immersive Sim", "Survival Game")},
    {"name": "Starfall Interactive", "staff": 360, "skill": 84, "reputation": 88, "fans": 12_000_000, "greed": 0.3, "genres": ("Action", "Adventure", "Third-Person Shooter")},
    {"name": "Frostmire Games", "staff": 280, "skill": 80, "reputation": 82, "fans": 10_000_000, "greed": 0.3, "genres": ("Role-Playing Game", "Strategy", "Deckbuilder")},
    {"name": "Paragon Studios", "staff": 400, "skill": 74, "reputation": 70, "fans": 16_000_000, "greed": 0.6, "genres": ("Battle Royale", "Third-Person Shooter", "Building Game")},
    {"name": "Heliosoft", "staff": 440, "skill": 72, "reputation": 72, "fans": 13_000_000, "greed": 0.5, "genres": ("Role-Playing Game", "Strategy", "Social Deduction")},
    {"name": "Vantage Point", "staff": 260, "skill": 70, "reputation": 66, "fans": 9_000_000, "greed": 0.6, "genres": ("First-Person Shooter", "Extraction Shooter", "Battle Royale")},
    {"name": "Novacore", "staff": 180, "skill": 74, "reputation": 76, "fans": 6_000_000, "greed": 0.3, "genres": ("Role-Playing Game", "Strategy", "Adventure")},
    {"name": "Red Engine Studio", "staff": 200, "skill": 82, "reputation": 85, "fans": 7_000_000, "greed": 0.2, "genres": ("Role-Playing Game", "Action", "Adventure")},
    {"name": "Runestone Forge", "staff": 72, "skill": 78, "reputation": 86, "fans": 3_000_000, "greed": 0.1, "genres": ("Role-Playing Game", "Strategy")},
    {"name": "Quantum Quill", "staff": 56, "skill": 76, "reputation": 79, "fans": 2_000_000, "greed": 0.15, "genres": ("Strategy", "Deckbuilder", "Economic Simulation")},
    {"name": "Nocturne Labs", "staff": 36, "skill": 72, "reputation": 74, "fans": 1_200_000, "greed": 0.2, "genres": ("Survival Game", "Adventure", "Immersive Sim")},
    {"name": "Redwood Arcade", "staff": 32, "skill": 66, "reputation": 69, "fans": 1_100_000, "greed": 0.4, "genres": ("Racing", "Sports Game", "Fighting Game")},
    {"name": "Hyperbolt", "staff": 12, "skill": 74, "reputation": 78, "fans": 300_000, "greed": 0.1, "genres": ("Action", "Roguelike", "Skill Game")},
    {"name": "Lumen Works", "staff": 9, "skill": 76, "reputation": 81, "fans": 250_000, "greed": 0.05, "genres": ("Puzzle Game", "Cozy Game", "Automation")},
    {"name": "Driftwood Games", "staff": 10, "skill": 68, "reputation": 71, "fans": 200_000, "greed": 0.1, "genres": ("Survival Game", "Building Game", "Simulation")},
    {"name": "Pixel Forge", "staff": 6, "skill": 72, "reputation": 72, "fans": 150_000, "greed": 0.1, "genres": ("Roguelike", "Metroidvania", "Deckbuilder")},
    {"name": "Moonpetal Games", "staff": 4, "skill": 66, "reputation": 68, "fans": 90_000, "greed": 0.05, "genres": ("Cozy Game", "Simulation", "Visual Novel")},
    {"name": "Tiny Anvil", "staff": 3, "skill": 64, "reputation": 65, "fans": 60_000, "greed": 0.05, "genres": ("Platformer", "Puzzle Game", "Metroidvania")},
    {"name": "Ghost Lantern", "staff": 4, "skill": 66, "reputation": 70, "fans": 80_000, "greed": 0.05, "genres": ("Survival Game", "Adventure", "Visual Novel")},
    {"name": "Papercut Studio", "staff": 3, "skill": 68, "reputation": 76, "fans": 70_000, "greed": 0.05, "genres": ("Visual Novel", "Interactive Movie", "Cozy Game")},
)
STUDIO_NAME_PARTS = (
    ("Bright", "Hollow", "Iron", "Little", "Quiet", "Wild", "Paper", "Copper", "Lantern", "Rogue", "Velvet", "Thunder",
     "Mossy", "Glass", "Second", "Odd", "North", "Salt", "Kite", "Ember", "Cloud", "Brave", "Pocket", "Neon"),
    ("Fox", "Owl", "Anvil", "Garden", "Signal", "Harbor", "Engine", "Lab", "Works", "Forge", "Tree", "Crow", "Moon",
     "Pixel", "Bear", "Cat", "Comet", "Hearth", "River", "Wolf", "Studio", "Arcade", "Collective", "Games"),
)
