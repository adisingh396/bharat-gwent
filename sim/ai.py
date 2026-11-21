"""Bots. The point of the simulator is to find out whether the game produces
real decisions, so the bar is: no card-advantage blindness, no automatic pass
wars, no over-committing."""

from __future__ import annotations

import random
from collections import Counter
from typing import Optional

from .engine import Game, new_game
from .cards import ROWS


MAX_SINGLE_CARD = 16  # the biggest swing one card can produce


class RandomAI:
    name = "random"

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)

    def choose_mulligan(self, game: Game, p: int, n: int = 2) -> list[int]:
        idx = list(range(len(game.sides[p].hand)))
        self.rng.shuffle(idx)
        return idx[:n]

    def choose(self, game: Game, p: int) -> tuple:
        return self.rng.choice(game.legal_actions(p))


class HeuristicAI:
    name = "heuristic"

    def __init__(self, seed: int = 0, aggression: float = 1.0,
                 mulligan: str = "smart"):
        self.rng = random.Random(seed)
        self.aggression = aggression
        self.mulligan_mode = mulligan

    # ---------- opening ----------

    def choose_mulligan(self, game: Game, p: int, n: int = 2) -> list[int]:
        """Pick cards to throw back. The replacements are blind.

        You keep bombs, spies and medics, and you dump dead cheap cards and
        copies beyond the bond cap. Everything else is a gamble.
        """
        side = game.sides[p]
        if self.mulligan_mode == "none" or n <= 0:
            return []
        if self.mulligan_mode == "random":
            idx = list(range(len(side.hand)))
            self.rng.shuffle(idx)
            return idx[:n]

        counts = Counter(c.name for c in (side.hand + side.deck))

        def keep(c) -> float:
            if c.ability == "hero":
                return 9.0
            if c.ability == "spy":
                return 9.0
            if c.ability == "medic":
                return 7.0
            if c.special:
                if c.ability.startswith("weapon:"):
                    parts = c.ability.split(":")
                    bonus = int(parts[1]) if len(parts) > 1 else 0
                    return 4.5 + bonus * 0.4 + (1.0 if "immune" in parts else 0.0)
                if c.ability.startswith("divine:"):
                    return 6.5 + (1.0 if c.d.requires else 0.0)
                if c.d.requires:
                    return 3.0   # situational: may be dead in this matchup
                return {
                    "horn": 6.0,
                    "scorch": 5.5,
                    "kill_top_all": 6.5,
                    "kill_any": 6.5,
                    "kill_top": 5.5,
                    "punish:5": 5.5,
                    "burn:3": 5.5,
                    "poison": 5.0,
                    "douse": 4.5,
                    "bounce:4": 4.5,
                    "reveal": 4.5,
                    "maya": 4.5,
                    "block": 4.0,
                    "purify": 3.0,
                    "clear": 2.5,
                }.get(c.ability, 3.5)
            v = c.strength + (1.5 if c.ability in ("morale", "bond") else 0.0)
            if c.ability == "bond" and counts[c.name] > 3:
                v -= 4.0  # copies past the multiplier cap are dead weight
            return v

        hand_vals = [keep(c) for c in side.hand]
        deck_vals = [keep(c) for c in side.deck]
        if not deck_vals:
            return []
        expected = sum(deck_vals) / len(deck_vals)
        # Only redraw when the card is worse than a random card from the deck.
        # Redrawing a weak card into an identical weak copy just loses tempo.
        order = sorted(range(len(side.hand)), key=lambda i: hand_vals[i])
        return [i for i in order[:n] if hand_vals[i] < expected - 1.5]

    # ---------- decision ----------

    def choose(self, game: Game, p: int) -> tuple:
        me, opp = game.sides[p], game.sides[1 - p]
        my, op = game.total(p), game.total(1 - p)

        if not me.hand:
            return ("pass", None, None)

        actions = game.legal_actions(p)
        plays = [a for a in actions if a[0] == "play"]

        # opponent has passed: win the round with the cheapest card that does it
        if opp.passed:
            if my > op:
                return ("pass", None, None)
            best = None
            for a in plays:
                g = self._sim(game, p, a)
                if g.total(p) > op:
                    card = me.hand[a[1]]
                    cost = 6 if card.special else card.strength
                    if best is None or cost < best[0]:
                        best = (cost, a)
            return best[1] if best else ("pass", None, None)

        if self._should_pass(game, p, my, op):
            return ("pass", None, None)

        best = None
        scored = []
        for a in plays:
            g = self._sim(game, p, a)
            delta = (g.total(p) - my) - (g.total(1 - p) - op)
            card = me.hand[a[1]]
            if card.ability == "spy":
                delta += 8.0 if game.round == 1 else 4.0
            if card.ability == "medic":
                delta += 2.0
            # opportunity cost of spending a big card. Cheap while behind
            # (you need the points), expensive while level or ahead.
            penalty = 0.02 if my < op else 0.10
            delta -= penalty * card.strength
            scored.append((delta, a))

        if not scored:
            return ("pass", None, None)
        scored.sort(key=lambda x: -x[0])
        # never spend a card for nothing: a wasted astra is worse than passing
        positive = [s for s in scored if s[0] > 0]
        if positive:
            return positive[0][1]
        if my >= op:
            return ("pass", None, None)
        return scored[0][1]

    # ---------- helpers ----------

    def _sim(self, game: Game, p: int, action: tuple) -> Game:
        g = game.clone()
        g.current = p
        g.play(action)
        return g

    def _potential(self, side) -> float:
        total = 0.0
        for c in side.hand:
            if c.special:
                continue
            if c.ability == "spy":
                continue
            total += c.strength
        return total

    def _should_pass(self, game: Game, p: int, my: int, op: int) -> bool:
        me, opp = game.sides[p], game.sides[1 - p]
        hand_left = len(me.hand)

        if hand_left == 0:
            return True

        spent = sum(1 for e in game.log
                    if e[0] == game.round and e[2] == p and e[3] is not None)
        opp_cards = self._opp_cards(game, p)

        # Round three is the decider: fight, unless sitting on a lead that
        # costs the opponent two cards to erase while I am shorter on cards.
        if game.round == 3:
            if my > op and my - op > MAX_SINGLE_CARD and hand_left < opp_cards:
                return True
            return False

        # Round two with a round already banked: dry pass only if actually ahead
        # on cards, otherwise the free concession just loses the card race.
        if game.round == 2 and game.wins[p] == 1:
            if hand_left >= opp_cards + 2:
                return True
            if spent >= 4 and my - op <= 10:
                return True
            return False

        # Round one: fight to a fixed budget. Both sides commit about the
        # same number of cards, so the round is contested rather than dumped.
        if game.round == 1:
            if spent >= 6:
                return True
            if op - my > self._potential(me) and hand_left <= 2:
                return True
            return False

        # Round two when the first round was lost: this one must be won.
        # Only fold if it is already out of reach.
        if op - my > self._potential(me) and hand_left <= 2:
            return True
        return False

    def _opp_cards(self, game: Game, p: int) -> int:
        """Estimate the opponent's hand from public information only."""
        opp = 1 - p
        played = sum(1 for e in game.log
                     if e[2] == opp and e[3] is not None)
        drawn = game.draw_between * (game.round - 1)
        return max(0, 10 + drawn - played)


def play_out(game: Game, ais: list, max_turns: int = 400) -> Game:
    for ai, p in zip(ais, (0, 1)):
        picked = ai.choose_mulligan(game, p, game.mulligan_count)
        game.mulligan(p, picked)
    turns = 0
    while game.phase != "over" and turns < max_turns:
        p = game.current
        if game.sides[p].passed:
            game._next_turn()
            continue
        action = ais[p].choose(game, p)
        game.play(action)
        turns += 1
    return game