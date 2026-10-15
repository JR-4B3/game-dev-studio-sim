"""Work-for-hire. Clients pay for delivered work; Client trust grows with
every job done well and opens bigger, better-paid offers."""
import math

from ..content import CONTRACT_CLIENTS, CONTRACT_JOBS
from ..game import int_arg
from ..state import Contract
from . import ideas as idea_rules

SKILL_WEIGHTS = {"design": (1, 0, 0, 0), "art": (0, 1, 0, 0), "audio": (0, 0, 1, 0), "code": (0, 0, 0, 1)}


def setup(game):
    s = game.s.studio
    s.contract_offers = [offer(game) for _ in range(game.b.start.contract_offers)]


def offer(game):
    rng, b, s = game.rng, game.b.contracts, game.s.studio
    reach = min(5, 1 + int(s.client_trust / 15) + (1 if rng.random() < 0.25 else 0))
    difficulty = rng.randint(1, reach)
    job, skill = rng.choice(CONTRACT_JOBS)
    work = b.base_work + difficulty * b.work_per_difficulty + rng.randint(0, 45)
    pay = work * (b.pay_per_work + difficulty * b.pay_per_difficulty + s.client_trust * b.pay_per_trust)
    days = math.ceil(work / 35) * 7 + 14 + difficulty * 3
    return Contract(id=game.new_id(), title=job, client=rng.choice(CONTRACT_CLIENTS), skill=skill,
                    difficulty=difficulty, work=work, days=days, pay=round(pay / 50) * 50,
                    quality_target=32 + difficulty * 9, trust_needed=(difficulty - 1) * 12,
                    expires_day=game.s.day + rng.randint(14, 45))


def on_month(game):
    s = game.s.studio
    s.contract_offers = [c for c in s.contract_offers if c.expires_day > game.s.day]
    target = min(8, game.b.start.contract_offers + int(s.client_trust / 20))
    while len(s.contract_offers) < target:
        s.contract_offers.append(offer(game))


def on_day(game):
    s = game.s.studio
    s.contract_offers = [c for c in s.contract_offers if c.expires_day > game.s.day]
    if not s.contracts:
        return
    active = s.contracts[0]
    active.days_left -= 1
    if active.days_left <= 0:
        s.contracts.pop(0)
        s.client_trust = max(0, s.client_trust - game.b.contracts.trust_loss)
        game.log(f"Missed the deadline for {active.client}. No pay, and word gets around.")
        start_next(game)


def start_next(game):
    s = game.s.studio
    if s.contracts:
        s.contracts[0].days_left = s.contracts[0].days


def skill_weights(game):
    return SKILL_WEIGHTS[game.s.studio.contracts[0].skill]


def wants_work(game):
    return bool(game.s.studio.contracts)


def work(game, output, average_skill):
    s, b = game.s.studio, game.b.contracts
    contract = s.contracts[0]
    contract.done += output
    contract.craft += output * average_skill
    if contract.done < contract.work:
        return
    quality = contract.craft / max(1, contract.done)
    if quality < contract.quality_target and contract.attempts == 0:
        contract.attempts += 1
        contract.work *= 1.2
        game.log(f"{contract.client} sent the work back: it is not good enough yet. Reworking.")
        return
    s.contracts.pop(0)
    pay = contract.pay * (1 if quality >= contract.quality_target else 0.7)
    game.earn("Contracts", pay)
    s.client_trust = min(100, s.client_trust + b.trust_gain * (1 if quality >= contract.quality_target else 0.3)
                         + contract.difficulty * 0.5)
    s.completed_contracts += 1
    game.log(f"Delivered \"{contract.title}\" to {contract.client} for ${pay:,.0f}.")
    if game.rng.random() < 0.2:
        idea_rules.inspire(game, "contract")
    start_next(game)


def accept(game, data):
    s = game.s.studio
    contract_id = int_arg(data, "id")
    contract = next((c for c in s.contract_offers if c.id == contract_id), None)
    if not contract:
        raise ValueError("That offer is gone.")
    if len(s.contracts) >= 3:
        raise ValueError("You already have three jobs lined up.")
    if contract.trust_needed > s.client_trust + 10:
        raise ValueError(f"{contract.client} wants a contractor with more of a track record.")
    s.contract_offers.remove(contract)
    s.contracts.append(contract)
    if len(s.contracts) == 1:
        start_next(game)
    game.log(f"Took on \"{contract.title}\" for {contract.client}.")


def share(game, data):
    value = data.get("value")
    if value not in (0.25, 0.5, 0.75):
        raise ValueError("Invalid share.")
    game.s.studio.contract_share = value


COMMANDS = {"accept_contract": accept, "contract_share": share}


def contract_view(c):
    return {"id": c.id, "title": c.title, "client": c.client, "skill": c.skill, "difficulty": c.difficulty,
            "work": round(c.work), "done": round(c.done), "weeks": round(c.days / 7, 1), "pay": c.pay,
            "quality_target": c.quality_target, "trust_needed": c.trust_needed,
            "days_left": c.days_left, "expires_in": None}


def estimate(game, contract):
    """Weeks the team would need at the current contract share, and the quality it would deliver."""
    from .people import team_output
    output, skill = team_output(game, SKILL_WEIGHTS[contract.skill])
    share = game.s.studio.contract_share if game.s.studio.project else 1.0
    weekly = output * 5 * share
    return (round(contract.work / weekly, 1) if weekly else None), round(skill)


def view(game):
    s = game.s.studio
    offers = []
    for c in s.contract_offers:
        row = contract_view(c)
        row["estimate_weeks"], row["your_quality"] = estimate(game, c)
        row["expires_in"] = max(0, c.expires_day - game.s.day)
        row["locked"] = c.trust_needed > s.client_trust + 10
        offers.append(row)
    return {"contract_offers": offers, "contracts": [contract_view(c) for c in s.contracts],
            "client_trust": round(s.client_trust, 1), "contract_share": s.contract_share,
            "completed_contracts": s.completed_contracts}
