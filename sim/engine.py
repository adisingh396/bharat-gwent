"""A faithful-enough clone of classic Gwent rules, Mahabharata themed.

Rules kept identical to the original minigame:
  - 10 cards drawn at the start, no further draws between rounds
  - three rows, three rounds, win two
  - one card per turn, passing ends your round but the opponent keeps playing
  - points only, no life totals
  - the winner of a round leads the next round
  - weather sets a row to 1, horn doubles a row, scorch kills the strongest
"""

from __future__ import annotations

import copy
import random
from dataclasses import dataclass, field
from typing import Optional

from .cards import CardDef, ROWS, build_alliance_deck, FACTION_NAMES


@dataclass
class Card:
    d: CardDef
    owner: int
    poisoned: bool = False
    illusion: bool = False
    damage: int = 0
    w_bonus: int = 0
    w_immune: bool = False
    weapon: str = ""

    @property
    def name(self) -> str:
        return self.d.name

    @property
    def strength(self) -> int:
        return self.d.strength

    @property
    def ability(self) -> str:
        return self.d.ability

    @property
    def row(self) -> str:
        return self.d.row

    @property
    def special(self) -> bool:
        return self.d.row == "special"

    def __repr__(self) -> str:
        return f"{self.name}({self.strength})"


@dataclass
class Side:
    factions: tuple
    hand: list[Card] = field(default_factory=list)
    deck: list[Card] = field(default_factory=list)
    grave: list[Card] = field(default_factory=list)
    rows: dict[str, list[Card]] = field(default_factory=lambda: {r: [] for r in ROWS})
    horns: dict[str, bool] = field(default_factory=lambda: {r: False for r in ROWS})
    passed: bool = False

    @property
    def name(self) -> str:
        return " + ".join(FACTION_NAMES[f] for f in self.factions)


@dataclass
class Game:
    sides: list[Side]
    weather: dict[str, bool]
    current: int
    round: int
    wins: list[int]
    first: int
    phase: str
    round_scores: list[tuple]
    points_total: list[int]
    log: list[tuple]
    seed: int = 0
    last_board: list = field(default_factory=list)
    draw_between: int = 0
    lead_loser: bool = False
    mulligan_count: int = 2
    rng: random.Random = field(default_factory=random.Random)
    blocked: dict = field(default_factory=dict)   # (side, row) -> True this round
    locked: dict = field(default_factory=dict)    # (side, row) -> True this round

    # ---------- scoring ----------

    def row_total(self, p: int, row: str) -> int:
        cards = self.sides[p].rows[row]
        if not cards:
            return 0
        bond_counts: dict[str, int] = {}
        for c in cards:
            bond_counts[c.name] = bond_counts.get(c.name, 0) + 1
        morale = sum(1 for c in cards if c.ability == "morale")
        horn = self.sides[p].horns[row]
        w = self.weather.get(row, False)
        locked = self.locked.get((p, row), False)
        total = 0
        for c in cards:
            if c.poisoned:
                total += 1
                continue
            if c.ability == "hero":
                total += c.strength + c.w_bonus
                continue
            s = max(0, c.strength + c.w_bonus - c.damage)
            if s == 0:
                continue
            if w:
                s = 1
            if not locked:
                if c.ability == "bond":
                    # capped at three copies, or cheap chaff becomes quadratic
                    s *= min(bond_counts[c.name], 3)
                s += max(0, morale - (1 if c.ability == "morale" else 0))
                if horn:
                    s *= 2
            total += s
        return total

    def total(self, p: int) -> int:
        return sum(self.row_total(p, r) for r in ROWS)

    def totals(self) -> tuple[int, int]:
        return self.total(0), self.total(1)

    # ---------- legality ----------

    def _special_targets(self, p: int, card: Card) -> list:
        side = self.sides[p]
        ab = card.ability
        if ab.startswith("weather:"):
            return [ab.split(":", 1)[1]]
        if ab in ("clear", "purify", "reveal", "dispel",
                  "divine:kill_top_all", "divine:kill_all"):
            return [None]
        if ab == "horn":
            return [r for r in ROWS if not side.horns[r]]
        if ab.startswith("weapon:"):
            return [r for r in ROWS
                    if any(c.weapon == "" and not c.illusion for c in side.rows[r])]
        return list(ROWS)

    def _condition_ok(self, p: int, card: Card, row) -> bool:
        """An astra is only legal when the board makes it worth casting.

        This is the whole point of the tier: bad hands are possible, so the
        opening redraw has something to fix.
        """
        req = card.d.requires
        if not req:
            return True
        kind, _, arg = req.partition(":")
        n = int(arg) if arg.isdigit() else 0
        opp = 1 - p
        if kind == "row_units":
            return row is not None and len(self.sides[opp].rows[row]) >= n
        if kind == "row_total":
            return row is not None and self.row_total(opp, row) >= n
        if kind == "row_low":
            return (row is not None and
                    any(c.strength <= n for c in self.sides[opp].rows[row]))
        if kind == "enemy_units":
            return sum(len(self.sides[opp].rows[r]) for r in ROWS) >= n
        if kind == "enemy_hero":
            return any(c.ability == "hero" for r in ROWS
                       for c in self.sides[opp].rows[r])
        if kind == "weather":
            return any(self.weather.values())
        if kind == "poisoned":
            return any(c.poisoned for r in ROWS for c in self.sides[p].rows[r])
        if kind == "enemy_horn":
            return any(self.sides[opp].horns.values())
        return True

    def legal_actions(self, p: int) -> list[tuple]:
        side = self.sides[p]
        acts: list[tuple] = []
        for idx, card in enumerate(side.hand):
            if card.special:
                for row in self._special_targets(p, card):
                    if self._condition_ok(p, card, row):
                        acts.append(("play", idx, row))
            elif card.row == "agile":
                for r in ("padati", "ashva"):
                    if not self.blocked.get((p, r)):
                        acts.append(("play", idx, r))
            else:
                if not self.blocked.get((p, card.row)):
                    acts.append(("play", idx, card.row))
        acts.append(("pass", None, None))
        return acts

    # ---------- moves ----------

    def mulligan(self, p: int, indices: list[int]) -> tuple[list[Card], list[Card]]:
        """Return chosen cards to the deck, then draw the same number at random.

        This is the only lever a player has over the opening hand: the ten
        cards are dealt blind, and a redraw is a second blind draw.
        """
        side = self.sides[p]
        idx = sorted({i for i in indices if 0 <= i < len(side.hand)})
        returned = [side.hand[i] for i in idx]
        for i in reversed(idx):
            side.hand.pop(i)
        side.deck.extend(returned)
        self.rng.shuffle(side.deck)
        drawn: list[Card] = []
        for _ in returned:
            if side.deck:
                card = side.deck.pop()
                side.hand.append(card)
                drawn.append(card)
        return returned, drawn

    def play(self, action: tuple) -> None:
        p = self.current
        if action[0] == "pass":
            self.sides[p].passed = True
        else:
            _, idx, row = action
            card = self.sides[p].hand.pop(idx)
            self._resolve(p, card, row)
            if not self.sides[1 - p].passed:
                self.current = 1 - p
        self._next_turn()

    def _resolve(self, p: int, card: Card, row: Optional[str]) -> None:
        side = self.sides[p]
        ab = card.ability

        if card.special:
            if ab.startswith("weather:"):
                self.weather[row] = True
            elif ab == "clear":
                self.weather = {r: False for r in ROWS}
            elif ab == "purify":
                self.weather = {r: False for r in ROWS}
                for r in ROWS:
                    for c in side.rows[r]:
                        c.poisoned = False
                self.locked = {k: v for k, v in self.locked.items() if k[0] != p}
            elif ab == "reveal":
                if side.deck:
                    side.hand.append(side.deck.pop())
                for r in ROWS:
                    self.sides[1 - p].horns[r] = False
            elif ab == "horn" and row:
                side.horns[row] = True
            elif ab == "scorch" and row:
                self._scorch(1 - p, row)
            elif ab == "burn" or ab.startswith("burn:"):
                n = int(ab.split(":")[1]) if ":" in ab else 1
                self._burn(1 - p, row, n)
            elif ab == "douse" and row:
                self.weather = {r: False for r in ROWS}
                self._burn(1 - p, row, 1)
            elif ab.startswith("bounce:") and row:
                self._bounce(1 - p, row, int(ab.split(":")[1]))
            elif ab == "block" and row:
                self.blocked[(1 - p, row)] = True
            elif ab == "poison" and row:
                self._poison(1 - p, row)
            elif ab in ("kill_top", "kill_any") and row:
                self._kill_top(1 - p, row, ignore_hero=(ab == "kill_any"))
            elif ab.startswith("weapon:"):
                self._attach(p, row, card)
            elif ab == "lock" and row:
                self.locked[(1 - p, row)] = True
            elif ab.startswith("kill_low:") and row:
                self._kill_low(1 - p, row, int(ab.split(":")[1]))
            elif ab == "dispel":
                self.weather = {r: False for r in ROWS}
                for r in ROWS:
                    self.sides[1 - p].horns[r] = False
            elif ab.startswith("divine:"):
                self._divine(p, ab, row)
            elif ab.startswith("punish:") and row:
                self._punish(1 - p, row, int(ab.split(":")[1]))
            elif ab == "maya" and row:
                self._maya(p, row)
            self.log.append((self.round, self._turn_no(), p, card, f"{ab}", self.totals()))
            return

        if ab == "spy":
            self.sides[1 - p].rows[card.row].append(card)
            card.owner = 1 - p
            for _ in range(2):
                if side.deck:
                    side.hand.append(side.deck.pop())
        else:
            side.rows[row].append(card)

        if ab == "muster" and card.d.muster:
            pulled = [c for c in side.deck if c.name == card.d.muster]
            for c in pulled:
                side.deck.remove(c)
                side.rows[row].append(c)

        if ab == "medic":
            pool = [c for c in side.grave if c.ability != "hero"]
            if pool:
                best = max(pool, key=lambda c: c.strength)
                side.grave.remove(best)
                best.owner = p
                side.rows[row].append(best)

        self.log.append((self.round, self._turn_no(), p, card, row or "", self.totals()))

    def _scorch(self, victim: int, row: str) -> None:
        if self.row_total(victim, row) < 10:
            return
        cards = self.sides[victim].rows[row]
        pool = [c for c in cards if c.ability != "hero"]
        if not pool:
            return
        top = max(c.strength for c in pool)
        doomed = [c for c in pool if c.strength == top]
        for c in doomed:
            cards.remove(c)
            self.sides[victim].grave.append(c)

    # ---------- astra effects ----------

    def _burn(self, victim: int, row: str, n: int) -> None:
        cards = self.sides[victim].rows[row]
        for c in list(cards):
            if c.ability == "hero" or c.poisoned or c.w_immune:
                continue
            c.damage += n
            if c.strength - c.damage <= 0:
                cards.remove(c)
                self.sides[victim].grave.append(c)

    def _bounce(self, victim: int, row: str, limit: int) -> None:
        cards = self.sides[victim].rows[row]
        for c in list(cards):
            if c.ability == "hero" or c.illusion:
                continue
            if c.strength <= limit:
                cards.remove(c)
                self.sides[victim].hand.append(c)

    def _poison(self, victim: int, row: str) -> None:
        pool = [c for c in self.sides[victim].rows[row]
                if c.ability != "hero" and not c.poisoned and not c.w_immune]
        if pool:
            max(pool, key=lambda c: c.strength).poisoned = True

    def _kill_top(self, victim: int, row: str, ignore_hero: bool) -> None:
        cards = self.sides[victim].rows[row]
        pool = [c for c in cards if ignore_hero or c.ability != "hero"]
        if not pool:
            return
        target = max(pool, key=lambda c: c.strength)
        cards.remove(target)
        self.sides[victim].grave.append(target)

    def _punish(self, victim: int, row: str, threshold: int) -> None:
        cards = self.sides[victim].rows[row]
        doomed = [c for c in cards
                  if c.ability != "hero" and not c.w_immune and c.strength >= threshold]
        for c in doomed:
            cards.remove(c)
            self.sides[victim].grave.append(c)

    def _kill_low(self, victim: int, row: str, limit: int) -> None:
        cards = self.sides[victim].rows[row]
        pool = [c for c in cards
                if c.ability != "hero" and not c.w_immune and c.strength <= limit]
        if not pool:
            return
        target = min(pool, key=lambda c: c.strength)
        cards.remove(target)
        self.sides[victim].grave.append(target)

    def _maya(self, p: int, row: str) -> None:
        token = CardDef("Maya", "neutral", row, 2, "illusion")
        for _ in range(2):
            self.sides[p].rows[row].append(Card(token, p, illusion=True))

    # ---------- shaastra and divine ----------

    def _attach(self, p: int, row: str, card: Card) -> None:
        parts = card.ability.split(":")
        bonus = int(parts[1]) if len(parts) > 1 else 0
        immune = len(parts) > 2 and parts[2] == "immune"
        pool = [c for c in self.sides[p].rows[row] if c.weapon == ""]
        if not pool:
            return
        target = max(pool, key=lambda c: c.strength)
        target.w_bonus += bonus
        target.w_immune = target.w_immune or immune
        target.weapon = card.name

    def _divine(self, p: int, ab: str, row: str) -> None:
        parts = ab.split(":")
        kind = parts[1] if len(parts) > 1 else ""
        single = "single" in parts

        if kind == "kill_top_all":
            for r in ROWS:
                self._kill_top(1 - p, r, ignore_hero=False)
        elif kind == "kill_all":
            for r in ROWS:
                cards = self.sides[1 - p].rows[r]
                doomed = [c for c in cards if c.ability != "hero"]
                for c in doomed:
                    cards.remove(c)
                    self.sides[1 - p].grave.append(c)
        elif kind == "kill_row_low" and row:
            limit = int(parts[2]) if len(parts) > 2 else 4
            cards = self.sides[1 - p].rows[row]
            doomed = [c for c in cards
                      if c.ability != "hero" and c.strength <= limit]
            for c in doomed:
                cards.remove(c)
                self.sides[1 - p].grave.append(c)
        elif kind == "kill_any" and row:
            self._kill_top(1 - p, row, ignore_hero=True)
        elif kind == "kill_row" and row:
            cards = self.sides[1 - p].rows[row]
            doomed = [c for c in cards if c.ability != "hero"]
            for c in doomed:
                cards.remove(c)
                self.sides[1 - p].grave.append(c)
        elif kind == "punish" and row:
            self._punish(1 - p, row, int(parts[2]) if len(parts) > 2 else 5)

        if not single:
            self._sacrifice(p)

    def _sacrifice(self, p: int) -> None:
        """Divine weapons are paid for with blood: lose your weakest warrior."""
        pool = [(c, r) for r in ROWS for c in self.sides[p].rows[r]
                if c.ability != "hero" and not c.illusion]
        if not pool:
            return
        card, row = min(pool, key=lambda cr: cr[0].strength)
        self.sides[p].rows[row].remove(card)
        self.sides[p].grave.append(card)

    def _turn_no(self) -> int:
        return len(self.log) + 1

    def _next_turn(self) -> None:
        for _ in range(10):
            # auto-pass empty hands
            for p in (0, 1):
                if not self.sides[p].passed and not self.sides[p].hand:
                    self.sides[p].passed = True
            if self.sides[0].passed and self.sides[1].passed:
                self._end_round()
                return
            if self.sides[self.current].passed:
                self.current = 1 - self.current
                continue
            return

    def _end_round(self) -> None:
        s = self.totals()
        self.last_board = [[self.row_total(p, r) for r in ROWS] for p in (0, 1)]
        winner = 0 if s[0] > s[1] else 1 if s[1] > s[0] else None
        self.round_scores.append((self.round, s[0], s[1], winner))
        self.points_total[0] += s[0]
        self.points_total[1] += s[1]
        if winner is not None:
            self.wins[winner] += 1

        # clear the board, keep hands
        for side in self.sides:
            for r in ROWS:
                side.rows[r].clear()
                side.horns[r] = False
            side.passed = False
        self.weather = {r: False for r in ROWS}
        self.blocked = {}
        self.locked = {}
        self.log.append((self.round, self._turn_no(), -1, None, "round-end", s))

        if self.wins[0] == 2 or self.wins[1] == 2 or self.round == 3:
            self.phase = "over"
            return
        self.round += 1
        # optional between-round draw (classic Gwent draws none, standalone
        # Gwent draws a few). More cards here makes the last round matter.
        if self.draw_between:
            for side in self.sides:
                for _ in range(self.draw_between):
                    if side.deck and len(side.hand) < 10:
                        side.hand.append(side.deck.pop())
        if winner is None:
            self.current = self.first
        elif self.lead_loser:
            self.current = 1 - winner
        else:
            self.current = winner
        self.first = self.current

    def match_winner(self) -> Optional[int]:
        if self.wins[0] != self.wins[1]:
            return 0 if self.wins[0] > self.wins[1] else 1
        if self.points_total[0] != self.points_total[1]:
            return 0 if self.points_total[0] > self.points_total[1] else 1
        return None

    def clone(self) -> "Game":
        return copy.deepcopy(self)


def new_game(faction_a, faction_b, seed: int = 0, budget: int = 160,
             draw_between: int = 0, lead_loser: bool = False,
             mulligan_count: int = 2) -> Game:
    rng = random.Random(seed)
    pairs = []
    for f in (faction_a, faction_b):
        pairs.append((f,) if isinstance(f, str) else tuple(f))
    sides = []
    for i, pair in enumerate(pairs):
        deck = [Card(d, i) for d in build_alliance_deck(pair, budget)]
        rng.shuffle(deck)
        side = Side(factions=pair, deck=deck)
        for _ in range(10):
            if side.deck:
                side.hand.append(side.deck.pop())
        sides.append(side)
    first = rng.randrange(2)
    return Game(
        sides=sides,
        weather={r: False for r in ROWS},
        current=first,
        round=1,
        wins=[0, 0],
        first=first,
        phase="round",
        round_scores=[],
        points_total=[0, 0],
        log=[],
        seed=seed,
        draw_between=draw_between,
        lead_loser=lead_loser,
        mulligan_count=mulligan_count,
        rng=rng,
    )


def describe(game: Game, p: int, action: tuple) -> str:
    if action[0] == "pass":
        return "PASS"
    _, idx, row = action
    card = game.sides[p].hand[idx]
    return f"{card.name} -> {row or '-'}"