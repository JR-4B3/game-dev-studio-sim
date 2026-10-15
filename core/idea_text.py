"""Idea text carried over from the old game.

Each activity names a genre and secondary genre; each setting names topics.
Hooks add an open question and technical doubt.
"""

FANTASIES = (
    'become a legend on your own terms',
    'outsmart a world built to fool you',
    'care for something fragile until it thrives',
    'survive what should have ended you',
    'build an empire from almost nothing',
    'master a deep system completely',
    'get lost in a beautiful unknown',
    'feel unbeatable, briefly and earned',
    'uncover a truth someone buried',
    'compete and prove you are the best',
    'escape a life that never fit',
    'make a mess and be the one to fix it',
)

# (activity, genre, secondary genre, tags)
ACTIVITIES = (
    ('guide a drifting settlement through hostile lands', 'Simulation', 'Strategy', ('exploration', 'management', 'systems')),
    ('build and automate a growing machine network', 'Automation', 'Building Game', ('creation', 'systems')),
    ('delve ever deeper into shifting ruins', 'Roguelite', 'Action', ('chance', 'exploration', 'reflex')),
    ("solve the town's mysteries through conversation", 'Adventure', 'Visual Novel', ('exploration', 'narrative')),
    ('defend the last bastion against endless waves', 'Strategy', 'Action', ('reflex', 'systems')),
    ('race improvised machines down impossible tracks', 'Racing', 'Skill Game', ('competition', 'reflex')),
    ('run a small business in a strange city', 'Economic Simulation', 'Simulation', ('management', 'systems')),
    ('cultivate a quiet farm on the edge of nowhere', 'Cozy Game', 'Simulation', ('creation', 'management')),
    ('duel rivals in fast, precise combat', 'Fighting Game', 'Action', ('competition', 'reflex')),
    ('survive a collapsing expedition into the wild', 'Survival Game', 'Roguelike', ('chance', 'exploration', 'systems')),
    ('command armies across a living map', 'Real-Time Strategy', 'Strategy', ('competition', 'management', 'systems')),
    ('explore a handcrafted world and chart its secrets', 'Metroidvania', 'Adventure', ('exploration', 'reflex')),
    ('outwit the table in card duels', 'Deckbuilder', 'Roguelite', ('chance', 'systems')),
    ('keep fragile creatures alive against the odds', 'Simulation', 'Puzzle Game', ('management', 'systems')),
    ('parkour across a vertical city', 'Platformer', 'Action', ('reflex',)),
    ('hunt monsters across vast hunting grounds', 'Role-Playing Game', 'Action', ('exploration', 'reflex')),
    ('unravel a conspiracy in a rain-soaked capital', 'Adventure', 'Interactive Movie', ('narrative',)),
    ('pilot a mech through escalating wars', 'Action', 'Third-Person Shooter', ('reflex', 'systems')),
    ('restore a ruined garden to life', 'Cozy Game', 'Puzzle Game', ('creation',)),
    ('climb an impossible tower that hates you', 'Platformer', 'Skill Game', ('chance', 'reflex')),
    ('direct a crew through scripted heists', 'Immersive Sim', 'Strategy', ('narrative', 'systems')),
    ('run a kitchen that is always one order from chaos', 'Simulation', 'Economic Simulation', ('management', 'reflex')),
)

# (setting, topics, tags)
SETTINGS = (
    ('a flooded machine-city', ('Oceans', 'Machines'), ('atmosphere',)),
    ('a cozy mountain village', ('Villages', 'Nature'), ('gentle',)),
    ('a derelict space station', ('Space Stations', 'Space'), ('atmosphere', 'tech')),
    ('a neon megacity', ('Cyberpunk', 'Cities'), ('atmosphere', 'tech')),
    ('an underground kingdom of miners', ('Mining', 'Dwarfs'), ('systems',)),
    ('an archipelago of floating islands', ('Islands', 'Oceans'), ('atmosphere',)),
    ('a haunted Victorian manor', ('Victorian Age', 'Ghosts'), ('narrative',)),
    ('the dying frontier of the wild west', ('Wild West', 'Cowboys'), ('narrative',)),
    ('a biopunk jungle research outpost', ('Jungle', 'Science'), ('atmosphere', 'tech')),
    ('a monastery of obsessive archivists', ('Books', 'Religion'), ('narrative',)),
    ('a highway through the end of the world', ('Apocalypse', 'Survivalism'), ('atmosphere',)),
    ('the courts of scheming noble houses', ('Noble Houses', 'Politics'), ('narrative', 'systems')),
    ("a busy spaceport at the galaxy's edge", ('Space', 'Aliens'), ('systems', 'tech')),
    ('a sunken kingdom', ('Atlantis', 'Oceans'), ('atmosphere',)),
    ('a clockwork metropolis', ('Steampunk', 'Machines'), ('systems', 'tech')),
    ('the backroads of a fantasy empire', ('Fantasy', 'Magic'), ('narrative',)),
    ('a rain-slick port town with secrets', ('Crime', 'Detective'), ('narrative',)),
    ('an ancient tomb city', ('Ancient Egypt', 'Mummies'), ('atmosphere',)),
    ('a frozen frontier station', ('Astronauts', 'Science'), ('atmosphere', 'tech')),
    ('a carnival that arrives without warning', ('Circus', 'Comedy'), ('gentle',)),
)

# (hook, open question, tags, technical doubt)
HOOKS = (
    ('the world rearranges itself every night', 'What keeps a rearranging world surprising?', ('procedural',), 0.35),
    ('every failure permanently scars the town', 'How harsh should permanent consequences feel?', ('narrative', 'persistent'), 0.2),
    ("you play the villain's overworked accountant", 'Can ledger comedy carry a whole game?', ('narrative',), 0.15),
    ('the interface lies to you', 'How much deception can players enjoy?', ('systems',), 0.3),
    ('two players share one body', 'Does shared control stay fun after an hour?', ('multiplayer',), 0.5),
    ('time only moves when you move', 'Does stopped-time pacing suit every encounter?', ('systems',), 0.25),
    ('the game remembers previous saves', 'Can cross-save memory stay fair?', ('persistent', 'systems'), 0.35),
    ('you must rebuild the town you destroyed in the intro', 'Does reversal land emotionally?', ('narrative',), 0.1),
    ('everyone lies, and the lies are mechanics', 'Can social deception work without other people?', ('narrative', 'social'), 0.4),
    ('the soundtrack is built from your actions', 'Does generative audio stay musical?', ('audio',), 0.4),
    ('gravity slowly rotates', 'Does rotating gravity stay readable?', ('reflex',), 0.45),
    ('you inherit failed expeditions from other players', 'Do inherited worlds feel fair?', ('persistent', 'procedural'), 0.55),
)

TITLE_HEADS = ('Tide', 'Ember', 'Hollow', 'Static', 'Lantern', 'Rust', 'Verdant', 'Glass', 'Iron', 'Fable', 'Drift', 'Cinder', 'Moss', 'Signal', 'Orbit', 'Bramble', 'Slate', 'Neon', 'Anchor', 'Comet', 'Marrow', 'Flux', 'Pale', 'Umbra')
TITLE_TAILS = ('fall', 'bound', 'line', 'song', 'works', 'gate', 'reach', 'forge', 'hearth', 'circuit', 'vale', 'root', 'light', 'drift', 'tide', 'spark', 'hollow', 'veil', 'coast', 'gardens', 'engine', 'letters', 'harbor', 'trail')
