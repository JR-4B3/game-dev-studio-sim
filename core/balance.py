"""Tuning numbers, one section per system.

Rebalancing after a new system (an office, a building) should mean changing
numbers in that system's section, then running tools/balance.py to compare the
economy before and after. Any value can also be overridden from a JSON file:
{"market": {"word_of_mouth": 0.4}} replaces just that number.
"""
from dataclasses import dataclass, field, fields, replace


@dataclass(frozen=True)
class StartBalance:
    cash: float = 15_000
    living_costs: float = 2_000  # the Founder's rent and food, monthly
    founder_skills: tuple = (48, 34, 26, 55, 36)  # design, art, audio, code, research
    applicants: int = 3
    contract_offers: int = 4


@dataclass(frozen=True)
class WorkBalance:
    output_per_skill: float = 0.3  # daily work points per skill point
    coordination: tuple = ((5, 1.0), (12, 0.7), (10**9, 0.45))  # (people, weight) bands
    pipeline_bonus: float = 0.15  # weight added to the second and third band
    coordination_bonus: float = 0.25  # weight added to the third band
    hardware_bonus: float = 0.10
    project_reserve: float = 0.5  # share of capacity the project keeps when other work competes
    bug_rate: float = 0.11  # bugs per work point at code skill 0
    bug_floor: float = 0.012
    bug_discovery: float = 0.04  # share of hidden bugs found per production day
    polish_work_per_bug: float = 1.6


@dataclass(frozen=True)
class IdeaBalance:
    shelf_base: int = 3
    shelf_max: int = 8
    weekly_chance: float = 0.06
    founder_bonus: float = 0.03
    lifetime_weeks: tuple = (10, 30)
    fun_mean: float = 48
    fun_spread: float = 14
    known_width_fun: float = 70  # width of the starting fun range at design skill 0
    iteration_gain: float = 0.10  # share of the gap to the ceiling closed per iteration
    fun_ceiling: float = 95
    pivot_spread: float = 12


@dataclass(frozen=True)
class QualityBalance:
    fun_weight: float = 0.55
    craft_weight: float = 0.45
    tools_bonus: float = 3
    bugs_per_point: float = 0.17  # quality lost per bug per 1000 work points
    max_bug_penalty: float = 30
    expectation_weight: float = 0.35  # how hard reputation-driven expectations hit ratings


@dataclass(frozen=True)
class MarketBalance:
    interest_cap: float = 0.3  # share of aware people who could ever want even a perfect game
    interest_midpoint: float = 2.0  # utility at which interest is half the cap
    interest_slope: float = 1.5
    weekly_conversion: float = 0.25  # share of would-be buyers who buy in a given week
    taste_weight: float = 1.6
    quality_weight: float = 0.9
    price_weight: float = 1.1
    content_weight: float = 0.6  # how much more people want bigger games
    yearly_discount: float = 0.3  # average store-sale discount gained per year since release
    lowest_discount: float = 0.3  # games never sell below this share of their price
    greed_weight: float = 2.0
    novelty_weight: float = 0.5
    age_decay: float = 0.6  # utility lost per year since release
    store_visibility: float = 0.00004  # awareness a release gets per visibility point
    store_browsing: float = 0.000004  # weekly awareness from store browsing, for a well-rated game
    word_of_mouth: float = 3.0  # people a buyer tells about a game rated 90
    chart_awareness: float = 0.0015  # weekly awareness for the number one, falls with rank
    forgetting: float = 0.02  # weekly share of non-owners who forget a game
    fan_attention: float = 0.5  # share of fans who notice a new release
    fan_conversion: float = 0.12  # buyers who become fans at a rating of 100
    fan_decay: float = 0.004  # monthly
    marketing_people_per_dollar: float = 4.0
    heat_drift: float = 0.06
    heat_saturation: float = 0.05  # heat lost per recent release in a genre
    refund_base: float = 0.04
    retention: float = 0.86  # monthly share of players who stay, at quality 50
    dlc_attach: float = 0.12
    dlc_price: float = 9.99


@dataclass(frozen=True)
class PeopleBalance:
    salary_base: float = 30_000
    salary_per_skill: float = 110
    hiring_fee_months: float = 0.25
    employer_burden: float = 0.13
    workspace_per_person: float = 350  # monthly desk, software and equipment per employee
    founder_tools: float = 60  # monthly software for a solo founder
    fatigue_per_day: float = 0.45
    rest_per_week: float = 2.0
    vacation_fatigue: float = 30
    burnout_days: int = 14
    xp_per_level: float = 450
    training_cost: float = 600


@dataclass(frozen=True)
class ContractBalance:
    base_work: float = 70
    work_per_difficulty: float = 55
    pay_per_work: float = 12
    pay_per_difficulty: float = 4  # extra pay per work point per difficulty level
    pay_per_trust: float = 0.06
    trust_gain: float = 2
    trust_loss: float = 6


@dataclass(frozen=True)
class FinanceBalance:
    tax_rate: float = 0.2
    overdraft_fee: float = 0.003  # weekly share of negative cash
    bankruptcy_weeks: int = 8
    credit_base: float = 12_000
    credit_per_revenue: float = 0.4
    credit_per_reputation: float = 1_500


@dataclass(frozen=True)
class RivalBalance:
    salary: float = 32_000  # yearly cost per head, all-in, for a tiny studio
    salary_large: float = 85_000  # for a studio of 200 or more
    scope_staff: tuple = (1, 1, 2, 5, 15, 40, 120, 350)  # team size per scope, in SCOPES order
    scope_months: tuple = (1, 5, 10, 16, 24, 30, 40, 50)
    marketing_share: float = 0.12  # launch marketing as a share of the project budget
    founding_chance: float = 0.7  # monthly chance a new studio opens
    hire_months: float = 18  # cash runway that triggers growth
    layoff_months: float = 4
    debt_limit_months: float = 6
    management_drift: float = 0.03


@dataclass(frozen=True)
class Balance:
    start: StartBalance = field(default_factory=StartBalance)
    work: WorkBalance = field(default_factory=WorkBalance)
    ideas: IdeaBalance = field(default_factory=IdeaBalance)
    quality: QualityBalance = field(default_factory=QualityBalance)
    market: MarketBalance = field(default_factory=MarketBalance)
    people: PeopleBalance = field(default_factory=PeopleBalance)
    contracts: ContractBalance = field(default_factory=ContractBalance)
    finance: FinanceBalance = field(default_factory=FinanceBalance)
    rivals: RivalBalance = field(default_factory=RivalBalance)

    def with_overrides(self, overrides):
        sections = {}
        for f in fields(self):
            section = getattr(self, f.name)
            changes = overrides.get(f.name, {})
            unknown = set(changes) - {x.name for x in fields(section)}
            if unknown:
                raise ValueError(f"Unknown balance values in {f.name}: {sorted(unknown)}")
            sections[f.name] = replace(section, **changes)
        return replace(self, **sections)


DEFAULT = Balance()
