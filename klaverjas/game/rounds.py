from .tricks import Trick


def team(player):
    return player % 2


def other_team(player):
    return (player + 1) % 2


class Round:
    def __init__(self, lead, eldest, trump_suit):
        self._lead = lead
        self._eldest = eldest
        self._trump_suit = trump_suit
        self._tricks = [Trick(eldest)]
        self._points = [0, 0]
        self._meld = [0, 0]

    def complete_trick(self):
        trick = self._tricks[-1]
        if trick.is_complete():
            winner = trick.winner(self._trump_suit)
            points = trick.points(self._trump_suit)
            meld = trick.meld(self._trump_suit)

            self._points[team(winner)] += points
            self._meld[team(winner)] += meld

            if len(self._tricks) == 8:
                self._points[team(winner)] += 10
                us = team(self._lead)
                them = other_team(self._lead)

                if (self._points[us] + self._meld[us] <=
                        self._points[them] + self._meld[them]):
                    self._points[them] = 162
                    self._meld[them] += self._meld[us]
                    self._points[us] = 0
                    self._meld[us] = 0
                elif self.is_pit():
                    self._meld[us] += 100
            else:
                self._tricks.append(Trick(winner))
            return True
        return False

    def current_trick(self):
        return self._tricks[-1]

    def is_complete(self):
        return len(self._tricks) == 8 and self._tricks[-1].is_complete()

    def is_pit(self):
        for trick in self._tricks:
            if team(self._lead) != team(trick.winner(self._trump_suit)):
                return False
        return True

    def lead(self):
        return self._lead

    def legal_moves(self, hand):
        trick = self._tricks[-1]
        leading_suit = trick.leading_suit()

        if leading_suit is None:
            return hand

        follow = []
        trump = []
        trump_higher = []
        highest_trump_value = trick.highest_trump(
            self._trump_suit).order(self._trump_suit)
        for card in hand:
            if card.suit() == leading_suit:
                follow.append(card)
            if card.suit() == self._trump_suit:
                trump.append(card)
                if card.order(self._trump_suit) > highest_trump_value:
                    trump_higher.append(card)

        if follow and leading_suit != self._trump_suit:
            return follow
        return trump_higher or trump or hand

    def meld(self):
        return self._meld

    def play_card(self, card):
        trick = self._tricks[-1]
        trick.add(card)

    def points(self):
        return self._points

    def to_play(self):
        return self._tricks[-1].to_play()

    def trump_suit(self):
        return self._trump_suit
