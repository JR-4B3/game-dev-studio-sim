"""Original games, from Idea to release.

Stages:
  concept     Run experiments to learn what the Idea really is, iterate on the
              core loop to make it more fun, or pivot to a direction an
              experiment discovered. Shelve it if the evidence says no.
  design      Choose scope, format, look, stores, business model, price and
              marketing. Pitch publishers. Commit to pay setup costs.
  production  The team builds it. Bugs pile up, milestones force decisions.
  polish      Fix bugs for as long as you like, then release.
"""
from ..content import (ANNOUNCEMENT, ANNOUNCEMENTS, BUSINESS_MODEL, BUSINESS_MODELS, EXPERIMENT, EXPERIMENTS,
                       FORMAT, FORMATS, GENRE_SKILLS, ITERATION, LAUNCH, LAUNCH_MARKETING, PRESENTATION,
                       PRESENTATIONS, PRICE_POINTS, PRODUCTION_DECISIONS, PUBLISHER, PUBLISHERS, SCOPE, SCOPES,
                       STOREFRONT, STOREFRONTS, TRAITS)
from ..idea_text import ACTIVITIES
from ..game import int_arg, str_arg
from ..state import Deal, Discovery, Finding, Plan, Project
from . import ideas as idea_rules
from . import market
from .people import available, team_mean, team_output

SKILL_INDEX = {"design": 0, "art": 1, "audio": 2, "code": 3}


def project_or_fail(game, *stages):
    project = game.s.studio.project
    if not project:
        raise ValueError("There is no game in development.")
    if stages and project.stage not in stages:
        raise ValueError(f"That is not possible during {project.stage}.")
    return project


def find_note(project, game, text):
    project.findings.append(Finding(day=game.s.day, text=text))


# --- Work ---------------------------------------------------------------------

def skill_weights(project):
    """Which skills the current project work needs, as (design, art, audio, code)."""
    if project.stage == "concept":
        key = project.activity
        skill = ITERATION["skill"] if key == "iterate" else EXPERIMENT[key]["skill"]
        if skill == "research":
            return "research"
        weights = [0, 0, 0, 0]
        weights[SKILL_INDEX[skill]] = 1
        return tuple(weights)
    genre = GENRE_SKILLS[project.idea.genre]
    look = PRESENTATION[project.plan.presentation]["skills"]
    return tuple(0.6 * g + 0.4 * p for g, p in zip(genre, look))


def wants_work(game):
    project = game.s.studio.project
    if not project:
        return False
    if project.stage == "concept":
        return bool(project.activity)
    return project.stage in ("production", "polish") and project.decision is None


def work(game, output, average_skill):
    project = game.s.studio.project
    if project.stage == "concept":
        project.activity_work += output
        if project.activity_work >= project.activity_total:
            finish_activity(game, project, average_skill)
    elif project.stage == "production":
        produce(game, project, output, average_skill)
    elif project.stage == "polish":
        polish(game, project, output)


def skill_factor(average_skill):
    return 0.6 + average_skill / 125


def finish_activity(game, project, average_skill):
    key, idea, rng = project.activity, project.idea, game.rng
    project.activity, project.activity_work, project.activity_total = "", 0.0, 0.0
    factor = skill_factor(average_skill)
    if key == "iterate":
        b = game.b.ideas
        gain = (b.fun_ceiling - idea.fun) * b.iteration_gain * factor / (1 + project.iterations * 0.35)
        gain = max(-2.0, gain + rng.gauss(0, 1.5))
        idea.fun = round(min(b.fun_ceiling, idea.fun + gain), 1)
        shift = gain + rng.gauss(0, 2)
        known = idea.fun_known
        known.low, known.high = max(0, known.low + shift), min(100, known.high + shift)
        known.low, known.high = min(known.low, idea.fun), max(known.high, idea.fun)
        idea.fun_known = idea_rules.narrow(rng, known, idea.fun, 0.1, 0, 100)
        project.iterations += 1
        verdict = "The loop feels tighter." if gain > 3 else "Small gains this time." if gain > 0.5 else "Nothing moved. The loop may be as good as it gets."
        find_note(project, game, f"Iteration {project.iterations}: {verdict} Fun now looks like "
                                 f"{idea.fun_known.low:.0f}–{idea.fun_known.high:.0f}.")
        return
    experiment = EXPERIMENT[key]
    reveals = experiment["reveals"]
    if "fun" in reveals:
        idea.fun_known = idea_rules.narrow(rng, idea.fun_known, idea.fun, min(0.9, reveals["fun"] * factor), 0, 100)
    if "complexity" in reveals:
        idea.complexity_known = idea_rules.narrow(rng, idea.complexity_known, idea.complexity,
                                                  min(0.9, reveals["complexity"] * factor), 0.5, 2.0)
    if "appeal" in reveals:
        strength = reveals["appeal"] * factor * (1.25 if game.has("market_research") else 1)
        idea.appeal_known = idea_rules.narrow(rng, idea.appeal_known, idea.appeal, min(0.9, strength), -0.4, 0.4)
    find_note(project, game, f"{experiment['name']}: {experiment_reading(key, idea)}")
    if rng.random() < experiment["discovery"] * factor:
        discovery = discover(game, idea)
        if discovery:
            project.discoveries.append(discovery)
            find_note(project, game, f"Discovery: {discovery.text}")


def experiment_reading(key, idea):
    fun, complexity, appeal = idea.fun, idea.complexity, idea.appeal
    f, c, a = idea.fun_known, idea.complexity_known, idea.appeal_known
    if key in ("paper", "playable", "hook"):
        mood = ("Testers did not want to stop." if fun >= 65 else "People smiled, then drifted off." if fun >= 45
                else "Sessions died after ten minutes.")
        return f"{mood} Fun now looks like {f.low:.0f}–{f.high:.0f}."
    if key == "spike":
        mood = ("Harder than it looks." if complexity >= 1.3 else "Mostly standard work." if complexity >= 0.9
                else "Simpler than feared.")
        return f"{mood} Build effort looks like {c.low:.2f}–{c.high:.2f}× normal."
    mood = ("Players asked when they can buy it." if appeal >= 0.12 else "Polite interest." if appeal >= -0.05
            else "The pitch did not land.")
    return f"{mood} Audience appeal looks like {a.low * 100:+.0f} to {a.high * 100:+.0f}."


def discover(game, idea):
    rng = game.rng
    if rng.random() < 0.5 and idea.secondary != idea.genre:
        genre, secondary = idea.secondary, idea.genre
        text = f"Testers kept coming back to the {genre.lower()} side of it. It could lead."
    else:
        options = [a for a in ACTIVITIES if set(a[3]) & set(idea.tags) and a[1] != idea.genre]
        if not options:
            return None
        activity, genre, secondary, _ = rng.choice(options)
        text = f"Someone tried to {activity} inside the prototype, and it worked. It could become a {genre.lower()}."
    shift = rng.gauss(3, game.b.ideas.pivot_spread)
    hint = shift + rng.gauss(0, 6)
    text += " The room was excited." if hint > 6 else " Opinions are split." if hint > -4 else " Most of the team is skeptical."
    return Discovery(text=text, genre=genre, secondary=secondary, fun_shift=round(shift, 1))


def produce(game, project, output, average_skill):
    b = game.b.work
    trait_craft = sum(TRAITS[p.trait].get("craft", 0) for p in game.s.studio.team if available(p))
    project.work_done += output
    project.craft += output * min(100, average_skill + trait_craft / max(1, len(game.s.studio.team)))
    people = [p for p in game.s.studio.team if available(p)] or game.s.studio.team
    trait_bugs = sum(TRAITS[p.trait]["bugs"] for p in people) / len(people)
    rate = max(b.bug_floor, b.bug_rate - team_mean(game, "code") / 900) * trait_bugs
    rate *= 1 + 0.05 * max(0, len(people) - 1) ** 0.5  # more hands, more seams
    if game.has("qa"):
        rate *= 0.75
    project.bugs += output * rate
    discovery = b.bug_discovery * (1.25 if game.has("qa") else 1)
    project.bugs_known += (project.bugs - project.bugs_known) * discovery
    progress = project.work_done / max(1, project.work_total)
    if project.decisions and progress >= PRODUCTION_DECISIONS[project.decisions[0]]["at"]:
        project.decision = project.decisions.pop(0)
        game.log(f"{project.idea.title}: {PRODUCTION_DECISIONS[project.decision]['title']}. A decision is needed.")
    if project.work_done >= project.work_total:
        project.stage = "polish"
        project.bugs_known += (project.bugs - project.bugs_known) * 0.3
        game.log(f"{project.idea.title} is content complete. Polish as long as you like, then release.")


def polish(game, project, output):
    fixes = output / game.b.work.polish_work_per_bug
    fixed = min(project.bugs_known, fixes)
    project.bugs_known -= fixed
    project.bugs -= fixed
    project.bugs_known += (project.bugs - project.bugs_known) * (0.10 if game.has("qa") else 0.07)
    project.polish_done += output


# --- Weekly ----------------------------------------------------------------------

def on_week(game):
    project = game.s.studio.project
    if not project or project.stage not in ("production", "polish"):
        return
    announcement = ANNOUNCEMENT[project.plan.announcement]
    s = game.s.studio
    if announcement["weekly_awareness"]:
        people = announcement["weekly_awareness"] * (120 + sum(s.fans.values()) * 0.01 + s.reputation * 25)
        market.add_awareness(game, project.awareness, people, project.idea.genre, project.plan.format)
    for cohort in project.awareness:
        project.awareness[cohort] *= 1 - announcement["decay"]


# --- Commands -----------------------------------------------------------------

def explore(game, data):
    s = game.s.studio
    if s.project:
        raise ValueError("Finish, shelve or cancel the current game first.")
    idea_id = int_arg(data, "id")
    idea = next((i for i in s.ideas if i.id == idea_id), None)
    if not idea:
        raise ValueError("That idea is gone.")
    s.ideas.remove(idea)
    plan = Plan(storefronts=["Steem"], price=SCOPE["Micro"]["price"])
    s.project = Project(id=game.new_id(), idea=idea, stage="concept", started_day=game.s.day, plan=plan)
    whose = "your own idea" if idea.author == "You" else f"{idea.author}'s idea"
    find_note(s.project, game, f"Picked up {whose}. Open question: {idea.question}")
    game.log(f"Started exploring \"{idea.title}\".")


def experiment(game, data):
    project = project_or_fail(game, "concept")
    if project.activity:
        raise ValueError("The team is already busy with an experiment.")
    key = str_arg(data, "key", EXPERIMENT)
    rule = EXPERIMENT[key]
    if rule.get("needs_hook") and not project.idea.hook:
        raise ValueError("This idea has no unusual hook to explore.")
    project.activity = key
    project.activity_total = rule["work"] * project.idea.complexity ** 0.5
    project.activity_work = 0.0


def iterate(game, data):
    project = project_or_fail(game, "concept")
    if project.activity:
        raise ValueError("The team is already busy with an experiment.")
    project.activity = "iterate"
    project.activity_total = ITERATION["work"] * project.idea.complexity ** 0.5
    project.activity_work = 0.0


def pivot(game, data):
    project = project_or_fail(game, "concept")
    index = int_arg(data, "index", 0, len(project.discoveries) - 1)
    discovery = project.discoveries.pop(index)
    idea, rng = project.idea, game.rng
    old = idea.genre
    idea.genre, idea.secondary = discovery.genre, discovery.secondary
    idea.fun = round(max(10, min(game.b.ideas.fun_ceiling, idea.fun + discovery.fun_shift)), 1)
    width = max(30.0, (idea.fun_known.high - idea.fun_known.low) * 1.5)
    idea.fun_known = idea_rules.known_range(rng, idea.fun, width, 0, 100)
    idea.complexity = round(max(0.6, min(1.9, idea.complexity * rng.uniform(0.9, 1.15))), 2)
    idea.complexity_known = idea_rules.known_range(rng, idea.complexity, 0.7, 0.5, 2.0)
    idea.appeal = round(max(-0.3, min(0.3, idea_rules.appeal_of(idea.genre, idea.topic, idea.hook) + rng.gauss(0, 0.07))), 3)
    idea.appeal_known = idea_rules.known_range(rng, idea.appeal, 0.45, -0.4, 0.4)
    project.pivots += 1
    project.discoveries.clear()
    find_note(project, game, f"Pivoted from {old.lower()} to {idea.genre.lower()}. Much of what we knew is uncertain again.")
    game.log(f"\"{idea.title}\" pivots to {idea.genre}.")


def shelve(game, data):
    s = game.s.studio
    project = project_or_fail(game, "concept", "design")
    idea = project.idea
    idea.expires_day = game.s.day + 26 * 7
    s.ideas.append(idea)
    s.project = None
    game.log(f"Shelved \"{idea.title}\". What you learned stays with the idea.")


def cancel(game, data):
    s = game.s.studio
    project = project_or_fail(game, "production", "polish")
    if project.deal:
        game.finance("Publisher refund", -project.deal.advance * 1.05)
    s.project = None
    for person in s.team:
        person.morale = max(0, person.morale - 8)
    game.log(f"Cancelled \"{project.idea.title}\". The team takes it hard.")


def to_design(game, data):
    project = project_or_fail(game, "concept")
    if project.activity:
        raise ValueError("Wait for the running experiment to finish.")
    project.stage = "design"


def to_concept(game, data):
    project = project_or_fail(game, "design")
    if project.deal:
        raise ValueError("A publisher has signed this design. Drop the deal first.")
    project.stage = "concept"


def plan_locks(game, project):
    """Why each plan option can't be chosen right now."""
    locks = {}
    for row in FORMATS + BUSINESS_MODELS + STOREFRONTS:
        if not game.has(row["research"]):
            from ..content import RESEARCH_NODE
            locks[row["name"]] = f"Needs {RESEARCH_NODE[row['research']]['name']}"
    return locks


def set_plan(game, data):
    project = project_or_fail(game, "design")
    plan = project.plan
    field = str_arg(data, "field", ("scope", "format", "presentation", "storefront", "model", "price", "marketing", "announcement"))
    value = data.get("value")
    lock = plan_locks(game, project).get(value)
    if lock:
        raise ValueError(lock)
    if project.deal and field in ("scope", "format", "model"):
        raise ValueError(f"{project.deal.publisher} signed off on this plan. Turn the deal down before changing it.")
    if field == "scope":
        plan.scope = str_arg(data, "value", SCOPE)
        if not BUSINESS_MODEL[plan.model]["free"]:
            plan.price = SCOPE[plan.scope]["price"]
    elif field == "format":
        plan.format = str_arg(data, "value", FORMAT)
    elif field == "presentation":
        plan.presentation = str_arg(data, "value", PRESENTATION)
    elif field == "storefront":
        name = str_arg(data, "value", STOREFRONT)
        if name in plan.storefronts:
            if len(plan.storefronts) == 1:
                raise ValueError("A game needs at least one storefront.")
            plan.storefronts.remove(name)
        else:
            plan.storefronts.append(name)
    elif field == "model":
        plan.model = str_arg(data, "value", BUSINESS_MODEL)
        plan.price = 0.0 if BUSINESS_MODEL[plan.model]["free"] else SCOPE[plan.scope]["price"]
    elif field == "price":
        if BUSINESS_MODEL[plan.model]["free"]:
            raise ValueError("This business model is free to download.")
        if value not in PRICE_POINTS:
            raise ValueError("Invalid price.")
        plan.price = float(value)
    elif field == "marketing":
        plan.marketing = str_arg(data, "value", LAUNCH)
    elif field == "announcement":
        plan.announcement = str_arg(data, "value", ANNOUNCEMENT)


def setup_cost(plan):
    return (SCOPE[plan.scope]["setup"] + FORMAT[plan.format]["setup"] + BUSINESS_MODEL[plan.model]["setup"],
            sum(STOREFRONT[name]["fee"] for name in plan.storefronts))


def work_multiplier(plan):
    return FORMAT[plan.format]["work"] * PRESENTATION[plan.presentation]["work"] * BUSINESS_MODEL[plan.model]["work"]


def forecast(game, project):
    """What the studio can predict about the plan, as ranges."""
    plan, idea = project.plan, project.idea
    output, average_skill = team_output(game, skill_weights_for_plan(project))
    weekly = max(1.0, output * 5 * 0.85)
    base_work = SCOPE[plan.scope]["work"] * work_multiplier(plan)
    work_low, work_high = base_work * idea.complexity_known.low, base_work * idea.complexity_known.high
    weeks = (work_low / weekly, work_high / weekly * 1.08)
    q = game.b.quality
    tools = q.tools_bonus if game.has("tools") else 0
    quality = (idea.fun_known.low * q.fun_weight + average_skill * q.craft_weight + tools - 6,
               idea.fun_known.high * q.fun_weight + average_skill * q.craft_weight + tools + 2)
    setup, fees = setup_cost(plan)
    monthly = monthly_team_cost(game)
    return {"weeks": [round(weeks[0]), round(weeks[1])], "work": [round(work_low), round(work_high)],
            "quality": [max(5, round(quality[0])), min(99, round(quality[1]))], "setup": setup, "fees": fees,
            "marketing": LAUNCH[plan.marketing]["cost"],
            "budget": [round(setup + fees + monthly * weeks[0] / 4.33), round(setup + fees + monthly * weeks[1] / 4.33)]}


def skill_weights_for_plan(project):
    genre = GENRE_SKILLS[project.idea.genre]
    look = PRESENTATION[project.plan.presentation]["skills"]
    return tuple(0.6 * g + 0.4 * p for g, p in zip(genre, look))


def monthly_team_cost(game):
    s = game.s.studio
    staff = [p for p in s.team if not p.founder]
    p = game.b.people
    return (sum(x.salary for x in staff) / 12 * (1 + p.employer_burden) + p.workspace_per_person * len(staff)
            + game.b.start.living_costs + p.founder_tools)


def pitch(game, data):
    project = project_or_fail(game, "design")
    name = str_arg(data, "publisher", PUBLISHER)
    if name in project.pitched:
        raise ValueError(f"{name} already heard this pitch.")
    if project.deal:
        raise ValueError("This game already has a publisher.")
    project.pitched.append(name)
    publisher, idea, s = PUBLISHER[name], project.idea, game.s.studio
    evidence = 1 - (idea.fun_known.high - idea.fun_known.low) / 80
    middle = (idea.fun_known.low + idea.fun_known.high) / 2
    _, average_skill = team_output(game, skill_weights_for_plan(project))
    score = middle * 0.45 + average_skill * 0.2 + s.reputation * 0.45 + evidence * 12 + game.rng.gauss(0, 7)
    score -= max(0, list(SCOPE).index(project.plan.scope) - 2) * 4  # big asks need a bigger track record
    if score < publisher["bar"]:
        game.log(f"{name} passed on \"{idea.title}\". "
                 + ("They want more proof the game is fun." if evidence < 0.5 else "They want a studio with a track record."))
        return
    budget = forecast(game, project)["budget"]
    advance = round(sum(budget) / 2 * publisher["advance"] / 1000) * 1000
    project.deal = Deal(publisher=name, advance=advance, recoup_share=publisher["recoup_share"], share=publisher["share"])
    game.log(f"{name} offers ${advance:,.0f}. They keep {publisher['recoup_share']:.0%} of sales until it is paid back, "
             f"then {publisher['share']:.0%}. The deal is signed when you commit.")


def drop_deal(game, data):
    project = project_or_fail(game, "design")
    if not project.deal:
        raise ValueError("There is no publisher deal.")
    game.log(f"Turned down {project.deal.publisher}.")
    project.deal = None


def commit(game, data):
    project = project_or_fail(game, "design")
    plan, s = project.plan, game.s.studio
    for name in [plan.format, plan.model] + plan.storefronts:
        lock = plan_locks(game, project).get(name)
        if lock:
            raise ValueError(lock)
    setup, fees = setup_cost(plan)
    advance = project.deal.advance if project.deal else 0
    if s.cash + advance < setup + fees:
        raise ValueError(f"Setup and store fees cost ${setup + fees:,.0f}. You have ${s.cash:,.0f}.")
    if project.deal:
        game.finance("Publisher advance", advance)
    if setup:
        game.spend("Production setup", setup)
    if fees:
        game.spend("Storefront fees", fees)
    project.costs += setup + fees
    project.work_total = SCOPE[plan.scope]["work"] * project.idea.complexity * work_multiplier(plan)
    count = SCOPE[plan.scope]["decisions"]
    project.decisions = sorted(game.rng.sample(range(len(PRODUCTION_DECISIONS)), count))
    project.stage = "production"
    project.production_day = game.s.day
    game.log(f"Production started on \"{project.idea.title}\" ({plan.scope}, {plan.presentation}).")


def decide(game, data):
    project = project_or_fail(game, "production", "polish")
    if project.decision is None:
        raise ValueError("No decision is waiting.")
    rule = PRODUCTION_DECISIONS[project.decision]
    option = rule["options"][int_arg(data, "index", 0, len(rule["options"]) - 1)]
    remaining = max(0, project.work_total - project.work_done)
    project.work_total = project.work_done + remaining * option["work"]
    project.quality_bonus += option.get("quality", 0)
    project.appeal_bonus += option.get("appeal", 0)
    if option.get("bugs"):
        project.bugs += max(5, project.bugs) * option["bugs"]
    if option.get("bug_fix"):
        project.bugs *= 1 - option["bug_fix"]
        project.bugs_known = min(project.bugs_known, project.bugs)
    for person in game.s.studio.team:
        person.fatigue = min(100, person.fatigue + option.get("fatigue", 0))
    project.decision = None
    find_note(project, game, f"{rule['title']}: {option['name']}.")
    game.log(f"{rule['title']}: {option['name']}.")


def release(game, data):
    s = game.s.studio
    project = project_or_fail(game, "polish")
    if project.decision is not None:
        raise ValueError("Make the waiting decision first.")
    plan = project.plan
    marketing = LAUNCH[plan.marketing]["cost"]
    if marketing:
        if s.cash < marketing:
            raise ValueError(f"The launch marketing costs ${marketing:,.0f}. Choose a smaller budget or wait.")
        game.spend("Marketing", marketing)
        project.costs += marketing
    q = game.b.quality
    craft = project.craft / max(1, project.work_done)
    quality = market.release_quality(game, project.idea.fun, craft, project.bugs, project.work_total,
                                     project.quality_bonus + (q.tools_bonus if game.has("tools") else 0))
    product = market.launch(
        game, studio_id=0, studio_name=s.name, title=project.idea.title, genre=project.idea.genre,
        secondary=project.idea.secondary, topic=project.idea.topic, plan=plan, quality=quality,
        appeal=project.idea.appeal + project.appeal_bonus, bugs=project.bugs, marketing=marketing,
        awareness=project.awareness, franchise=project.idea.franchise or project.idea.title, deal=project.deal)
    product.costs = project.costs
    s.project = None
    review = f"Press score {product.review:.0f}" if product.review else "No press coverage"
    game.log(f"Released \"{product.title}\" on {', '.join(plan.storefronts)}. {review}.")
    if game.rng.random() < 0.6:
        idea_rules.inspire(game, "release", franchise=product.franchise)


COMMANDS = {"explore": explore, "experiment": experiment, "iterate": iterate, "pivot": pivot, "shelve": shelve,
            "cancel_project": cancel, "to_design": to_design, "to_concept": to_concept, "plan": set_plan,
            "pitch": pitch, "drop_deal": drop_deal, "commit": commit, "decide": decide, "release": release}


# --- View -----------------------------------------------------------------------

def view(game):
    project = game.s.studio.project
    view = {"project": None, "experiments": [], "plan_options": plan_options(game), "decision": None}
    if not project:
        return view
    idea, plan = project.idea, project.plan
    data = {
        "id": project.id, "stage": project.stage, "idea": idea_rules.idea_view(game, idea),
        "weeks": (game.s.day - project.started_day) // 7, "findings": [f.text for f in project.findings],
        "discoveries": [d.text for d in project.discoveries], "iterations": project.iterations,
        "pivots": project.pivots, "activity": project.activity,
        "activity_name": "Iterate on the core loop" if project.activity == "iterate" else EXPERIMENT.get(project.activity, {}).get("name", ""),
        "activity_progress": project.activity_work / project.activity_total if project.activity_total else 0,
        "plan": {"scope": plan.scope, "format": plan.format, "presentation": plan.presentation,
                 "storefronts": plan.storefronts, "model": plan.model, "price": plan.price,
                 "marketing": plan.marketing, "announcement": plan.announcement},
        "deal": vars(project.deal) if project.deal else None, "pitched": project.pitched,
        "progress": project.work_done / project.work_total if project.work_total else 0,
        "work_done": round(project.work_done), "work_total": round(project.work_total),
        "known_bugs": round(project.bugs_known), "aware": round(market.aware_people(project.awareness)),
        "costs": round(project.costs), "polish_weeks": 0,
    }
    if project.stage in ("concept", "design"):
        data["forecast"] = forecast(game, project)
    if project.stage in ("production", "polish"):
        output, _ = team_output(game, skill_weights(project))
        remaining = max(0, project.work_total - project.work_done)
        data["eta_weeks"] = round(remaining / max(1, output * 5 * share_estimate(game)))
        craft = project.craft / max(1, project.work_done)
        width = idea.fun_known.high - idea.fun_known.low
        q = game.b.quality
        tools = q.tools_bonus if game.has("tools") else 0
        known_penalty = min(q.max_bug_penalty, project.bugs_known / max(1, project.work_total / 1000) * q.bugs_per_point)
        mid = (idea.fun_known.low + idea.fun_known.high) / 2 * q.fun_weight + craft * q.craft_weight + tools + project.quality_bonus - known_penalty
        data["quality_estimate"] = [max(5, round(mid - width * q.fun_weight / 2 - 3)), min(99, round(mid + width * q.fun_weight / 2))]
    view["project"] = data
    if project.stage == "concept":
        view["experiments"] = [{"key": e["key"], "name": e["name"], "blurb": e["blurb"], "skill": e["skill"],
                                "work": round(e["work"] * idea.complexity ** 0.5),
                                "available": not e.get("needs_hook") or bool(idea.hook)} for e in EXPERIMENTS]
    if project.decision is not None:
        rule = PRODUCTION_DECISIONS[project.decision]
        view["decision"] = {"title": rule["title"], "question": rule["question"],
                            "options": [{"name": o["name"], "effect": o["effect"]} for o in rule["options"]]}
    return view


def share_estimate(game):
    from .work import allocation
    return allocation(game).get("project", 0.0) or 0.5


def plan_options(game):
    locks = plan_locks(game, None)
    return {
        "scope": [{"name": s["name"], "work": s["work"], "setup": s["setup"], "price": s["price"]} for s in SCOPES],
        "format": [{"name": f["name"], "work": f["work"], "setup": f["setup"], "lock": locks.get(f["name"], "")} for f in FORMATS],
        "presentation": [{"name": p["name"], "work": p["work"]} for p in PRESENTATIONS],
        "storefront": [{"name": s["name"], "platform": s["platform"], "fee": s["fee"], "cut": s["cut"],
                        "lock": locks.get(s["name"], "")} for s in STOREFRONTS],
        "model": [{"name": m["name"], "free": m["free"], "setup": m["setup"], "lock": locks.get(m["name"], "")} for m in BUSINESS_MODELS],
        "price": list(PRICE_POINTS),
        "marketing": [{"name": m["name"], "cost": m["cost"]} for m in LAUNCH_MARKETING],
        "announcement": [{"name": a["name"]} for a in ANNOUNCEMENTS],
        "publishers": [{"name": p["name"]} for p in PUBLISHERS],
    }
