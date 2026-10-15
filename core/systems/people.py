"""The team: hiring, pay, condition, training and how much work people produce."""
from ..content import FIRST_NAMES, LAST_NAMES, ROLES, SENIORITY, TRAITS
from ..game import int_arg, str_arg
from ..state import Person

SKILL_NAMES = ("design", "art", "audio", "code", "research")


def setup(game):
    s = game.s.studio
    skills = game.b.start.founder_skills
    founder = Person(id=game.new_id(), name="You", role="Founder", **dict(zip(SKILL_NAMES, skills)),
                     salary=0, trait="Steady", founder=True)
    s.team.append(founder)
    refresh_applicants(game, game.b.start.applicants)


def make_person(game, role=None, seniority=None):
    rng = game.rng
    role = role or rng.choice(ROLES)
    if seniority is None:
        # Experienced people prefer studios with a track record.
        senior_chance = 0.08 + game.s.studio.reputation / 400
        roll = rng.random()
        seniority = SENIORITY[2] if roll < senior_chance else SENIORITY[0] if roll < senior_chance + 0.45 else SENIORITY[1]
    label, _, offset = seniority
    skills = [max(15, min(95, round(base + offset + rng.gauss(0, 7)))) for base in role["skills"]]
    p = game.b.people
    salary = round((p.salary_base + sum(skills) * p.salary_per_skill) / 1000) * 1000
    return Person(id=game.new_id(), name=f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}", role=role["name"],
                  **dict(zip(SKILL_NAMES, skills)), salary=salary, trait=rng.choice(sorted(TRAITS)),
                  seniority=label)


def refresh_applicants(game, count=None):
    s = game.s.studio
    if count is None:
        count = min(10, 3 + len(s.team) // 2 + int(s.reputation / 25))
    s.applicants = [make_person(game) for _ in range(count)]


def available(person):
    return not (person.vacation_days or person.burnout_days or person.training_days)


def condition(person):
    """Output multiplier from morale, fatigue, onboarding and trait."""
    morale = max(0.35, min(1.15, 0.55 + person.morale / 150))
    fatigue = 1.0 if person.fatigue < 50 else max(0.5, 1 - (person.fatigue - 50) / 100)
    onboarding = 1.0 if not person.onboarding_days else 0.4 + 0.6 * (1 - person.onboarding_days / 28)
    return morale * fatigue * onboarding * TRAITS[person.trait]["output"]


def skill(person, weights):
    """Weighted skill for (design, art, audio, code) weights, or "research"."""
    if weights == "research":
        return person.research * TRAITS[person.trait].get("research", 1.0)
    total = sum(weights) or 1
    return (person.design * weights[0] + person.art * weights[1] + person.audio * weights[2] + person.code * weights[3]) / total


def coordination(game, count):
    """Effective head count once communication overhead is paid."""
    w = game.b.work
    effective, left, start = 0.0, count, 0
    for index, (size, weight) in enumerate(w.coordination):
        if index >= 1 and game.has("production_pipeline"):
            weight += w.pipeline_bonus
        if index >= 2 and game.has("advanced_coordination"):
            weight += w.coordination_bonus
        take = min(left, size)
        effective += take * min(1.0, weight)
        left -= take
        if left <= 0:
            break
    return effective / max(1, count)


def team_output(game, weights):
    """Work points per day the whole available team produces, and their average skill."""
    people = [p for p in game.s.studio.team if available(p)]
    if not people:
        return 0.0, 0.0
    contributions = [(skill(p, weights), condition(p)) for p in people]
    raw = sum(sk * cond for sk, cond in contributions)
    output = raw * game.b.work.output_per_skill * coordination(game, len(people))
    if game.has("hardware"):
        output *= 1 + game.b.work.hardware_bonus
    average_skill = sum(sk for sk, _ in contributions) / len(contributions)
    return output, average_skill


def team_mean(game, attribute):
    people = [p for p in game.s.studio.team if available(p)] or game.s.studio.team
    return sum(getattr(p, attribute) for p in people) / len(people)


def add_experience(game, main_skill, workload):
    """Called by the work system once per workday with the day's busiest skill."""
    rate = 1.0 + (0.25 if game.has("mentorship") else 0) + (0.35 if game.has("academy") else 0)
    rate += sum(TRAITS[p.trait].get("team_xp", 0) for p in game.s.studio.team)
    for person in game.s.studio.team:
        if not available(person):
            continue
        person.xp += 2.0 * workload * rate
        if person.xp >= game.b.people.xp_per_level and main_skill:
            person.xp -= game.b.people.xp_per_level
            old = getattr(person, main_skill)
            setattr(person, main_skill, min(99, old + 1))
            total = sum(getattr(person, k) for k in SKILL_NAMES)
            person.career = max(1, min(5, 1 + int((total - 200) / 60)))
            if not person.founder:
                person.salary += 300


def tire(game, workload):
    """Called by the work system each workday with the share of the day that was busy."""
    p = game.b.people
    for person in game.s.studio.team:
        if not available(person):
            continue
        rate = p.fatigue_per_day * max(0.3, workload) * TRAITS[person.trait]["fatigue"]
        if game.has("health"):
            rate *= 0.8
        person.fatigue = min(100, person.fatigue + rate)
        if person.fatigue >= 100:
            person.burnout_days = p.burnout_days
            person.fatigue = 70
            person.morale = max(0, person.morale - 15)
            game.log(f"{person.name} burned out and is off for two weeks.")


def on_day(game):
    s = game.s.studio
    for person in s.team:
        for counter in ("vacation_days", "burnout_days", "onboarding_days"):
            if getattr(person, counter):
                setattr(person, counter, getattr(person, counter) - 1)
        if person.training_days:
            person.training_days -= 1
            if not person.training_days and person.training_skill:
                gain = 6 if game.has("academy") else 4
                setattr(person, person.training_skill, min(99, getattr(person, person.training_skill) + gain))
                game.log(f"{person.name} finished training: {person.training_skill} +{gain}.")
                person.training_skill = ""


def on_week(game):
    p = game.b.people
    for person in game.s.studio.team:
        if available(person):
            person.fatigue = max(0, person.fatigue - p.rest_per_week)
        if game.has("auto_leave") and available(person) and person.fatigue >= 75:
            start_vacation(game, person, automatic=True)


def on_month(game):
    p = game.b.people
    s = game.s.studio
    staff = [x for x in s.team if not x.founder]
    payroll = sum(x.salary for x in staff) / 12
    if payroll:
        game.spend("Salaries", payroll * (1 + p.employer_burden))
    game.spend("Workspace & tools", p.founder_tools + p.workspace_per_person * len(staff))
    for person in s.team:
        person.morale += (65 - person.morale) * 0.15 - max(0, person.fatigue - 60) * 0.1
        if s.cash < 0 and not person.founder:
            person.morale -= 6
        person.morale = max(0, min(100, person.morale))
    for person in list(staff):
        if person.morale < 15 and game.rng.random() < 0.4:
            s.team.remove(person)
            game.log(f"{person.name} resigned. Morale had been too low for too long.")
    refresh_applicants(game)


def start_vacation(game, person, automatic=False):
    if not available(person):
        raise ValueError(f"{person.name} is not available.")
    person.vacation_days = 7
    relief = game.b.people.vacation_fatigue + (8 if game.has("paid_leave") else 0)
    person.fatigue = max(0, person.fatigue - relief)
    person.morale = min(100, person.morale + (6 if game.has("paid_leave") else 3))
    game.log(f"{person.name} {'was sent' if automatic else 'went'} on a week of vacation.")


def find(people, person_id):
    for person in people:
        if person.id == person_id:
            return person
    raise ValueError("That person is not here anymore.")


def hire(game, data):
    s = game.s.studio
    person = find(s.applicants, int_arg(data, "id"))
    fee = max(500, person.salary / 12 * game.b.people.hiring_fee_months)
    if s.cash < fee + person.salary / 12:
        raise ValueError(f"You can't cover the hiring fee and a first month of pay for {person.name}.")
    game.spend("Hiring", fee)
    s.applicants.remove(person)
    person.onboarding_days = 28
    person.hired_day = game.s.day
    s.team.append(person)
    game.log(f"Hired {person.name} ({person.seniority} {person.role}) for ${person.salary / 12:,.0f} a month.")


def fire(game, data):
    s = game.s.studio
    person = find(s.team, int_arg(data, "id"))
    if person.founder:
        raise ValueError("You can't fire yourself.")
    game.spend("Severance", person.salary / 26)
    s.team.remove(person)
    for other in s.team:
        other.morale = max(0, other.morale - 5)
    game.log(f"Let {person.name} go with two weeks of severance. The team is shaken.")


def vacation(game, data):
    start_vacation(game, find(game.s.studio.team, int_arg(data, "id")))


def train(game, data):
    s = game.s.studio
    person = find(s.team, int_arg(data, "id"))
    skill_name = str_arg(data, "skill", SKILL_NAMES)
    if not available(person):
        raise ValueError(f"{person.name} is not available.")
    cost = round((game.b.people.training_cost + getattr(person, skill_name) * 30) / 50) * 50
    if s.cash < cost:
        raise ValueError(f"Training costs ${cost:,.0f}.")
    game.spend("Training", cost)
    person.training_days = 14 if game.has("academy") else 21 if game.has("structured_training") else 28
    person.training_skill = skill_name
    game.log(f"{person.name} started a {skill_name} course for ${cost:,.0f}.")


COMMANDS = {"hire": hire, "fire": fire, "vacation": vacation, "train": train}


def person_view(game, person):
    status = ("Vacation" if person.vacation_days else "Burnout" if person.burnout_days else
              "Training" if person.training_days else "Onboarding" if person.onboarding_days else "Available")
    days = person.vacation_days or person.burnout_days or person.training_days or person.onboarding_days
    return {"id": person.id, "name": person.name, "role": person.role, "seniority": person.seniority,
            "founder": person.founder, "trait": person.trait, "monthly_salary": person.salary / 12,
            "design": round(person.design), "art": round(person.art), "audio": round(person.audio),
            "code": round(person.code), "research": round(person.research), "fatigue": round(person.fatigue),
            "morale": round(person.morale), "career": person.career, "status": status, "status_days": days,
            "training": person.training_skill}


def view(game):
    s = game.s.studio
    return {"team": [person_view(game, p) for p in s.team],
            "applicants": [{**person_view(game, p), "hiring_fee": max(500, p.salary / 12 * game.b.people.hiring_fee_months)}
                           for p in s.applicants]}
