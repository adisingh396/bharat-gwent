"""Balance probe: deck strength and the most cost-efficient cards per kingdom."""

from .cards import (faction_pool, provision, _unit_value, FACTION_NAMES,
                    build_alliance_deck)


def main() -> None:
    for f in FACTION_NAMES:
        print()
        print(FACTION_NAMES[f])
        pool = faction_pool(f)
        seen = []
        for c in sorted(pool, key=lambda c: _unit_value(c) / provision(c),
                        reverse=True):
            if any(x.name == c.name for x in seen):
                continue
            seen.append(c)
            if len(seen) > 8:
                break
        for c in seen:
            print(f"   {c.name:<22} str {c.strength:>2}  prov {provision(c):>2}"
                  f"  ratio {_unit_value(c) / provision(c):.2f}  {c.ability}")
        deck = build_alliance_deck((f,))
        print(f"   deck25: strength {sum(c.strength for c in deck)}"
              f"  cost {sum(provision(c) for c in deck)}")


if __name__ == "__main__":
    main()