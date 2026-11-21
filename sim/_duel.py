"""Duel two specific alliance decks N times.

  python -m sim._duel --a hastinapura+anga --b hastinapura+gandhara --games 100
"""

from .engine import new_game
from .ai import HeuristicAI, play_out


def parse(text: str) -> tuple[str, ...]:
    return tuple(p.strip() for p in text.split("+") if p.strip())


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default="hastinapura+anga")
    ap.add_argument("--b", default="hastinapura+gandhara")
    ap.add_argument("--games", type=int, default=100)
    ap.add_argument("--budget", type=int, default=160)
    ap.add_argument("--draw", type=int, default=2)
    ap.add_argument("--lead", default="loser", choices=("winner", "loser"))
    ap.add_argument("--mulligan", type=int, default=2)
    ap.add_argument("--ma", default="smart", choices=("smart", "random", "none"))
    ap.add_argument("--mb", default="smart", choices=("smart", "random", "none"))
    args = ap.parse_args()

    a, b = parse(args.a), parse(args.b)
    wa = wb = d = 0
    for i in range(args.games):
        game = new_game(a, b, seed=i + 1, budget=args.budget,
                        draw_between=args.draw, lead_loser=args.lead == "loser",
                        mulligan_count=args.mulligan)
        ais = [HeuristicAI(i * 2 + 1, mulligan=args.ma),
               HeuristicAI(i * 2 + 2, mulligan=args.mb)]
        game = play_out(game, ais)
        m = game.match_winner()
        if m is None:
            d += 1
        elif m == 0:
            wa += 1
        else:
            wb += 1
    n = args.games
    print(f"  {'+'.join(a) + ' [' + args.ma + ']':<34} {wa:>4}  {wa / n:>6.1%}")
    print(f"  {'+'.join(b) + ' [' + args.mb + ']':<34} {wb:>4}  {wb / n:>6.1%}")
    if d:
        print(f"  {'draws':<34} {d:>4}  {d / n:>6.1%}")


if __name__ == "__main__":
    main()