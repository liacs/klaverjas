from .cards import Card, Rank, Suit


meld_20 = []
meld_50 = []
meld_100 = []
for suit in Suit:
    for idx in range(6):
        meld_20.append({Card(suit, Rank(rank))
                        for rank in range(idx, idx + 3)})
    for idx in range(5):
        meld_50.append({Card(suit, Rank(rank))
                        for rank in range(idx, idx + 4)})
for rank in Rank:
    meld_100.append({Card(suit, rank) for suit in Suit})


def meld_points(trick, trump_suit):
    for meld in meld_100:
        if meld <= set(trick):
            return 100

    points = 0
    royal = {Card(trump_suit, Rank.QUEEN), Card(trump_suit, Rank.KING)}
    if royal <= set(trick):
        points = 20

    for meld in meld_50:
        if meld <= set(trick):
            return points + 50
    for meld in meld_20:
        if meld <= set(trick):
            return points + 20
    return points
