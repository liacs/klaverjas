import random
from cards import Card, Rank, Suit
from rounds import Round


class Game:
    def __init__(self):
        self._players = ['north', 'east ', 'south', 'west ']
        self._rounds = []
        self._scores = [0, 0]

    def bid(self):
        round_nr = len(self._rounds) + 1
        eldest = round_nr % 4
        trump_suit = random.choice(list(Suit))

        print('round {}'.format(round_nr))
        print('score: {:4} vs {:4}'.format(self._scores[0], self._scores[1]))

        for idx, player in enumerate(self._players):
            print('trump: {}'.format(trump_suit))
            self.print_hand((eldest + idx) % 4)
            ans = input('1) play\n2) pass\nplay: ')
            if ans == '1':
                return (eldest + idx) % 4, trump_suit

        self.print_hand(eldest)
        for idx, suit in enumerate(Suit):
            if suit != trump_suit:
                print('{}) {}'.format(idx + 1, suit))
        idx = int(input('trump: ')) - 1
        return eldest, Suit(idx)

    def deal(self):
        deck = [Card(Suit(idx // 8), Rank(idx % 8)) for idx in range(32)]
        random.shuffle(deck)
        self._hands = [sorted(deck[0:8]), sorted(deck[8:16]),
                       sorted(deck[16:24]), sorted(deck[24:32])]

    def play(self):
        while len(self._rounds) < 16:
            self.play_round()
            round = self._rounds[-1]
            self._scores[0] += round.points()[0] + round.meld()[0]
            self._scores[1] += round.points()[1] + round.meld()[1]
        print('final score: {:4} vs {:4}'.format(self._scores[0],
                                                 self._scores[1]))

    def play_round(self):
        self.deal()
        lead, trump_suit = self.bid()
        eldest = (len(self._rounds) + 1) % 4
        round = Round(lead, eldest, trump_suit)
        self._rounds.append(round)
        while not round.is_complete():
            self.print_round(round)
            to_play = round.to_play()
            moves = round.legal_moves(self._hands[to_play])
            self.print_hand(to_play)
            for idx, card in enumerate(moves):
                print('{}) {}'.format(idx + 1, str(card)))
            idx = int(input('play: ')) - 1
            card = moves[idx]
            self._hands[to_play].remove(card)
            round.play_card(card)
        self.print_round(round)

    def print_hand(self, player):
        print('{}: '.format(self._players[player]) +
              '  '.join(str(card) for card in self._hands[player]))

    def print_round(self, round):
        tricks = round.tricks()
        points = round.points()
        meld = round.meld()
        print('{} plays {}'.format(self._players[round.lead()],
                                   round.trump_suit()))
        print('points: {:3} vs {:3}'.format(points[0], points[1]))
        print('meld  : {:3} vs {:3}'.format(meld[0], meld[1]))
        print('tricks:')
        for idx, trick in enumerate(tricks):
            print('    {} ({}): {}'.format(idx + 1,
                                           self._players[trick.lead()],
                                           str(trick)))
