"""Card data for the Akshauhini simulator.

Thirteen kingdoms, 33 cards each (counting duplicates), plus the three ranks of
celestial hardware. Ability strings mirror classic Gwent:

  ""            vanilla
  hero          immune to weather and scorch
  spy           played to the opponent's board, draws 2
  medic         on deploy, revive the strongest unit from your graveyard
  morale        +1 to every other unit in its row
  bond          strength multiplied by the number of copies in the row (max 3)
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


# name, row, strength, ability, copies
_POOLS = {
    "hastinapura": [
        ("Bhishma", "gaja", 16, "hero", 1),
        ("Drona", "ashva", 14, "hero", 1),
        ("Ashwatthama", "padati", 15, "hero", 1),
        ("Duryodhana", "padati", 15, "hero", 1),
        ("Kripa", "ashva", 10, "morale", 1),
        ("Vikarna", "padati", 9, "morale", 1),
        ("Bhurishravas", "gaja", 11, "bond", 2),
        ("Somadatta", "gaja", 7, "bond", 2),
        ("Bahlika", "gaja", 8, "bond", 2),
        ("Dushasana", "padati", 7, "", 2),
        ("Vivimsati", "padati", 6, "", 2),
        ("Durmukha", "padati", 5, "", 2),
        ("Sanjaya", "padati", 4, "spy", 1),
        ("Kuru Levy", "padati", 2, "bond", 4),
        ("Kuru Archer", "ashva", 3, "", 3),
        ("Kuru Elephant", "gaja", 4, "", 3),
        ("Kuru Chariot", "gaja", 6, "", 2),
        ("Kuru Medic", "ashva", 5, "medic", 2),
    ],
    "anga": [
        ("Karna", "ashva", 16, "hero", 1),
        ("Karna Unarmoured", "ashva", 12, "scorch", 1),
        ("Vrishasena", "ashva", 13, "hero", 1),
        ("Chitrasena", "padati", 10, "morale", 1),
        ("Sushena", "ashva", 7, "bond", 2),
        ("Satyasena", "ashva", 6, "bond", 2),
        ("Anga Bowline", "ashva", 3, "bond", 4),
        ("Anga Spearman", "padati", 3, "", 3),
        ("Anga Guard", "padati", 4, "", 3),
        ("Anga Rider", "ashva", 5, "agile", 3),
        ("Anga Medic", "padati", 5, "medic", 2),
        ("Anga Informant", "ashva", 0, "spy", 1),
        ("Sun Herald", "ashva", 2, "morale", 2),
        ("Anga Chariot", "gaja", 6, "", 3),
        ("Anga Vanguard", "padati", 4, "", 4),
    ],
    "panchala": [
        ("Dhrishtadyumna", "gaja", 14, "hero", 1),
        ("Drupada", "padati", 13, "hero", 1),
        ("Shikhandi", "padati", 11, "hero", 1),
        ("Satyajit", "gaja", 8, "bond", 2),
        ("Uttamaujas", "ashva", 10, "morale", 1),
        ("Yudhamanyu", "ashva", 10, "morale", 1),
        ("Dhrishtaketu", "gaja", 9, "", 2),
        ("Chekitana", "ashva", 8, "agile", 2),
        ("Panchala Longbow", "ashva", 3, "bond", 4),
        ("Panchala Levy", "padati", 2, "bond", 5),
        ("Panchala Chariot", "gaja", 5, "", 3),
        ("Panchala Guard", "padati", 4, "", 3),
        ("Panchala Rider", "ashva", 4, "agile", 3),
        ("Panchala Medic", "padati", 5, "medic", 2),
        ("Panchala Scout", "padati", 1, "spy", 1),
    ],
    "matsya": [
        ("Virata", "gaja", 13, "hero", 1),
        ("Kichaka", "padati", 12, "hero", 1),
        ("Shveta", "gaja", 10, "hero", 1),
        ("Shankha", "padati", 7, "morale", 1),
        ("Uttara", "ashva", 6, "medic", 1),
        ("Sudhanva", "ashva", 7, "", 2),
        ("Matsya Wall", "padati", 2, "bond", 5),
        ("Matsya Elephant", "gaja", 5, "bond", 3),
        ("Matsya Archer", "ashva", 3, "", 4),
        ("Matsya Spear", "padati", 4, "", 3),
        ("Matsya Rider", "ashva", 4, "agile", 3),
        ("Matsya Medic", "padati", 5, "medic", 2),
        ("Matsya Informant", "ashva", 0, "spy", 1),
        ("Virata Guard", "gaja", 6, "", 2),
    ],
    "madra": [
        ("Shalya", "gaja", 15, "hero", 1),
        ("Rukmaratha", "gaja", 10, "morale", 1),
        ("Madra Noble", "padati", 6, "", 2),
        ("Madra Lancers", "padati", 4, "bond", 4),
        ("Madra Chariot", "gaja", 6, "", 3),
        ("Madra Spear", "padati", 3, "", 3),
        ("Madra Rider", "ashva", 4, "agile", 3),
        ("Madra Medic", "padati", 5, "medic", 2),
        ("Madra Scout", "padati", 1, "spy", 1),
        ("Madra Guard", "padati", 4, "", 4),
        ("Madra Archer", "ashva", 3, "bond", 4),
        ("Shalya's Driver", "gaja", 5, "morale", 2),
    ],
    "trigarta": [
        ("Susharma", "gaja", 12, "hero", 1),
        ("Satyaratha", "ashva", 7, "bond", 2),
        ("Satyavarma", "ashva", 7, "bond", 2),
        ("Trigarta Champion", "padati", 6, "", 2),
        ("Samsaptaka", "padati", 3, "bond", 5),
        ("Trigarta Chariot", "gaja", 5, "", 3),
        ("Trigarta Rider", "ashva", 4, "agile", 3),
        ("Trigarta Spear", "padati", 3, "", 4),
        ("Trigarta Medic", "padati", 5, "medic", 2),
        ("Trigarta Informant", "ashva", 0, "spy", 1),
        ("Mountain Archer", "ashva", 4, "morale", 3),
        ("Trigarta Guard", "padati", 4, "", 2),
    ],
    "kamboja": [
        ("Sudakshina", "ashva", 12, "hero", 1),
        ("Kamboja Lancer", "ashva", 6, "", 2),
        ("Kamboja Horse Archer", "ashva", 4, "bond", 4),
        ("Kamboja Skirmisher", "padati", 3, "agile", 3),
        ("Kamboja Outrider", "ashva", 5, "agile", 3),
        ("Kamboja Chariot", "gaja", 5, "", 3),
        ("Kamboja Guard", "padati", 4, "", 3),
        ("Kamboja Medic", "padati", 5, "medic", 2),
        ("Kamboja Scout", "padati", 1, "spy", 1),
        ("Kamboja Standard", "ashva", 2, "morale", 2),
        ("Kamboja Spear", "padati", 3, "", 3),
        ("Kamboja Rider", "ashva", 4, "agile", 3),
    ],
    "magadha": [
        ("Jarasandha", "padati", 15, "hero", 1),
        ("Sahadeva of Magadha", "gaja", 11, "morale", 1),
        ("Jayatsena", "padati", 10, "morale", 1),
        ("Magadha Bruiser", "padati", 6, "", 3),
        ("Magadha Maceman", "padati", 4, "bond", 5),
        ("Magadha Elephant", "gaja", 5, "bond", 3),
        ("Magadha Guard", "padati", 4, "", 3),
        ("Magadha Archer", "ashva", 3, "bond", 4),
        ("Magadha Medic", "padati", 5, "medic", 2),
        ("Magadha Informant", "padati", 1, "spy", 1),
        ("Magadha Chariot", "gaja", 6, "", 3),
    ],
    "sindhu": [
        ("Jayadratha", "gaja", 12, "hero", 1),
        ("Kotikashya", "gaja", 8, "bond", 2),
        ("Kotika", "padati", 6, "", 2),
        ("Sindhu Veteran", "padati", 7, "", 2),
        ("Sindhu Blockade", "padati", 3, "bond", 2),
        ("Sindhu Horseman", "ashva", 3, "agile", 3),
        ("Sindhu Guard", "padati", 4, "", 4),
        ("Sindhu Archer", "ashva", 3, "bond", 4),
        ("Sindhu Medic", "padati", 5, "medic", 2),
        ("Sindhu Informant", "ashva", 0, "spy", 1),
        ("Sindhu Chariot", "gaja", 6, "", 3),
        ("Sindhu Standard", "padati", 2, "morale", 2),
    ],
    "gandhara": [
        ("Shakuni", "padati", 9, "hero", 1),
        ("Uluka", "ashva", 7, "spy", 1),
        ("Vrishaka", "ashva", 6, "bond", 2),
        ("Achala", "padati", 6, "bond", 2),
        ("Gandhara Sellsword", "padati", 5, "", 2),
        ("Gandhara Rider", "ashva", 3, "agile", 4),
        ("Gandhara Skirmisher", "padati", 3, "", 4),
        ("Gandhara Medic", "padati", 5, "medic", 2),
        ("Gandhara Informant", "ashva", 0, "spy", 1),
        ("Gandhara Archer", "ashva", 2, "bond", 3),
        ("Gandhara Guard", "padati", 4, "", 3),
        ("Gandhara Standard", "padati", 2, "morale", 2),
    ],
    "pragjyotisha": [
        ("Bhagadatta", "gaja", 15, "hero", 1),
        ("Supratika", "gaja", 14, "hero", 1),
        ("Vajradatta", "gaja", 11, "bond", 2),
        ("Kirata Chieftain", "padati", 6, "", 2),
        ("Mleccha Elephant", "gaja", 6, "bond", 3),
        ("Kirata Hunter", "ashva", 3, "agile", 3),
        ("Pragjyotisha Guard", "padati", 4, "", 3),
        ("Pragjyotisha Archer", "ashva", 3, "bond", 4),
        ("Pragjyotisha Medic", "padati", 5, "medic", 2),
        ("Pragjyotisha Scout", "padati", 1, "spy", 1),
        ("War Elephant Calf", "gaja", 4, "", 3),
        ("Ankusha Bearer", "padati", 2, "morale", 2),
    ],
    "dvaraka": [
        ("Krishna", "ashva", 18, "hero", 1),
        ("Balarama", "gaja", 18, "hero", 1),
        ("Satyaki", "gaja", 14, "hero", 1),
        ("Pradyumna", "ashva", 11, "morale", 1),
        ("Kritavarma", "padati", 10, "morale", 1),
        ("Samba", "ashva", 8, "", 2),
        ("Narayani Sena", "padati", 4, "bond", 4),
        ("Yadava Chariot", "gaja", 6, "", 3),
        ("Yadava Guard", "padati", 5, "", 3),
        ("Yadava Medic", "padati", 5, "medic", 2),
        ("Yadava Informant", "ashva", 0, "spy", 1),
        ("Yadava Archer", "ashva", 3, "bond", 3),
    ],
    "indraprastha": [
        ("Arjuna", "ashva", 16, "hero", 1),
        ("Bhima", "padati", 15, "hero", 1),
        ("Yudhishthira", "padati", 14, "hero", 1),
        ("Abhimanyu", "ashva", 13, "hero", 1),
        ("Ghatotkacha", "gaja", 12, "hero", 1),
        ("Nakula", "ashva", 9, "medic", 1),
        ("Sahadeva", "ashva", 9, "morale", 1),
        ("Draupadi", "padati", 8, "morale", 1),
        ("Iravan", "ashva", 8, "agile", 1),
        ("Prativindhya", "padati", 7, "bond", 2),
        ("Mayasura", "padati", 3, "spy", 1),
        ("Indraprastha Guard", "padati", 4, "", 3),
        ("Indraprastha Archer", "ashva", 3, "bond", 4),
        ("Palace Elephant", "gaja", 5, "", 3),
        ("Indraprastha Chariot", "gaja", 6, "", 2),
        ("Indraprastha Levy", "padati", 2, "bond", 5),
    ],
}

FILLER = {
    "hastinapura": ("Kuru Levy", "padati"),
    "anga": ("Anga Vanguard", "padati"),
    "panchala": ("Panchala Levy", "padati"),
    "matsya": ("Matsya Wall", "padati"),
    "madra": ("Madra Noble", "padati"),
    "trigarta": ("Trigarta Guard", "padati"),
    "kamboja": ("Kamboja Spear", "padati"),
    "magadha": ("Magadha Guard", "padati"),
    "sindhu": ("Sindhu Guard", "padati"),
    "gandhara": ("Gandhara Skirmisher", "padati"),
    "pragjyotisha": ("Pragjyotisha Guard", "padati"),
    "dvaraka": ("Yadava Guard", "padati"),
    "indraprastha": ("Indraprastha Levy", "padati"),
}

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
    "indraprastha": "Indraprastha",
}

# The kingdoms are not equal. This is a design statement, not a balance bug.
KINGDOM_TIER = {
    "hastinapura": "major",
    "anga": "major",
    "panchala": "major",
    "magadha": "major",
    "dvaraka": "major",
    "indraprastha": "major",
    "matsya": "minor",
    "pragjyotisha": "minor",
    "madra": "minor",
    "sindhu": "minor",
    "trigarta": "minor",
    "kamboja": "minor",
    "gandhara": "weak",
}

# Equal contribution keeps alliances honest: an ally's cards are in your deck,
# weak or not. The tier table is a deck-legality statement instead: a minor or
# weak kingdom cannot field an army alone, it needs an ally.
MIN_CONTRIB = {"major": 8, "minor": 8, "weak": 8}
MIN_KINGDOMS = {"major": 1, "minor": 2, "weak": 2}

KINGDOM_ORDER = {name: i for i, name in enumerate(FACTION_NAMES)}

# ---------- three ranks of celestial hardware ----------
# Shaastra: a physical weapon. Attaches to one of your warriors and stays there.
# Astra:    a mantra-weapon. Hits the battlefield, never attaches, and needs
#           the board to suit it.
# Divine:   the Brahma-class tier. One per deck, and it takes a sacrifice.

SPECIALS = {
    "frost": CardDef("Biting Frost", "neutral", "special", 0, "weather:padati"),
    "fog": CardDef("Impenetrable Fog", "neutral", "special", 0, "weather:ashva"),
    "rain": CardDef("Torrential Rain", "neutral", "special", 0, "weather:gaja"),
    "clear": CardDef("Clear Weather", "neutral", "special", 0, "clear"),
    "horn": CardDef("Sankha", "neutral", "special", 0, "horn"),
    "scorch": CardDef("Scorch", "neutral", "special", 0, "scorch"),
}

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


def faction_pool(faction: str) -> list[CardDef]:
    """Exactly 33 cards, counting duplicate copies."""
    cards: list[CardDef] = []
    for name, row, strength, ability, copies in _POOLS[faction]:
        for _ in range(copies):
            cards.append(CardDef(name, faction, row, strength, ability))
    filler_name, filler_row = FILLER[faction]
    while len(cards) < 33:
        cards.append(CardDef(filler_name, faction, filler_row, 2, "bond"))
    assert len(cards) == 33, (faction, len(cards))
    return cards


def _unit_value(d: CardDef) -> float:
    return d.strength + _ABILITY_VALUE.get(d.ability, 0)


_PROV_BY_NAME = {d.name: PROVISIONS[k] for k, d in ALL_CARDS.items()}


def provision(d: CardDef) -> int:
    if d.row == "special":
        return _PROV_BY_NAME.get(d.name, 5)
    base = 4.0 + max(0, d.strength - 2) * 0.6 + ABILITY_PREMIUM.get(d.ability, 0.0)
    return int(round(base))


def deck_specials(pair: tuple[str, ...]) -> tuple[str, ...]:
    """Seven specials: weather for the thin row, clear, horn, scorch, one
    shaastra, and two from the astra/divine pool."""
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


def build_alliance_deck(pair: tuple[str, ...], budget: int = 200,
                        units: int = 18) -> list[CardDef]:
    """Pick units from the allied kingdoms under a provision budget.

    At most two kingdoms, each contributing an equal share. Elite kingdoms may
    not be able to field a full army within the budget, which is allowed: they
    field a smaller, stronger one.
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
        need_after = units - len(picked) - 1
        others = sorted(provision(x) for x in available if x is not c)
        return spent + provision(c) + sum(others[:need_after]) <= remaining_budget

    def pick(c: CardDef) -> None:
        nonlocal spent
        available.remove(c)
        picked.append(c)
        spent += provision(c)

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


def build_deck(faction: str, units: int = 18) -> list[CardDef]:
    """Single kingdom deck."""
    return build_alliance_deck((faction,), units=units)