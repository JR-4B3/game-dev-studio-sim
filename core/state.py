"""Everything a Campaign remembers. Plain data only: no behaviour, no I/O.

Saves are a JSON dump of these dataclasses (see codec.py), and the frontend
receives views built from them. New systems add fields with defaults so older
saves keep loading.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Range:
    """What the studio believes about a hidden value."""
    low: float
    high: float


@dataclass
class Person:
    id: int
    name: str
    role: str
    design: float
    art: float
    audio: float
    code: float
    research: float
    salary: float  # yearly
    trait: str
    seniority: str = "Mid-level"
    founder: bool = False
    fatigue: float = 10.0
    morale: float = 70.0
    xp: float = 0.0
    career: int = 1
    onboarding_days: int = 0
    vacation_days: int = 0
    burnout_days: int = 0
    training_days: int = 0
    training_skill: str = ""
    hired_day: int = 0


@dataclass
class Finding:
    day: int
    text: str


@dataclass
class Discovery:
    """A new direction an experiment turned up. The player may pivot to it."""
    text: str
    genre: str
    secondary: str
    fun_shift: float  # hidden: how much better or worse the new direction is


@dataclass
class Idea:
    id: int
    title: str
    fantasy: str
    activity: str
    setting: str
    hook: str
    question: str
    genre: str
    secondary: str
    topic: str
    tags: list[str]
    author: str
    origin: str
    created_day: int
    expires_day: int
    # Hidden truth, and what the studio believes about it.
    fun: float
    complexity: float
    appeal: float  # how strongly the pitch speaks to its audiences, -0.3..0.3
    fun_known: Range = field(default_factory=lambda: Range(10, 90))
    complexity_known: Range = field(default_factory=lambda: Range(0.6, 1.8))
    appeal_known: Range = field(default_factory=lambda: Range(-0.3, 0.3))
    franchise: str = ""


@dataclass
class Plan:
    scope: str = "Micro"
    format: str = "Offline solo"
    presentation: str = "Pixel art"
    storefronts: list[str] = field(default_factory=lambda: ["Scratch.io"])
    model: str = "Premium"
    price: float = 4.99
    marketing: str = "Word of mouth"
    announcement: str = "Late reveal"


@dataclass
class Deal:
    publisher: str
    advance: float
    recoup_share: float
    share: float
    recouped: float = 0.0


@dataclass
class Project:
    id: int
    idea: Idea
    stage: str  # concept, design, production, polish
    started_day: int
    findings: list[Finding] = field(default_factory=list)
    discoveries: list[Discovery] = field(default_factory=list)
    activity: str = ""  # key of the running experiment, "iterate", or ""
    activity_work: float = 0.0
    activity_total: float = 0.0
    iterations: int = 0
    pivots: int = 0
    plan: Plan = field(default_factory=Plan)
    work_total: float = 0.0
    work_done: float = 0.0
    craft: float = 0.0  # sum of output weighted by relevant skill
    bugs: float = 0.0  # bugs not yet fixed
    bugs_known: float = 0.0
    polish_done: float = 0.0
    quality_bonus: float = 0.0
    appeal_bonus: float = 0.0
    decisions: list[int] = field(default_factory=list)  # still to come
    decision: Optional[int] = None  # waiting for the player
    awareness: dict[str, float] = field(default_factory=dict)  # pre-launch, per cohort
    deal: Optional[Deal] = None
    pitched: list[str] = field(default_factory=list)
    production_day: int = 0
    costs: float = 0.0
    last_community: dict[str, int] = field(default_factory=dict)


@dataclass
class Update:
    product_id: int
    size: str
    work: float
    done: float = 0.0


@dataclass
class Product:
    """A released game in the shared Market, made by the player or a Rival."""
    id: int
    title: str
    studio_id: int  # 0 is the player's Studio
    studio_name: str
    genre: str
    secondary: str
    topic: str
    scope: str
    format: str
    presentation: str
    model: str
    storefronts: list[str]
    price: float
    quality: float
    review: float  # press score at launch, 0 if nobody reviewed it
    rating: float  # what players say now
    released_day: int
    appeal: float = 0.0
    novelty: float = 0.0
    greed: float = 0.0
    bugs: float = 0.0
    sentiment: float = 60.0
    awareness: dict[str, float] = field(default_factory=dict)
    owners: dict[str, float] = field(default_factory=dict)
    weekly_units: float = 0.0
    units: float = 0.0
    players: float = 0.0  # monthly active players
    revenue: float = 0.0  # what the studio received
    costs: float = 0.0
    sales_history: list[int] = field(default_factory=list)
    support: str = "Active"
    version: str = "1.0"
    dlc_owners: float = 0.0
    franchise: str = ""
    deal: Optional[Deal] = None
    last_community: dict[str, int] = field(default_factory=dict)
    retired: bool = False


@dataclass
class Contract:
    id: int
    title: str
    client: str
    skill: str
    difficulty: int
    work: float
    days: int  # deadline from acceptance
    pay: float
    quality_target: float
    trust_needed: float
    expires_day: int
    done: float = 0.0
    craft: float = 0.0  # sum of output weighted by skill, for the quality check
    days_left: int = 0
    attempts: int = 0


@dataclass
class Loan:
    name: str
    principal: float
    balance: float
    rate: float
    weekly_payment: float
    weeks_left: int


@dataclass
class Commitment:
    """A running promotion or community action."""
    key: str
    kind: str  # promotion or community
    target: int  # product id, or 0 for the current project
    days_left: int
    capacity: float


@dataclass
class Studio:
    name: str
    cash: float
    fans: dict[str, float] = field(default_factory=dict)
    reputation: float = 0.0
    client_trust: float = 0.0
    team: list[Person] = field(default_factory=list)
    applicants: list[Person] = field(default_factory=list)
    ideas: list[Idea] = field(default_factory=list)
    project: Optional[Project] = None
    contract_offers: list[Contract] = field(default_factory=list)
    contracts: list[Contract] = field(default_factory=list)  # first is active
    contract_share: float = 0.5
    completed_contracts: int = 0
    research_done: list[str] = field(default_factory=list)
    research_active: str = ""
    research_work: float = 0.0
    research_queue: list[str] = field(default_factory=list)
    loans: list[Loan] = field(default_factory=list)
    updates: list[Update] = field(default_factory=list)  # first is active
    commitments: list[Commitment] = field(default_factory=list)
    insolvent_days: int = 0
    lifetime_revenue: float = 0.0
    tax_base: float = 0.0  # profit this quarter, losses carried forward
    closed: str = ""  # why the Campaign ended, empty while it runs


@dataclass
class RivalProject:
    title: str
    genre: str
    secondary: str
    topic: str
    scope: str
    format: str
    model: str
    staff: int
    months_left: float
    fun: float
    budget: float
    monthly_cost: float = 0.0  # setup spread over the project, on top of payroll


@dataclass
class Rival:
    id: int
    name: str
    staff: int
    skill: float
    reputation: float
    fans: dict[str, float]
    greed: float
    genres: list[str]
    cash: float
    management: float = 0.7  # how well the studio is run, 0..1
    debt: float = 0.0
    projects: list[RivalProject] = field(default_factory=list)
    revenue_history: list[float] = field(default_factory=list)  # by month
    founded_day: int = 0
    closed_day: int = -1
    owner: int = 0  # rival id that acquired it, 0 if independent
    notes: list[str] = field(default_factory=list)


@dataclass
class Market:
    heat: dict[str, float] = field(default_factory=dict)  # by genre, 1.0 is normal
    recent_releases: dict[str, float] = field(default_factory=dict)  # by genre, decaying count
    confidence: float = 1.0  # consumer spending mood


@dataclass
class Ledger:
    month: str
    opening: float = 0.0  # cash on the first day of the month
    income: dict[str, float] = field(default_factory=dict)
    expenses: dict[str, float] = field(default_factory=dict)
    financing: dict[str, float] = field(default_factory=dict)


@dataclass
class State:
    version: int
    seed: int
    rng: list  # random.Random state
    start: str  # ISO date of day 0
    day: int
    ironman: bool
    next_id: int
    studio: Studio
    rivals: list[Rival]
    products: list[Product]
    market: Market
    ledgers: list[Ledger]  # newest last
    log: list[str]  # newest first
    news: list[str] = field(default_factory=list)  # market news, newest first
