from enum import Enum, unique


@unique
class Suit(Enum):
    SPADES = 0
    HEARTS = 1
    CLUBS = 2
    DIAMONDS = 3

    def __str__(self):
        return ['spades', 'hearts', 'clubs', 'diamonds'][self.value]


@unique
class Rank(Enum):
    SEVEN = 0
    EIGHT = 1
    NINE = 2
    TEN = 3
    JACK = 4
    QUEEN = 5
    KING = 6
    ACE = 7

    def __str__(self):
        return ['7', '8', '9', '10', 'J', 'Q', 'K', 'A'][self.value]


class Card:
    def __init__(self, suit, rank):
        if not isinstance(suit, Suit):
            raise TypeError
        if not isinstance(rank, Rank):
            raise TypeError
        self._suit = suit
        self._rank = rank

    def __eq__(self, other):
        return self._suit == other._suit and self._rank == other._rank

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return '{}{}'.format(self._suit, self._rank)

    def order(self, trump_suit):
        if self._suit == trump_suit:
            return [8, 9, 14, 12, 15, 10, 11, 13][self._rank.value]
        return [0, 1, 2, 6, 3, 4, 5, 7][self._rank.value]

    def points(self, trump_suit):
        if self._suit == trump_suit:
            return [0, 0, 14, 10, 20, 3, 4, 11][self._rank.value]
        return [0, 0, 0, 10, 2, 3, 4, 11][self._rank.value]

    def rank(self):
        return self._rank

    def suit(self):
        return self._suit

    def to_dict(self):
        return {'rank': str(self._rank), 'suit': str(self._suit)}


def card_from_dict(dict):
    return Card(suit_from_label(dict['suit']), rank_from_label(dict['rank']))


def suit_from_label(label):
    return Suit(['spades', 'hearts', 'clubs', 'diamonds'].index(label))


def rank_from_label(label):
    return Rank(['7', '8', '9', '10', 'J', 'Q', 'K', 'A'].index(label))
