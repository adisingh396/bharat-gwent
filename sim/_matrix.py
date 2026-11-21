"""Head-to-head matrix: each kingdom alone against each other, same AI."""

from .cards import FACTION_NAMES
from .engine import new_game
from .ai import HeuristicAI, play_out

KINGDOMS = list(FACTION_NAMES)


def run(a: str, b: str, games: int, budget: int, draw: int, lead: str) -> tuple[int, int, int]:
    w = d = 0
    for i in range(games):
        game = new_game((a,), (b,), seed=i + 1, budget=budget,
                        draw_between=draw, lead_loser=lead == "loser")
        ais = [HeuristicAI(i * 2 + 1), HeuristicAI(i * 2 + 2)]
        game = play_out(game, ais)
        m = game.match_winner()
        if m is None:
            d += 1
        elif m == 0:
            w += 1
    return w, games - w - d, d


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--games", type=int, default=100)
    ap.add_argument("--budget", type=int, default=160)
    ap.add_argument("--draw", type=int, default=2)
    ap.add_argument("--lead", default="loser", choices=("winner", "loser"))
    args = ap.parse_args()

    print(f"{'':<13}" + "".join(f"{FACTION_NAMES[k][:9]:>11}" for k in KINGDOMS))
    totals = {k: [0, 0] for k in KINGDOMS}
    for a in KINGDOMS:
        row = f"{FACTION_NAMES[a]:<13}"
        for b in KINGDOMS:
            if a == b:
                row += f"{'-':>11}"
                continue
            w, _l, _d = run(a, b, args.games, args.budget, args.draw, args.lead)
            totals[a][0] += w
            totals[a][1] += args.games
            row += f"{w / args.games:>10.0%}"
        print(row)
    print()
    for k in KINGDOMS:
        w, n = totals[k]
        print(f"  {FACTION_NAMES[k]:<13} overall {w}/{n} = {w / n:.1%}")


if __name__ == "__main__":
    main()