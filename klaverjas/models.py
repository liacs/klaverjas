from datetime import datetime
from hashlib import md5
import random
import uuid

from flask_login import UserMixin
from flask_socketio import emit
from werkzeug.security import generate_password_hash, check_password_hash

from klaverjas import db, login
from klaverjas.game.cards import (Card, Rank, Suit, card_from_dict,
                                  suit_from_label)
from klaverjas.game.rounds import Round


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer,
                               db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer,
                               db.ForeignKey('user.id')))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship('User', secondary=followers,
                               primaryjoin=(followers.c.follower_id == id),
                               secondaryjoin=(followers.c.followed_id == id),
                               backref=db.backref('followers', lazy='dynamic'),
                               lazy='dynamic')

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __str__(self):
        return self.username

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def to_dict(self):
        return {'avatar': self.avatar(60), 'name': str(self)}


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Game(db.Model):
    id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()),
                   primary_key=True)
    north_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    east_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    south_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    west_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    north = db.relationship('User', primaryjoin='Game.north_id == User.id',
                            backref='games_north')
    east = db.relationship('User', primaryjoin='Game.east_id == User.id',
                           backref='games_east')
    south = db.relationship('User', primaryjoin='Game.south_id == User.id',
                            backref='games_south')
    west = db.relationship('User', primaryjoin='Game.west_id == User.id',
                           backref='games_west')

    def __init__(self, north, east, south, west):
        if len(set([north, east, south, west])) == 4:
            self.north = north
            self.east = east
            self.south = south
            self.west = west

    def has_user(self, user):
        return user in [self.north, self.east, self.south, self.west]

    def init(self):
        self._players = [self.north, self.east, self.south, self.west]
        self._rounds = []
        self._scores = [0, 0]
        self._sids = [None, None, None, None]
        self.deal()

    def deal(self):
        deck = [Card(Suit(idx // 8), Rank(idx % 8)) for idx in range(32)]
        random.shuffle(deck)
        self._hands = [deck[0:8], deck[8:16], deck[16:24], deck[24:32]]
        self._trump_suit = random.choice(list(Suit))
        self._bids = 0
        self.notify_all(self.notify_deal)
        self.notify(self.to_play(), self.notify_ask_bid)

    def dealer(self):
        if self._bids is not None:
            return self._players[len(self._rounds) % 4]
        return self._players[(len(self._rounds) - 1) % 4]

    def event_bid(self, player, trump_suit):
        if (self._bids is not None and player == self.to_play()):
            lead = self._players.index(player)
            eldest = (self._players.index(self.dealer()) + 1) % 4
            self._bids = None
            self._trump_suit = suit_from_label(trump_suit)
            self._rounds.append(Round(lead, eldest, self._trump_suit))
            self.notify_all(self.notify_bid, player)
            self.notify(self.to_play(), self.notify_ask_play)

    def event_join(self, player, sid):
        idx = self._players.index(player)
        self._sids[idx] = sid
        self.notify(player, self.notify_init)
        if self._bids is not None:
            self.notify(player, self.notify_deal)
            if player == self.to_play():
                if self._bids < 4:
                    self.notify(player, self.notify_ask_bid)
                else:
                    self.notify(player, self.notify_force_bid)
        else:
            self.notify(player, self.notify_trick)
            if player == self.to_play():
                self.notify(player, self.notify_ask_play)

    def event_pass(self, player):
        if (self._bids is not None and self._bids < 4 and
                player == self.to_play()):
            self._bids += 1
            self.notify_all(self.notify_pass, player)
            if self._bids < 4:
                self.notify(self.to_play(), self.notify_ask_bid)
            else:
                self.notify(self.to_play(), self.notify_force_bid)

    def event_play(self, player, card_dict):
        if self._bids is None and player == self.to_play():
            idx = self._players.index(player)
            round = self._rounds[-1]
            moves = round.legal_moves(self._hands[idx])
            card = card_from_dict(card_dict)
            if card not in moves:
                return
            self._hands[idx].remove(card)
            round.play_card(card)
            self.notify_all(self.notify_play, {'card': card,
                                               'player': player})
            trick = round.current_trick()
            meld = trick.meld(self._trump_suit)
            winner = trick.winner(self._trump_suit)
            if round.complete_trick():
                self.notify_all(self.notify_take_trick, {'meld': meld,
                                                         'winner': winner})
                if round.is_complete():
                    self._scores[0] += round.points()[0] + round.meld()[0]
                    self._scores[1] += round.points()[1] + round.meld()[1]
                    self.notify_all(self.notify_score,
                                    {'scores': round.points(),
                                     'meld': round.meld()})
                    if len(self._rounds) < 16:
                        self.deal()
                        return
            self.notify(self.to_play(), self.notify_ask_play)

    def notify(self, player, event, data=None):
        idx = self._players.index(player)
        sid = self._sids[idx]
        if sid is not None:
            label, data = event(player, data)
            emit(label, data, room=sid)

    def notify_all(self, event, data=None):
        for player in self._players:
            self.notify(player, event, data)

    def notify_ask_bid(self, player, _):
        return 'ask_bid', {'trump_suit': str(self._trump_suit)}

    def notify_ask_play(self, player, _):
        idx = self._players.index(player)
        round = self._rounds[-1]
        moves = round.legal_moves(self._hands[idx])
        return 'ask_play', {'legal_moves': [card.to_dict() for card in moves]}

    def notify_bid(self, _, data):
        return 'bid', {'player': str(data),
                       'to_play': str(self.to_play()),
                       'trump_suit': str(self._trump_suit)}

    def notify_deal(self, player, _):
        idx = self._players.index(player)
        return 'deal', {'hand': [card.to_dict() for card in self._hands[idx]],
                        'dealer': str(self.dealer()),
                        'to_play': str(self.to_play())}

    def notify_force_bid(self, player, _):
        return 'force_bid', {'trump_suits': [str(suit) for suit in Suit
                                             if suit != self._trump_suit]}

    def notify_init(self, player, _):
        idx = self._players.index(player)
        return 'init', {'north': self._players[(idx + 2) % 4].to_dict(),
                        'east': self._players[(idx + 3) % 4].to_dict(),
                        'south': player.to_dict(),
                        'west': self._players[(idx + 1) % 4].to_dict()}

    def notify_pass(self, _, data):
        return 'pass', {'player': str(data),
                        'to_play': str(self.to_play())}

    def notify_play(self, _, data):
        return 'play', {'card': data.get('card').to_dict(),
                        'player': str(data.get('player')),
                        'to_play': str(self.to_play())}

    def notify_score(self, _, data):
        return 'score', data

    def notify_take_trick(self, _, data):
        return 'take_trick', data

    def notify_trick(self, player, _):
        round = self._rounds[-1]
        trick = round.current_trick()
        lead = trick.lead()
        data = []
        for idx, card in enumerate(trick.cards()):
            data.append({'player': str(self._players[(lead + idx) % 4]),
                         'card': card.to_dict()})
        idx = self._players.index(player)
        return 'trick', {'trick': data,
                         'hand': [card.to_dict() for card in self._hands[idx]],
                         'north': len(self._hands[0]),
                         'east': len(self._hands[1]),
                         'west': len(self._hands[3]),
                         'to_play': str(self.to_play()),
                         'trump_suit': str(self._trump_suit),
                         'dealer': str(self.dealer()),
                         'lead': str(self._players[round.lead()])}

    def to_play(self):
        if self._bids is not None:
            idx = self._players.index(self.dealer())
            return self._players[(idx + self._bids + 1) % 4]
        else:
            idx = self._rounds[-1].to_play()
            return self._players[idx]
