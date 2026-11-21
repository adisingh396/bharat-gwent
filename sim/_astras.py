"""Which specials actually get played, and what they are worth.

  python -m sim._astras --games 200
"""

from collections import defaultdict

from .engine import new_game
from .ai import HeuristicAI, play_out


def main() -> None:
    import argparse
    from .cli import matchup
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=200)
    ap.add_argument("--budget", type=int, default=200)
    ap.add_argument("--draw", type=int, default=2)
    ap.add_argument("--lead", default="loser", choices=("winner", "loser"))
    args = ap.parse_args()

    stats = defaultdict(lambda: [0, 0.0, 0.0])
    for i in range(args.games):
        a, b = matchup(i)
        game = new_game(a, b, seed=i + 1, budget=args.budget,
                        draw_between=args.draw, lead_loser=args.lead == "loser")
        ais = [HeuristicAI(i * 2 + 1), HeuristicAI(i * 2 + 2)]
        game = play_out(game, ais)
        prev = (0, 0)
        for _rnd, _turn, p, card, _info, totals in game.log:
            if p < 0:
                prev = totals
                continue
            if card is not None and card.special:
                row = stats[card.name]
                row[0] += 1
                row[1] += totals[p] - prev[p]
                row[2] += totals[1 - p] - prev[1 - p]
            prev = totals

    print()
    print(f"  {'special':<22}{'plays':>7}{'own pts':>9}{'enemy pts':>11}")
    print("  " + "-" * 47)
    for name, (n, mine, theirs) in sorted(stats.items(),
                                          key=lambda kv: -kv[1][0]):
        print(f"  {name:<22}{n:>7}{mine / n:>9.1f}{theirs / n:>11.1f}")
    print()
    print("  own pts   = points the caster gained immediately")
    print("  enemy pts = points the caster stripped from the opponent")


if __name__ == "__main__":
    main()