"""Ideas: rough pitches the team comes up with while it works.

Every Idea hides three true values: how fun its core can be, how complex it is
to build, and how strongly it appeals to its audiences. The studio only sees
ranges that always contain the truth. Experiments narrow them.
"""
from ..content import TRAITS
from ..genres import GOOD_MATCHES
from ..idea_text import ACTIVITIES, FANTASIES, HOOKS, SETTINGS, TITLE_HEADS, TITLE_TAILS
from ..game import int_arg
from ..state import Idea, Range
from .people import available

GENERIC_QUESTIONS = {
    "systems": "Will the systems stay interesting after ten hours?",
    "narrative": "Can the story carry the whole game?",
    "reflex": "Does the moment-to-moment control feel good?",
    "exploration": "Is there enough to find?",
    "management": "Do the decisions matter, or is it busywork?",
    "creation": "Will players care about what they build?",
    "competition": "Is it fair enough to keep people competing?",
    "chance": "Does randomness feel exciting or unfair?",
}


def setup(game):
    founder = game.s.studio.team[0]
    game.s.studio.ideas.append(generate(game, founder, "team"))


def known_range(rng, truth, width, low, high):
    """A range of the given width that contains the truth at a random position."""
    width = max(0.0, min(width, high - low))
    start = truth - width * rng.uniform(0.15, 0.85)
    start = max(low, min(start, high - width))
    return Range(round(start, 2), round(start + width, 2))


def narrow(rng, known, truth, strength, low, high):
    width = (known.high - known.low) * (1 - strength)
    fresh = known_range(rng, truth, width, low, high)
    # Evidence never contradicts earlier evidence: keep inside the old range.
    return Range(max(fresh.low, known.low), min(fresh.high, known.high))


def title(rng):
    head, tail = rng.choice(TITLE_HEADS), rng.choice(TITLE_TAILS)
    style = rng.random()
    if style < 0.45:
        return f"{head}{tail}"
    if style < 0.75:
        return f"{head} {tail.capitalize()}"
    return f"The {head} {tail.capitalize()}"


def appeal_of(genre, topic, hook):
    appeal = 0.08 if topic in GOOD_MATCHES.get(genre, ()) else -0.06
    return appeal + (0.05 if hook else 0.0)


def generate(game, author, origin, franchise=""):
    rng, b = game.rng, game.b.ideas
    activity, genre, secondary, tags = rng.choice(ACTIVITIES)
    setting, topics, setting_tags = rng.choice(SETTINGS)
    hook = rng.choice(HOOKS) if rng.random() < 0.6 else None
    all_tags = sorted(set(tags) | set(setting_tags) | (set(hook[2]) if hook else set()))
    topic = rng.choice(topics)
    fun = rng.gauss(b.fun_mean + (author.design - 50) * 0.15 + (3 if hook else 0), b.fun_spread)
    fun = max(12, min(88, fun))
    complexity = 0.8 + (hook[3] * 0.8 if hook else 0) + 0.1 * ("systems" in all_tags) + rng.gauss(0, 0.12)
    complexity = round(max(0.6, min(1.9, complexity)), 2)
    appeal = round(max(-0.3, min(0.3, appeal_of(genre, topic, hook) + rng.gauss(0, 0.07))), 3)
    width_fun = b.known_width_fun * (1 - author.design / 160)
    width_complexity = 1.0 * (1 - author.code / 160)
    question = hook[1] if hook else GENERIC_QUESTIONS.get(next((t for t in tags if t in GENERIC_QUESTIONS), ""),
                                                           "Is the core idea strong enough?")
    lifetime = rng.randint(*b.lifetime_weeks) * 7
    return Idea(
        id=game.new_id(), title=title(rng), fantasy=rng.choice(FANTASIES), activity=activity, setting=setting,
        hook=hook[0] if hook else "", question=question, genre=genre, secondary=secondary, topic=topic,
        tags=all_tags, author=author.name, origin=origin, created_day=game.s.day,
        expires_day=game.s.day + lifetime, fun=round(fun, 1), complexity=complexity, appeal=appeal,
        fun_known=known_range(rng, fun, width_fun, 0, 100),
        complexity_known=known_range(rng, complexity, width_complexity, 0.5, 2.0),
        appeal_known=known_range(rng, appeal, 0.5, -0.4, 0.4), franchise=franchise,
    )


def shelf_capacity(game):
    b = game.b.ideas
    return min(b.shelf_max, b.shelf_base + len(game.s.studio.team))


def on_week(game):
    s, b = game.s.studio, game.b.ideas
    expired = [i for i in s.ideas if i.expires_day <= game.s.day]
    for idea in expired:
        s.ideas.remove(idea)
    if len(expired) == 1:
        game.log(f"The team lost interest in \"{expired[0].title}\".")
    elif expired:
        game.log(f"The team lost interest in {len(expired)} old ideas.")
    for person in s.team:
        if len(s.ideas) >= shelf_capacity(game):
            break
        if not available(person) or person.fatigue >= 90:
            continue
        chance = (b.weekly_chance + (b.founder_bonus if person.founder else 0)) * TRAITS[person.trait]["ideas"]
        if not s.ideas and not s.project:
            chance *= 2.5  # nothing to work on is when ideas come
        if person.fatigue > 70:
            chance /= 2
        if game.rng.random() < chance:
            idea = generate(game, person, "team")
            s.ideas.append(idea)
            game.log(f"{person.name} pitched an idea: \"{idea.title}\".")


def inspire(game, origin, franchise=""):
    """A release or finished job sometimes sparks a new Idea."""
    s = game.s.studio
    if len(s.ideas) < shelf_capacity(game) + 1:
        author = game.rng.choice([p for p in s.team if available(p)] or s.team)
        idea = generate(game, author, origin, franchise)
        s.ideas.append(idea)
        game.log(f"{author.name} had an idea after the {origin}: \"{idea.title}\".")


def discard(game, data):
    s = game.s.studio
    idea_id = int_arg(data, "id")
    idea = next((i for i in s.ideas if i.id == idea_id), None)
    if not idea:
        raise ValueError("That idea is gone.")
    s.ideas.remove(idea)


COMMANDS = {"discard_idea": discard}


def range_view(known, digits=0):
    return [round(known.low, digits), round(known.high, digits)]


def idea_view(game, idea):
    return {"id": idea.id, "title": idea.title, "fantasy": idea.fantasy, "activity": idea.activity,
            "setting": idea.setting, "hook": idea.hook, "question": idea.question, "genre": idea.genre,
            "secondary": idea.secondary, "topic": idea.topic, "author": idea.author, "origin": idea.origin,
            "franchise": idea.franchise, "weeks_left": max(0, (idea.expires_day - game.s.day) // 7),
            "fun": range_view(idea.fun_known), "complexity": range_view(idea.complexity_known, 2),
            "appeal": [round(idea.appeal_known.low * 100), round(idea.appeal_known.high * 100)]}


def view(game):
    return {"ideas": [idea_view(game, i) for i in game.s.studio.ideas], "idea_capacity": shelf_capacity(game)}
