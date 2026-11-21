"""Effect tests for every special card. Run: python -m sim._selftest"""

from __future__ import annotations

from .cards import ALL_CARDS, CardDef, ROWS, SPECIALS
from .engine import Card, Game, new_game


def fresh() -> Game:
    """A clean mid-round board. Each side keeps one card in hand so the round
    cannot auto-end while a test is inspecting the board."""
    g = new_game(("hastinapura",), ("anga",), seed=1)
    for idx, s in enumerate(g.sides):
        s.hand = [Card(CardDef("Dummy", "neutral", "padati", 1), idx)]
        s.deck.clear()
        s.grave.clear()
        for r in ROWS:
            s.rows[r].clear()
            s.horns[r] = False
        s.passed = False
    g.weather = {r: False for r in ROWS}
    g.blocked = {}
    g.locked = {}
    g.current = 0
    g.round = 1
    g.wins = [0, 0]
    g.round_scores = []
    g.points_total = [0, 0]
    g.log = []
    g.phase = "round"
    return g


def put(g: Game, p: int, row: str, strength: int, ability: str = "") -> Card:
    c = Card(CardDef(f"T{strength}", "neutral", row, strength, ability), p)
    g.sides[p].rows[row].append(c)
    return c


def give(g: Game, key: str) -> None:
    g.sides[0].hand.insert(0, Card(ALL_CARDS[key], 0))


def play(g: Game, row=None) -> None:
    g.play(("play", 0, row))


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"  [{'ok' if cond else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))
    if not cond:
        raise SystemExit(1)


def main() -> None:
    # burn: 3 to every non-hero in a row, hero untouched, dead units removed
    g = fresh()
    put(g, 1, "ashva", 3)
    put(g, 1, "ashva", 5)
    put(g, 1, "ashva", 10, "hero")
    give(g, "agni")
    play(g, "ashva")
    check("Agneyastra burns non-heroes", g.row_total(1, "ashva") == 12,
          f"ashva={g.row_total(1, 'ashva')} (5-3=2 + hero 10)")
    check("Agneyastra kills a 3", len(g.sides[1].rows["ashva"]) == 2)

    # conditions: an astra with no valid target is simply not legal
    g = fresh()
    put(g, 1, "ashva", 5)
    give(g, "vasavi")          # requires an enemy hero
    acts = [a for a in g.legal_actions(0) if a[0] == "play"]
    check("Vasavi Shakti is illegal with no enemy hero",
          all(a[1] != 0 for a in acts))
    put(g, 1, "ashva", 10, "hero")
    acts = [a for a in g.legal_actions(0) if a[0] == "play"]
    check("Vasavi Shakti becomes legal once a hero is on the board",
          any(a[1] == 0 for a in acts))

    # and a weather-dependent astra is dead until weather exists
    g = fresh()
    put(g, 1, "gaja", 5)
    give(g, "varuna")          # requires weather
    acts = [a for a in g.legal_actions(0) if a[0] == "play"]
    check("Varunastra is dead without weather", all(a[1] != 0 for a in acts))
    g.weather["gaja"] = True
    acts = [a for a in g.legal_actions(0) if a[0] == "play"]
    check("Varunastra wakes up when weather is up",
          any(a[1] == 0 for a in acts))

    # ignores hero immunity
    g = fresh()
    put(g, 1, "ashva", 10, "hero")
    put(g, 1, "ashva", 2)
    give(g, "vasavi")
    play(g, "ashva")
    check("Vasavi Shakti kills a hero", g.row_total(1, "ashva") == 2)

    # poison: strongest non-hero scores 1
    g = fresh()
    put(g, 1, "padati", 9)
    put(g, 1, "padati", 2)
    give(g, "naga")
    play(g, "padati")
    check("Nagastra poisons the strongest to 1", g.row_total(1, "padati") == 3,
          f"padati={g.row_total(1, 'padati')}")

    # block: row refuses new units, and is not offered as a legal target
    g = fresh()
    put(g, 1, "gaja", 4)
    give(g, "parvata")
    play(g, "gaja")
    check("Parvatastra blocks the row", g.blocked.get((1, "gaja")) is True)
    g.sides[1].hand.append(Card(CardDef("X", "neutral", "gaja", 2), 1))
    g.current = 1
    legal = [a for a in g.legal_actions(1) if a[0] == "play"]
    check("blocked row is not a legal placement",
          all(a[2] != "gaja" for a in legal))

    # bounce: small units go back to hand
    g = fresh()
    put(g, 1, "ashva", 3)
    put(g, 1, "ashva", 9)
    give(g, "vayu")
    play(g, "ashva")
    check("Vayavyastra bounces strength <= 4", g.row_total(1, "ashva") == 9)
    check("bounced card reached the hand", len(g.sides[1].hand) == 2)

    # punish: destroy everything at or above a threshold
    g = fresh()
    put(g, 1, "padati", 6)
    put(g, 1, "padati", 7)
    put(g, 1, "padati", 2)
    give(g, "narayana")
    play(g, "padati")
    check("Narayanastra punishes tall units", g.row_total(1, "padati") == 2,
          f"padati={g.row_total(1, 'padati')}")

    # maya: two illusion tokens
    g = fresh()
    give(g, "maya")
    before = len(g.sides[0].rows["padati"])
    play(g, "padati")
    check("Maya summons two tokens",
          len(g.sides[0].rows["padati"]) == before + 2)
    check("tokens score 4", g.row_total(0, "padati") == 4,
          "two 2-strength illusions")

    # purify: clears weather and poison
    g = fresh()
    put(g, 0, "ashva", 7)
    g.weather["ashva"] = True
    g.sides[0].rows["ashva"][-1].poisoned = True
    give(g, "garuda")
    play(g, None)
    check("Garudastra clears weather", g.weather["ashva"] is False)
    check("Garudastra cures poison", g.sides[0].rows["ashva"][-1].poisoned is False)

    # brahmastra: strongest non-hero in every enemy row
    g = fresh()
    put(g, 1, "padati", 7)
    put(g, 1, "ashva", 8)
    put(g, 1, "gaja", 6)
    give(g, "brahma")
    play(g, None)
    check("Brahmastra hits every row",
          all(g.row_total(1, r) == 0 for r in ROWS))

    # reveal: draw one and strip enemy horns
    g = fresh()
    g.sides[0].deck.append(Card(CardDef("D", "neutral", "padati", 2), 0))
    g.sides[1].horns["gaja"] = True
    give(g, "mohini")
    hand_before = len(g.sides[0].hand)
    play(g, None)
    check("Mohini draws a card",
          len(g.sides[0].hand) == hand_before,  # played one, drew one
          f"hand={len(g.sides[0].hand)}")
    check("Mohini strips enemy horn", g.sides[1].horns["gaja"] is False)

    # douse: clears weather and burns 1
    g = fresh()
    put(g, 1, "gaja", 5)
    g.weather["gaja"] = True
    give(g, "varuna")
    play(g, "gaja")
    check("Varunastra clears weather", g.weather["gaja"] is False)
    check("Varunastra burns for 1", g.row_total(1, "gaja") == 4)

    # lock: abilities in a row stop working
    g = fresh()
    g.sides[1].horns["ashva"] = True
    put(g, 1, "ashva", 4)
    put(g, 1, "ashva", 4)
    plain = g.row_total(1, "ashva")
    g.locked[(1, "ashva")] = True
    locked = g.row_total(1, "ashva")
    check("locked row ignores horn", locked == 8 and plain == 16,
          f"horn {plain} -> locked {locked}")

    # shaastra: attaches to your strongest warrior and adds strength
    g = fresh()
    put(g, 0, "padati", 5)
    give(g, "gandiva")
    play(g, "padati")
    check("Gandiva attaches and adds 5", g.row_total(0, "padati") == 10,
          f"padati={g.row_total(0, 'padati')}")
    check("weapon is recorded on the unit",
          g.sides[0].rows["padati"][0].weapon == "Gandiva")

    # a unit cannot take a second weapon
    g = fresh()
    put(g, 0, "padati", 5)
    give(g, "gandiva")
    play(g, "padati")
    give(g, "vijaya")
    play(g, "padati")
    check("second weapon finds no free target",
          g.sides[0].rows["padati"][0].weapon == "Gandiva",
          "still Gandiva, no stacking")

    # kavach: immune to damage
    g = fresh()
    put(g, 0, "padati", 4)
    give(g, "kavach")
    play(g, "padati")
    armed = g.sides[0].rows["padati"][0]
    check("Kavach grants immunity", armed.w_immune is True)
    g.sides[1].hand.append(Card(ALL_CARDS["agni"], 1))
    g.current = 1
    g.play(("play", 0, "padati"))
    check("immune unit ignores Agneyastra", g.row_total(0, "padati") == 4,
          f"padati={g.row_total(0, 'padati')}")

    # divine: hits the enemy and costs you a warrior
    g = fresh()
    put(g, 1, "padati", 8)
    put(g, 1, "ashva", 9)
    put(g, 0, "padati", 2)
    put(g, 0, "padati", 6)
    give(g, "brahma")
    play(g, None)
    check("Brahmastra clears the enemy board",
          all(g.row_total(1, r) == 0 for r in ROWS))
    check("Brahmastra sacrifices your weakest",
          g.row_total(0, "padati") == 6,
          f"own padati={g.row_total(0, 'padati')} (the 2 died)")

    # vasavi: single use, no sacrifice
    g = fresh()
    put(g, 1, "ashva", 12, "hero")
    put(g, 0, "padati", 2)
    give(g, "vasavi")
    play(g, "ashva")
    check("Vasavi Shakti kills a hero", g.row_total(1, "ashva") == 0)
    check("Vasavi Shakti costs no sacrifice", g.row_total(0, "padati") == 2)

    # new astras
    g = fresh()
    put(g, 1, "ashva", 2)
    put(g, 1, "ashva", 9)
    give(g, "sabda")            # kill_low:3, requires row_low:3
    play(g, "ashva")
    check("Sabda-vedhi kills the weakest", g.row_total(1, "ashva") == 9)

    g = fresh()
    put(g, 1, "padati", 3)
    put(g, 1, "padati", 4)
    give(g, "vajra")            # lock a row
    play(g, "padati")
    check("Vajra locks the row", g.locked.get((1, "padati")) is True)

    g = fresh()
    put(g, 1, "gaja", 5)
    give(g, "tvashtar")         # burn 1, requires 3 units
    g.sides[1].rows["gaja"].append(Card(CardDef("T2", "neutral", "gaja", 2), 1))
    g.sides[1].rows["gaja"].append(Card(CardDef("T3", "neutral", "gaja", 3), 1))
    play(g, "gaja")
    check("Tvashtarastra chips the row", g.row_total(1, "gaja") == 7,
          f"gaja={g.row_total(1, 'gaja')} (5+2+3 -3)")

    g = fresh()
    g.weather["ashva"] = True
    g.sides[1].horns["gaja"] = True
    give(g, "surya")            # dispel, requires weather
    play(g, None)
    check("Suryastra clears weather and horns",
          not any(g.weather.values()) and not any(g.sides[1].horns.values()))

    g = fresh()
    put(g, 1, "padati", 4)
    put(g, 1, "ashva", 5)
    put(g, 1, "gaja", 6)
    put(g, 0, "padati", 2)
    give(g, "brahmanda")        # kill_all, requires 5 enemy units
    g.sides[1].rows["padati"].append(Card(CardDef("T1", "neutral", "padati", 1), 1))
    g.sides[1].rows["ashva"].append(Card(CardDef("T1b", "neutral", "ashva", 1), 1))
    play(g, None)
    check("Brahmanda Astra wipes the board",
          all(g.row_total(1, r) == 0 for r in ROWS))

    g = fresh()
    put(g, 1, "padati", 4)
    put(g, 1, "padati", 9)
    put(g, 1, "padati", 3)
    give(g, "raudra")           # kill_row_low:5, requires 3 units
    play(g, "padati")
    check("Raudrastra kills the small ones", g.row_total(1, "padati") == 9)

    print("\n  all special effects behave.")


if __name__ == "__main__":
    main()