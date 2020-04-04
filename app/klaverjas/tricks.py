from .cards import Card, Rank
from .meld import meld_points


class Trick:
    def __init__(self, lead):
        self._cards = []
        self._lead = lead

    def __str__(self):
        return '  '.join(str(card) for card in self._cards)

    def add(self, card):
        self._cards.append(card)

    def highest_trump(self, trump_suit):
        return max(self._cards,
                   default=Card(trump_suit, Rank.SEVEN).order(trump_suit),
                   key=lambda card: card.order(trump_suit))

    def is_complete(self):
        return len(self._cards) == 4

    def lead(self):
        return self._lead

    def leading_suit(self):
        if self._cards:
            return self._cards[0].suit()

    def meld(self, trump_suit):
        return meld_points(self._cards, trump_suit)

    def points(self, trump_suit):
        return sum(card.points(trump_suit) for card in self._cards)

    def to_play(self):
        return (self._lead + len(self._cards)) % 4

    def winner(self, trump_suit):
        highest = self._cards[0]
        for card in self._cards:
            if (card.order(trump_suit) > highest.order(trump_suit) and
                (card.suit() == self.leading_suit() or
                 card.suit() == trump_suit)):
                highest = card
        return (self._lead + self._cards.index(highest)) % 4
