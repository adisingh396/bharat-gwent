"""Command line for the Akshauhini simulator.

  python -m sim.cli play  --a hastinapura+anga --b panchala+matsya --seed 1
  python -m sim.cli stats --games 200 --budget 160 --draw 0
"""

from __future__ import annotations

import argparse
import statistics
from collections import Counter

try:
    from .engine import new_game, describe, ROWS
    from .ai import HeuristicAI, RandomAI, play_out
    from .cards import FACTION_NAMES, provision
except ImportError:  # allow `python sim/cli.py`
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from sim.engine import new_game, describe, ROWS
    from sim.ai import HeuristicAI, RandomAI, play_out
    from sim.cards import FACTION_NAMES, provision

KINGDOMS = list(FACTION_NAMES)

# the six coalition decks used by the batch runner: every kingdom appears once
PAIRS = [
    ("hastinapura", "anga"),        # Kaurava core
    ("madra", "sindhu"),
    ("gandhara", "trigarta"),
    ("pragjyotisha", "kamboja"),
    ("panchala", "matsya"),         # Pandava core
    ("magadha", "dvaraka"),
]

# all fifteen unordered matchups between those alliances
MATCHUPS = [(PAIRS[i], PAIRS[j])
            for i in range(len(PAIRS))
            for j in range(i + 1, len(PAIRS))]


def matchup(i: int) -> tuple[tuple, tuple]:
    a, b = MATCHUPS[i % len(MATCHUPS)]
    if (i // len(MATCHUPS)) % 2:
        return b, a
    return a, b


def parse_pair(text: str) -> tuple[str, ...]:
    parts = [p.strip() for p in text.split("+") if p.strip()]
    for p in parts:
        if p not in FACTION_NAMES:
            raise SystemExit(f"unknown kingdom '{p}'. choose from {', '.join(KINGDOMS)}")
    if not 1 <= len(parts) <= 2:
        raise SystemExit("an alliance is one or two kingdoms, e.g. hastinapura+anga")
    return tuple(parts)


def print_board(game, p: int, rows=None) -> None:
    name = game.sides[p].name
    vals = rows[p] if rows is not None else [game.row_total(p, r) for r in ROWS]
    parts = [f"{r} {v:>2}" for r, v in zip(ROWS, vals)]
    print(f"    {name:<22} " + "  ".join(parts) + f"   = {sum(vals)}")


def cmd_play(args) -> None:
    a, b = parse_pair(args.a), parse_pair(args.b)
    game = new_game(a, b, args.seed, budget=args.budget, draw_between=args.draw,
                    lead_loser=args.lead == "loser",
                    mulligan_count=args.mulligan)
    ais = [HeuristicAI(args.seed * 2 + 1, mulligan=args.mulligan_mode),
           HeuristicAI(args.seed * 2 + 2, mulligan=args.mulligan_mode)]
    opening = [list(game.sides[p].hand) for p in (0, 1)]
    swaps = []
    for ai, p in zip(ais, (0, 1)):
        idx = ai.choose_mulligan(game, p, game.mulligan_count)
        swaps.append(game.mulligan(p, idx))

    print()
    print("=" * 78)
    print(f"  AKSHAUHINI SIM   {game.sides[0].name}  vs  {game.sides[1].name}"
          f"   (seed {args.seed}, budget {args.budget}, draw {args.draw},"
          f" lead {args.lead})")
    print("=" * 78)
    print(f"  first player: {game.sides[game.first].name}")
    for p in (0, 1):
        dealt = ", ".join(c.name for c in opening[p])
        print(f"  {game.sides[p].name:<22} opening: {dealt}")
    for p in (0, 1):
        returned, drawn = swaps[p]
        if returned:
            print(f"  {game.sides[p].name:<22} mulligan -"
                  f"{', '.join(c.name for c in returned)}"
                  f"  +{', '.join(c.name for c in drawn)}")
        else:
            print(f"  {game.sides[p].name:<22} mulligan: keeps all ten")
    for p in (0, 1):
        cost = sum(provision(c.d) for c in game.sides[p].hand)
        print(f"  {game.sides[p].name:<22} hand {len(game.sides[p].hand):>2}"
              f"   provisions in hand {cost}")
    print()

    last_round = 0
    turn = 0
    while game.phase != "over" and turn < 400:
        p = game.current
        if game.sides[p].passed:
            game._next_turn()
            continue
        if game.round != last_round:
            last_round = game.round
            print(f"  -- ROUND {game.round} " + "-" * 60)
            print(f"  {'#':<4}{'player':<24}{'action':<30}{'score':>12}")
        action = ais[p].choose(game, p)
        text = describe(game, p, action)
        rounds_before = len(game.round_scores)
        game.play(action)
        turn += 1
        if len(game.round_scores) > rounds_before:
            rnd, s0, s1, winner = game.round_scores[-1]
            who = "draw" if winner is None else ("0" if winner == 0 else "1")
            print(f"  {turn:<4}{game.sides[p].name:<24}{text:<30}{s0:>5} : {s1:<5}")
            print(f"       round {rnd} ends  {s0} - {s1}   (side {who})")
            print()
            if game.phase != "over":
                print_board(game, 0, game.last_board)
                print_board(game, 1, game.last_board)
                print()
            continue
        my, op = game.totals()
        print(f"  {turn:<4}{game.sides[p].name:<24}{text:<30}{my:>5} : {op:<5}")

    print("=" * 78)
    print("  SCORING LINE")
    print("=" * 78)
    for rnd, s0, s1, winner in game.round_scores:
        who = "-" if winner is None else ("0" if winner == 0 else "1")
        print(f"    R{rnd}: {game.sides[0].name:<22}{s0:>4} - {s1:<4}"
              f" {game.sides[1].name:<22} winner {who}")
    w = game.match_winner()
    print()
    if w is None:
        print(f"    DRAW   {game.points_total[0]} - {game.points_total[1]}"
              f"   (rounds {game.wins[0]}-{game.wins[1]})")
    else:
        print(f"    {game.sides[w].name} wins   rounds {game.wins[w]}-{game.wins[1 - w]}"
              f"   points {game.points_total[w]}-{game.points_total[1 - w]}")
    print()


def _plays_per_round(game):
    plays = {}
    for rnd, _turn, p, card, _info, _t in game.log:
        if p < 0 or card is None:
            continue
        plays.setdefault(rnd, [0, 0])[p] += 1
    return plays


def cmd_stats(args) -> None:
    games = []
    for i in range(args.games):
        a, b = matchup(i)
        game = new_game(a, b, seed=i + 1, budget=args.budget,
                        draw_between=args.draw, lead_loser=args.lead == "loser",
                        mulligan_count=args.mulligan)
        ais = [HeuristicAI(i * 2 + 1, mulligan=args.mulligan_mode),
               HeuristicAI(i * 2 + 2, mulligan=args.mulligan_mode)]
        games.append(play_out(game, ais))

    ended_two = sum(1 for g in games if len(g.round_scores) == 2)
    ended_three = sum(1 for g in games if len(g.round_scores) == 3)
    draws = sum(1 for g in games if g.match_winner() is None)
    margins = [abs(s0 - s1) for g in games for _, s0, s1, _ in g.round_scores]
    per_round = []
    dry_rounds = 0
    for g in games:
        for rnd, counts in _plays_per_round(g).items():
            per_round.extend(counts)
            if min(counts) == 0:
                dry_rounds += 1
    turns = [len([e for e in g.log if e[2] >= 0]) for g in games]
    first_wins = sum(1 for g in games
                     if g.match_winner() is not None and g.match_winner() == g.first)

    kingdom_games: Counter = Counter()
    kingdom_wins: Counter = Counter()
    for g in games:
        w = g.match_winner()
        for p in (0, 1):
            for f in g.sides[p].factions:
                kingdom_games[f] += 1
                if w == p:
                    kingdom_wins[f] += 1

    print()
    print("=" * 78)
    print(f"  BATCH: {len(games)} games, heuristic vs heuristic,"
          f" budget {args.budget}, draw {args.draw}")
    print("=" * 78)
    print(f"  ended in two rounds         {ended_two:>4}  {ended_two/len(games):6.1%}")
    print(f"  went to a decider           {ended_three:>4}  {ended_three/len(games):6.1%}")
    print(f"  drawn matches               {draws:>4}  {draws/len(games):6.1%}")
    print(f"  avg round margin            {statistics.mean(margins):6.1f}")
    print(f"  median round margin         {statistics.median(margins):6.1f}")
    print(f"  biggest round margin        {max(margins):>4}")
    print(f"  dry-pass rounds (a side 0)  {dry_rounds:>4}")
    print(f"  avg cards played per round  {statistics.mean(per_round):6.1f}")
    print(f"  avg actions per game        {statistics.mean(turns):6.1f}")
    print(f"  first player won the match  {first_wins:>4}  {first_wins/len(games):6.1%}")
    print()
    print(f"  {'kingdom':<14}{'decks':>7}{'wins':>7}{'rate':>8}")
    for f in KINGDOMS:
        n = kingdom_games[f]
        w = kingdom_wins[f]
        rate = (w / n) if n else 0.0
        print(f"  {FACTION_NAMES[f]:<14}{n:>7}{w:>7}{rate:>8.1%}")

    hw = 0
    trials = max(50, args.games // 2)
    for i in range(trials):
        a, b = matchup(i + 1)
        game = new_game(a, b,
                        seed=10_000 + i, budget=args.budget,
                        draw_between=args.draw, lead_loser=args.lead == "loser",
                        mulligan_count=args.mulligan)
        ais = [HeuristicAI(i, mulligan=args.mulligan_mode), RandomAI(i)]
        if i % 2:
            ais = [RandomAI(i), HeuristicAI(i)]
        game = play_out(game, ais)
        w = game.match_winner()
        if w is not None and ais[w].name == "heuristic":
            hw += 1
    print()
    print(f"  heuristic vs random: {hw}/{trials} = {hw/trials:.1%}")
    print()
    _verdict(ended_two, margins, per_round, kingdom_wins, kingdom_games,
             first_wins, len(games))
    print()


def _verdict(ended_two, margins, per_round, kingdom_wins, kingdom_games,
             first_wins, n) -> None:
    print("  VERDICT")
    flags = []
    if statistics.mean(per_round) < 3.5:
        flags.append("few cards per round: pass wars")
    med = statistics.median(margins)
    if med < 3:
        flags.append("median round margin under 3: rounds feel like coin flips")
    if med > 20:
        flags.append("median round margin over 20: blowouts, not tactics")
    rates = [kingdom_wins[f] / kingdom_games[f]
             for f in kingdom_games if kingdom_games[f] >= 20]
    if rates and (max(rates) - min(rates)) > 0.20:
        flags.append("kingdom win rates spread more than 20 points")
    fp = first_wins / n
    if not (0.35 <= fp <= 0.65):
        flags.append(f"first player wins {fp:.0%}: structural turn-order problem")
    if stats_ok(ended_two, n):
        pass
    if not flags:
        print("    healthy: rounds contested, margins moderate, kingdoms close,"
              " turn order neutral.")
    else:
        for f in flags:
            print(f"    - {f}")


def stats_ok(ended_two, n) -> bool:
    return 0.10 <= ended_two / n <= 0.70


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="sim")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("play", help="one verbose game")
    p.add_argument("--a", default="hastinapura+anga")
    p.add_argument("--b", default="panchala+matsya")
    p.add_argument("--seed", type=int, default=1)
    p.set_defaults(func=cmd_play)

    s = sub.add_parser("stats", help="batch metrics")
    s.add_argument("--games", type=int, default=200)
    s.set_defaults(func=cmd_stats)

    for sp in (p, s):
        sp.add_argument("--budget", type=int, default=160)
        sp.add_argument("--draw", type=int, default=0,
                        help="cards drawn between rounds (0 = classic Gwent)")
        sp.add_argument("--lead", choices=("winner", "loser"), default="winner",
                        help="who leads the next round")
        sp.add_argument("--mulligan", type=int, default=2,
                        help="cards you may redraw at the start")
        sp.add_argument("--mulligan-mode", choices=("smart", "random", "none"),
                        default="smart", help="how the bot picks its redraws")

    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()