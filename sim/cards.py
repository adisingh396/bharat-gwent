"""Card data for the Akshauhini simulator.

Four kingdoms, 33 cards each (counting duplicate copies), plus a shared
pool of neutral specials. Ability strings mirror classic Gwent:

  ""            vanilla
  hero          immune to weather, scorch and row effects
  spy           played to the opponent's board, draws 2
  medic         on deploy, revive the strongest unit from your graveyard
  morale        +1 to every other unit in its row
  bond          strength multiplied by the number of copies in the row
  muster        on deploy, pull every copy of `muster` from your deck
  scorch        destroy the strongest non-hero unit(s) in a row
  horn          double the row (one per row)
  clear         remove all weather
  weather:<row> set that row to strength 1 for both players
  agile         may be placed on padati or ashva
"""

from dataclasses import dataclass
from typing import Optional

ROWS = ("padati", "ashva", "gaja")


@dataclass(frozen=True)
class CardDef:
    name: str
    faction: str
    row: str
    strength: int
    ability: str = ""
    muster: Optional[str] = None
    requires: str = ""

    @property
    def weather_row(self) -> Optional[str]:
        if self.ability.startswith("weather:"):
            return self.ability.split(":", 1)[1]
        return None


# name, row, strength, ability, copies, muster
_POOLS = {
    "hastinapura": [
        ("Bhishma", "gaja", 16, "hero", 1, None),
        ("Drona", "ashva", 14, "hero", 1, None),
        ("Ashwatthama", "padati", 15, "hero", 1, None),
        ("Duryodhana", "padati", 15, "hero", 1, None),
        ("Kripa", "ashva", 10, "morale", 1, None),
        ("Vikarna", "padati", 9, "morale", 1, None),
        ("Bhurishravas", "gaja", 11, "bond", 2, None),
        ("Somadatta", "gaja", 7, "bond", 2, None),
        ("Dushasana", "padati", 7, "", 2, None),
        ("Kuru Levy", "padati", 2, "bond", 5, None),
        ("Kuru Archer", "ashva", 3, "", 4, None),
        ("Kuru Elephant", "gaja", 4, "", 3, None),
        ("Kuru Chariot", "gaja", 6, "", 2, None),
        ("Kuru Medic", "ashva", 5, "medic", 2, None),
        ("Uluka", "ashva", 0, "spy", 1, None),
        ("Hastinapura Scout", "padati", 1, "spy", 1, None),
        ("Suta Charioteer", "gaja", 4, "agile", 2, None),
    ],
    "anga": [
        ("Karna", "ashva", 16, "hero", 1, None),
        ("Karna Unarmoured", "ashva", 12, "scorch", 1, None),
        ("Vrishasena", "ashva", 13, "hero", 1, None),
        ("Chitrasena", "padati", 10, "morale", 1, None),
        ("Sushena", "ashva", 7, "bond", 2, None),
        ("Satyasena", "ashva", 6, "bond", 2, None),
        ("Anga Bowline", "ashva", 3, "bond", 4, None),
        ("Anga Spearman", "padati", 3, "", 4, None),
        ("Anga Guard", "padati", 4, "", 3, None),
        ("Anga Rider", "ashva", 5, "agile", 3, None),
        ("Anga Medic", "padati", 5, "medic", 2, None),
        ("Anga Informant", "ashva", 0, "spy", 1, None),
        ("Sun Herald", "ashva", 2, "morale", 2, None),
        ("Anga Chariot", "gaja", 6, "", 3, None),
    ],
    "panchala": [
        ("Dhrishtadyumna", "gaja", 14, "hero", 1, None),
        ("Drupada", "padati", 13, "hero", 1, None),
        ("Shikhandi", "padati", 11, "hero", 1, None),
        ("Satyajit", "gaja", 8, "bond", 2, None),
        ("Uttamaujas", "ashva", 10, "morale", 1, None),
        ("Yudhamanyu", "ashva", 10, "morale", 1, None),
        ("Panchala Longbow", "ashva", 3, "bond", 4, None),
        ("Panchala Levy", "padati", 2, "bond", 5, None),
        ("Panchala Chariot", "gaja", 5, "", 3, None),
        ("Panchala Guard", "padati", 4, "", 3, None),
        ("Panchala Rider", "ashva", 4, "agile", 3, None),
        ("Panchala Medic", "padati", 5, "medic", 2, None),
        ("Panchala Scout", "padati", 1, "spy", 1, None),
    ],
    "matsya": [
        ("Virata", "gaja", 13, "hero", 1, None),
        ("Kichaka", "padati", 12, "hero", 1, None),
        ("Shveta", "gaja", 10, "hero", 1, None),
        ("Shankha", "padati", 7, "morale", 1, None),
        ("Uttara", "ashva", 6, "medic", 1, None),
        ("Matsya Wall", "padati", 2, "bond", 5, None),
        ("Matsya Elephant", "gaja", 5, "bond", 3, None),
        ("Matsya Archer", "ashva", 3, "", 4, None),
        ("Matsya Spear", "padati", 4, "", 3, None),
        ("Matsya Rider", "ashva", 4, "agile", 3, None),
        ("Matsya Medic", "padati", 5, "medic", 2, None),
        ("Matsya Informant", "ashva", 0, "spy", 1, None),
        ("Virata Guard", "gaja", 6, "", 2, None),
    ],
    "madra": [
        ("Shalya", "gaja", 15, "hero", 1, None),
        ("Rukmaratha", "gaja", 10, "morale", 1, None),
        ("Madra Lancers", "padati", 4, "bond", 4, None),
        ("Madra Chariot", "gaja", 6, "", 3, None),
        ("Madra Spear", "padati", 3, "", 4, None),
        ("Madra Rider", "ashva", 4, "agile", 3, None),
        ("Madra Medic", "padati", 5, "medic", 2, None),
        ("Madra Scout", "padati", 1, "spy", 1, None),
        ("Madra Guard", "padati", 4, "", 3, None),
        ("Madra Archer", "ashva", 3, "bond", 4, None),
        ("Shalya's Driver", "gaja", 5, "morale", 2, None),
    ],
    "trigarta": [
        ("Susharma", "gaja", 12, "hero", 1, None),
        ("Satyaratha", "ashva", 7, "bond", 2, None),
        ("Satyavarma", "ashva", 7, "bond", 2, None),
        ("Samsaptaka", "padati", 3, "bond", 5, None),
        ("Trigarta Chariot", "gaja", 5, "", 3, None),
        ("Trigarta Rider", "ashva", 4, "agile", 3, None),
        ("Trigarta Spear", "padati", 3, "", 4, None),
        ("Trigarta Medic", "padati", 5, "medic", 2, None),
        ("Trigarta Informant", "ashva", 0, "spy", 1, None),
        ("Mountain Archer", "ashva", 4, "morale", 3, None),
        ("Trigarta Guard", "padati", 4, "", 2, None),
    ],
    "kamboja": [
        ("Sudakshina", "ashva", 12, "hero", 1, None),
        ("Kamboja Horse Archer", "ashva", 4, "bond", 4, None),
        ("Kamboja Skirmisher", "padati", 3, "agile", 3, None),
        ("Kamboja Outrider", "ashva", 5, "agile", 3, None),
        ("Kamboja Chariot", "gaja", 5, "", 3, None),
        ("Kamboja Guard", "padati", 4, "", 3, None),
        ("Kamboja Medic", "padati", 5, "medic", 2, None),
        ("Kamboja Scout", "padati", 1, "spy", 1, None),
        ("Kamboja Standard", "ashva", 2, "morale", 2, None),
        ("Kamboja Spear", "padati", 3, "", 3, None),
        ("Kamboja Rider", "ashva", 4, "agile", 3, None),
    ],
    "magadha": [
        ("Jarasandha", "padati", 15, "hero", 1, None),
        ("Sahadeva of Magadha", "gaja", 11, "morale", 1, None),
        ("Jayatsena", "padati", 10, "morale", 1, None),
        ("Magadha Maceman", "padati", 4, "bond", 5, None),
        ("Magadha Elephant", "gaja", 5, "bond", 3, None),
        ("Magadha Guard", "padati", 4, "", 3, None),
        ("Magadha Archer", "ashva", 3, "bond", 4, None),
        ("Magadha Medic", "padati", 5, "medic", 2, None),
        ("Magadha Informant", "padati", 1, "spy", 1, None),
        ("Magadha Chariot", "gaja", 6, "", 3, None),
    ],
    "sindhu": [
        ("Jayadratha", "gaja", 12, "hero", 1, None),
        ("Kotikashya", "gaja", 8, "bond", 2, None),
        ("Sindhu Blockade", "padati", 3, "bond", 2, None),
        ("Sindhu Horseman", "ashva", 3, "agile", 3, None),
        ("Sindhu Guard", "padati", 4, "", 4, None),
        ("Sindhu Archer", "ashva", 3, "bond", 4, None),
        ("Sindhu Medic", "padati", 5, "medic", 2, None),
        ("Sindhu Informant", "ashva", 0, "spy", 1, None),
        ("Sindhu Chariot", "gaja", 6, "", 3, None),
        ("Sindhu Standard", "padati", 2, "morale", 2, None),
    ],
    "gandhara": [
        ("Shakuni", "padati", 9, "hero", 1, None),
        ("Uluka", "ashva", 7, "spy", 1, None),
        ("Vrishaka", "ashva", 6, "bond", 2, None),
        ("Achala", "padati", 6, "bond", 2, None),
        ("Gandhara Rider", "ashva", 3, "agile", 4, None),
        ("Gandhara Skirmisher", "padati", 3, "", 4, None),
        ("Gandhara Medic", "padati", 5, "medic", 2, None),
        ("Gandhara Informant", "ashva", 0, "spy", 1, None),
        ("Gandhara Archer", "ashva", 2, "bond", 3, None),
        ("Gandhara Guard", "padati", 4, "", 3, None),
        ("Gandhara Standard", "padati", 2, "morale", 2, None),
    ],
    "pragjyotisha": [
        ("Bhagadatta", "gaja", 15, "hero", 1, None),
        ("Supratika", "gaja", 14, "hero", 1, None),
        ("Vajradatta", "gaja", 11, "bond", 2, None),
        ("Mleccha Elephant", "gaja", 6, "bond", 3, None),
        ("Kirata Hunter", "ashva", 3, "agile", 3, None),
        ("Pragjyotisha Guard", "padati", 4, "", 3, None),
        ("Pragjyotisha Archer", "ashva", 3, "bond", 4, None),
        ("Pragjyotisha Medic", "padati", 5, "medic", 2, None),
        ("Pragjyotisha Scout", "padati", 1, "spy", 1, None),
        ("War Elephant Calf", "gaja", 4, "", 3, None),
        ("Ankusha Bearer", "padati", 2, "morale", 2, None),
    ],
    "dvaraka": [
        ("Krishna", "ashva", 18, "hero", 1, None),
        ("Balarama", "gaja", 18, "hero", 1, None),
        ("Satyaki", "gaja", 14, "hero", 1, None),
        ("Pradyumna", "ashva", 11, "morale", 1, None),
        ("Kritavarma", "padati", 10, "morale", 1, None),
        ("Narayani Sena", "padati", 4, "bond", 4, None),
        ("Yadava Chariot", "gaja", 6, "", 3, None),
        ("Yadava Guard", "padati", 5, "", 3, None),
        ("Yadava Medic", "padati", 5, "medic", 2, None),
        ("Yadava Informant", "ashva", 0, "spy", 1, None),
        ("Yadava Archer", "ashva", 3, "bond", 3, None),
    ],
}

FILLER = {
    "hastinapura": ("Kuru Levy", "padati"),
    "anga": ("Anga Spearman", "padati"),
    "panchala": ("Panchala Levy", "padati"),
    "matsya": ("Matsya Wall", "padati"),
    "madra": ("Madra Levy", "padati"),
    "trigarta": ("Trigarta Levy", "padati"),
    "kamboja": ("Kamboja Levy", "padati"),
    "magadha": ("Magadha Levy", "padati"),
    "sindhu": ("Sindhu Levy", "padati"),
    "gandhara": ("Gandhara Levy", "padati"),
    "pragjyotisha": ("Pragjyotisha Levy", "padati"),
    "dvaraka": ("Yadava Levy", "padati"),
}

# Kingdom tiers are a design statement, not a balance bug. Great powers carry
# their alliances; small kingdoms come as junior partners and bring fewer cards.
KINGDOM_TIER = {
    "hastinapura": "major",
    "anga": "major",
    "panchala": "major",
    "magadha": "major",
    "dvaraka": "major",
    "matsya": "minor",
    "pragjyotisha": "minor",
    "madra": "minor",
    "sindhu": "minor",
    "trigarta": "minor",
    "kamboja": "minor",
    "gandhara": "weak",
}

# Equal contribution keeps alliances honest: an ally's cards are in your deck,
# weak or not. The tier table below is a deck-legality statement instead:
# a minor or weak kingdom cannot field an army alone, it needs an ally.
MIN_CONTRIB = {"major": 8, "minor": 8, "weak": 8}
MIN_KINGDOMS = {"major": 1, "minor": 2, "weak": 2}

FACTION_NAMES = {
    "hastinapura": "Hastinapura",
    "anga": "Anga",
    "panchala": "Panchala",
    "matsya": "Matsya",
    "madra": "Madra",
    "trigarta": "Trigarta",
    "kamboja": "Kamboja",
    "magadha": "Magadha",
    "sindhu": "Sindhu",
    "gandhara": "Gandhara",
    "pragjyotisha": "Pragjyotisha",
    "dvaraka": "Dvaraka",
}

KINGDOM_ORDER = {name: i for i, name in enumerate(FACTION_NAMES)}

# ---------- three ranks of celestial hardware ----------
# Shaastra: a physical weapon. Attaches to one of your warriors and stays there.
# Astra:    a mantra-weapon. Hits the battlefield, never attaches.
# Divine:   the Brahma-class tier. One per deck, and it takes a sacrifice.

SPECIALS = {
    "frost": CardDef("Biting Frost", "neutral", "special", 0, "weather:padati"),
    "fog": CardDef("Impenetrable Fog", "neutral", "special", 0, "weather:ashva"),
    "rain": CardDef("Torrential Rain", "neutral", "special", 0, "weather:gaja"),
    "clear": CardDef("Clear Weather", "neutral", "special", 0, "clear"),
    "horn": CardDef("Sankha", "neutral", "special", 0, "horn"),
    "scorch": CardDef("Scorch", "neutral", "special", 0, "scorch"),
}

# astras: conditional on the board. A dead astra in hand is the point.
ASTRAS = {
    "agni": CardDef("Agneyastra", "neutral", "special", 0, "burn:3",
                    requires="row_units:2"),
    "varuna": CardDef("Varunastra", "neutral", "special", 0, "douse",
                      requires="weather"),
    "vayu": CardDef("Vayavyastra", "neutral", "special", 0, "bounce:4",
                    requires="row_low:4"),
    "parvata": CardDef("Parvatastra", "neutral", "special", 0, "block",
                       requires="row_units:2"),
    "naga": CardDef("Nagastra", "neutral", "special", 0, "poison",
                    requires="row_units:1"),
    "garuda": CardDef("Garudastra", "neutral", "special", 0, "purify",
                      requires="poisoned"),
    "mohini": CardDef("Mohini Astra", "neutral", "special", 0, "reveal",
                      requires="enemy_horn"),
    "vajra": CardDef("Vajra", "neutral", "special", 0, "lock",
                     requires="row_units:2"),
    "sabda": CardDef("Sabda-vedhi", "neutral", "special", 0, "kill_low:3",
                     requires="row_low:3"),
    "tvashtar": CardDef("Tvashtarastra", "neutral", "special", 0, "burn:1",
                        requires="row_units:3"),
    "surya": CardDef("Suryastra", "neutral", "special", 0, "dispel",
                     requires="weather"),
    "maya": CardDef("Alambusha's Maya", "neutral", "special", 0, "maya"),
}

# shaastra: attached to a friendly unit, adds strength, some grant a property
SHASHTRAS = {
    "gandiva": CardDef("Gandiva", "neutral", "special", 0, "weapon:5"),
    "vijaya": CardDef("Vijaya", "neutral", "special", 0, "weapon:4"),
    "musala": CardDef("Musala", "neutral", "special", 0, "weapon:4"),
    "kaumodaki": CardDef("Kaumodaki", "neutral", "special", 0, "weapon:3"),
    "nandaka": CardDef("Nandaka", "neutral", "special", 0, "weapon:3"),
    "parashu": CardDef("Parashu", "neutral", "special", 0, "weapon:3"),
    "akshaya": CardDef("Akshaya Quiver", "neutral", "special", 0, "weapon:2"),
    "kavach": CardDef("Karna's Kavach", "neutral", "special", 0, "weapon:0:immune"),
}

# divine: one per deck, costs a warrior, and only legal when it matters
DIVINE = {
    "brahma": CardDef("Brahmastra", "neutral", "special", 0,
                      "divine:kill_top_all", requires="enemy_units:3"),
    "brahmashirsha": CardDef("Brahmashirsha", "neutral", "special", 0,
                             "divine:kill_row", requires="row_total:15"),
    "brahmanda": CardDef("Brahmanda Astra", "neutral", "special", 0,
                         "divine:kill_all", requires="enemy_units:5"),
    "pashupata": CardDef("Pashupatastra", "neutral", "special", 0,
                         "divine:kill_any", requires="enemy_hero"),
    "narayana": CardDef("Narayanastra", "neutral", "special", 0,
                        "divine:punish:5", requires="row_units:3"),
    "vaishnava": CardDef("Vaishnavastra", "neutral", "special", 0,
                         "divine:kill_any:single", requires="enemy_units:2"),
    "vasavi": CardDef("Vasavi Shakti", "neutral", "special", 0,
                      "divine:kill_any:single", requires="enemy_hero"),
    "raudra": CardDef("Raudrastra", "neutral", "special", 0,
                      "divine:kill_row_low:5", requires="row_units:3"),
}

PROVISIONS = {
    "frost": 5, "fog": 5, "rain": 5, "clear": 4, "horn": 5, "scorch": 5,
    "agni": 8, "varuna": 6, "vayu": 7, "parvata": 6, "naga": 7, "garuda": 5,
    "mohini": 5, "vajra": 6, "sabda": 6, "tvashtar": 7, "surya": 5, "maya": 7,
    "gandiva": 10, "vijaya": 8, "musala": 8, "kaumodaki": 7, "nandaka": 7,
    "parashu": 7, "akshaya": 6, "kavach": 9,
    "brahma": 16, "brahmashirsha": 18, "brahmanda": 20, "pashupata": 17,
    "narayana": 15, "vaishnava": 14, "vasavi": 13, "raudra": 15,
}

ALL_CARDS = {**SPECIALS, **ASTRAS, **SHASHTRAS, **DIVINE}

ASTRA_POOL = ("agni", "varuna", "vayu", "parvata", "naga", "garuda", "mohini",
              "vajra", "sabda", "tvashtar", "surya", "maya")
SHASHTRA_POOL = ("gandiva", "vijaya", "musala", "kaumodaki", "nandaka",
                 "parashu", "akshaya", "kavach")
DIVINE_POOL = ("brahma", "brahmashirsha", "brahmanda", "pashupata",
               "narayana", "vaishnava", "vasavi", "raudra")

_ABILITY_VALUE = {
    "hero": 4,
    "spy": 6,
    "medic": 5,
    "morale": 3,
    "bond": 2,
    "muster": 2,
    "scorch": 3,
    "agile": 1,
    "": 0,
}


def faction_pool(faction: str) -> list[CardDef]:
    """Exactly 33 cards, counting duplicate copies."""
    entries = _POOLS[faction]
    cards: list[CardDef] = []
    for name, row, strength, ability, copies, muster in entries:
        for _ in range(copies):
            cards.append(CardDef(name, faction, row, strength, ability, muster))
    filler_name, filler_row = FILLER[faction]
    while len(cards) < 33:
        cards.append(CardDef(filler_name, faction, filler_row, 2, "bond"))
    assert len(cards) == 33, (faction, len(cards))
    return cards


def _unit_value(d: CardDef) -> float:
    return d.strength + _ABILITY_VALUE.get(d.ability, 0)


# ---------- provisions (Gwent Homecoming style) ----------
# Every card has a cost. A deck is built to a fixed budget, so taking Bhishma
# means giving up three mid cards. This is the normalisation that stops an
# alliance from simply stacking every hero in the game.

ABILITY_PREMIUM = {
    "hero": 3.0,
    "spy": 3.0,
    "medic": 4.0,
    "morale": 3.0,
    "bond": 2.0,
    "muster": 2.0,
    "scorch": 2.5,
    "agile": 1.0,
    "": 0.0,
}

_PROV_BY_NAME = {d.name: PROVISIONS[k] for k, d in ALL_CARDS.items()}


def provision(d: CardDef) -> int:
    if d.row == "special":
        return _PROV_BY_NAME.get(d.name, 5)
    base = 4.0 + max(0, d.strength - 2) * 0.6 + ABILITY_PREMIUM.get(d.ability, 0.0)
    return int(round(base))


def deck_specials(pair: tuple[str, ...]) -> tuple[str, ...]:
    """Seven specials: weather for the thin row, clear, horn, scorch, one
    shaastra, and two from the astra/divine pool. Great powers carry a divine
    weapon; smaller kingdoms carry two astras instead."""
    rows = {r: 0 for r in ROWS}
    for f in pair:
        for d in faction_pool(f):
            if d.row in rows:
                rows[d.row] += 1
    thin = sorted(rows, key=rows.get)[0]
    weather = {"padati": "frost", "ashva": "fog", "gaja": "rain"}[thin]
    idx = sum(KINGDOM_ORDER.get(f, 0) for f in pair)
    shastra = SHASHTRA_POOL[idx % len(SHASHTRA_POOL)]
    major = any(KINGDOM_TIER[f] == "major" for f in pair)
    if major:
        first = DIVINE_POOL[idx % len(DIVINE_POOL)]
        second = ASTRA_POOL[(idx * 2) % len(ASTRA_POOL)]
    else:
        first = ASTRA_POOL[idx % len(ASTRA_POOL)]
        second = ASTRA_POOL[(idx + 5) % len(ASTRA_POOL)]
    return (weather, "clear", "horn", "scorch", shastra, first, second)


def _max_affordable(available: list[CardDef], budget: int) -> int:
    total = 0
    n = 0
    for p in sorted(provision(c) for c in available):
        if total + p > budget:
            break
        total += p
        n += 1
    return n


def build_alliance_deck(pair: tuple[str, ...], budget: int = 160,
                        units: int = 18) -> list[CardDef]:
    """Pick units from the allied kingdoms under a provision budget.

    Rules: at most two kingdoms, and each must contribute a minimum number of
    cards set by its tier. Great powers carry the alliance; a weak kingdom
    like Gandhara comes as a junior partner and brings fewer cards.

    Elite kingdoms may not be able to field a full 21 within the budget. That
    is allowed: they field a smaller, stronger army.
    """
    pair = tuple(pair)
    assert 1 <= len(pair) <= 2, pair
    specials = deck_specials(pair)
    remaining_budget = budget - sum(PROVISIONS[s] for s in specials)

    available: list[CardDef] = []
    for f in pair:
        available.extend(faction_pool(f))

    affordable = _max_affordable(available, remaining_budget)
    units = max(12, min(units, affordable))

    mins = [MIN_CONTRIB[KINGDOM_TIER[f]] for f in pair]
    while sum(mins) > units:
        i = mins.index(max(mins))
        mins[i] -= 1

    picked: list[CardDef] = []
    spent = 0

    def feasible(c: CardDef) -> bool:
        """Can we take this card and still fill the remaining slots?"""
        need_after = units - len(picked) - 1
        others = sorted(provision(x) for x in available if x is not c)
        return spent + provision(c) + sum(others[:need_after]) <= remaining_budget

    def pick(c: CardDef) -> None:
        nonlocal spent
        available.remove(c)
        picked.append(c)
        spent += provision(c)

    # alliance obligation: each kingdom brings its minimum
    if len(pair) == 2:
        for f, need in zip(pair, mins):
            while (len(picked) < units
                   and sum(1 for x in picked if x.faction == f) < need):
                cands = sorted([c for c in available if c.faction == f],
                               key=lambda c: _unit_value(c) / provision(c),
                               reverse=True)
                chosen = next((c for c in cands if feasible(c)), None)
                if chosen is None:
                    break
                pick(chosen)

    # fill by best value per provision, keeping the deck affordable
    while len(picked) < units:
        cands = sorted(available,
                       key=lambda c: _unit_value(c) / provision(c), reverse=True)
        chosen = next((c for c in cands if feasible(c)), None)
        if chosen is None:
            break
        pick(chosen)

    deck = picked + [ALL_CARDS[s] for s in specials]
    assert len(deck) >= 12, (len(deck), pair)
    return deck


def build_deck(faction: str, units: int = 21) -> list[CardDef]:
    """Backwards-compatible single kingdom deck."""
    return build_alliance_deck((faction,), units=units)