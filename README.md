# bharat-gwent

A small simulator that plays a Gwent-style card game about the Mahabharata, so I can
test whether the design is any fun before building a real game.

Two bots play each other. The terminal shows the score after every card, and a batch mode
reports whether rounds are contested or lopsided.

## Run it

```
python -m sim.cli play --a hastinapura+anga --b panchala+matsya --seed 11 --draw 2 --lead loser
python -m sim.cli stats --games 240 --draw 2 --lead loser
```

No dependencies. Python 3.10 or newer. Run everything from the repo root.

Other tools:

```
python -m sim._selftest              # checks every card effect
python -m sim._astras --games 200    # which specials get played and what they swing
python -m sim._matrix --games 60     # kingdom vs kingdom
python -m sim._duel --a hastinapura+anga --b hastinapura+gandhara --games 100
python -m sim._balance               # deck strength and card costs
```

## The game

Three rows, three rounds, win two. Ten cards at the start, one card per turn, pass when
you want. Same skeleton as Gwent.

Decks are built from alliances. You pick two kingdoms out of twelve, because Kurukshetra
was two coalitions. The kingdoms are Hastinapura, Anga, Panchala, Matsya, Madra, Trigarta,
Kamboja, Magadha, Sindhu, Gandhara, Pragjyotisha and Dvaraka. Every card costs
"provisions" and a deck has 160 of them, so taking Bhishma means giving up three mid cards.
Each kingdom has to supply at least 8 cards, which keeps an alliance a real blend.

The kingdoms are not equal. On their own, Magadha wins about 72% of games and Madra about
30%. Small kingdoms need an ally, and even then they drag the alliance down. That is
deliberate.

Special cards come in three ranks. A shaastra is a physical weapon and attaches to one of
your warriors. An astra is an invoked weapon that hits the board. A divine weapon is one
per deck and costs you a warrior when you use it.

Astras only work when the board suits them. Varunastra needs weather up, Vasavi Shakti
needs an enemy hero, Brahmashirsha needs an enemy row worth 15 points. A hand can be full
of dead cards, which is why the opening redraw matters at all.

## What the numbers say

Classic Gwent rules, with no draw between rounds and the round winner leading the next,
gave the first player 91% wins. Adding a two-card draw between rounds and letting the
round loser lead brought that down to about 45%. Without both changes the coin toss
decides the game.

A good opening redraw is worth about 12 points of win rate over a random one.

## Limits

There is one bot, so "healthy" means healthy against this opponent. The bot does not price
cards, so it will trade a 17-provision weapon for six points. The provision formula is
rough, and the top cards need hand pricing before this is a real set.