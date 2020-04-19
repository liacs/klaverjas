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
        self._hands = [sorted(deck[0:8]), sorted(deck[8:16]),
                       sorted(deck[16:24]), sorted(deck[24:32])]
        self._trump_suit = random.choice(list(Suit))
        self._bids = 0
        self.event_deal()
        self.event_ask_bid()

    def dealer(self):
        if self._bids is not None:
            return self._players[len(self._rounds) % 4]
        return self._players[(len(self._rounds) - 1) % 4]

    def event_ask_bid(self):
        idx = self._players.index(self.to_play())
        sid = self._sids[idx]
        if sid is not None:
            emit('ask_bid', {'trump_suit': str(self._trump_suit)}, room=sid)

    def event_ask_play(self):
        idx = self._players.index(self.to_play())
        sid = self._sids[idx]
        if sid is not None:
            moves = self._rounds[-1].legal_moves(self._hands[idx])
            emit('ask_play',
                 {'legal_moves': [card.to_dict() for card in moves]},
                 room=sid)

    def event_bid(self, user, trump_suit):
        if self._bids is not None and user == self.to_play():
            lead = self._players.index(user)
            eldest = (self._players.index(self.dealer()) + 1) % 4
            self._bids = None
            self._trump_suit = suit_from_label(trump_suit)
            self._rounds.append(Round(lead, eldest, self._trump_suit))
            for idx, player in enumerate(self._players):
                sid = self._sids[idx]
                if sid is not None:
                    emit('bid',
                         {'player': str(user),
                          'to_play': str(self.to_play()),
                          'trump_suit': str(self._trump_suit)},
                         room=sid)
            self.event_ask_play()

    def event_deal(self):
        for idx, player in enumerate(self._players):
            sid = self._sids[idx]
            if sid is not None:
                emit('deal',
                     {'hand': [card.to_dict() for card in self._hands[idx]],
                      'dealer': str(self.dealer()),
                      'to_play': str(self.to_play())},
                     room=sid)

    def event_force_bid(self):
        idx = self._players.index(self.to_play())
        sid = self._sids[idx]
        if sid is not None:
            emit('force_bid',
                 {'trump_suits': [str(suit) for suit in Suit
                                  if suit != self._trump_suit]},
                 room=sid)

    def event_join(self, user, sid):
        try:
            idx = self._players.index(user)
        except ValueError:
            return
        self._sids[idx] = sid
        emit('init',
             {'north': self._players[(idx + 2) % 4].to_dict(),
              'east': self._players[(idx + 3) % 4].to_dict(),
              'south': user.to_dict(),
              'west': self._players[(idx + 1) % 4].to_dict()},
             room=sid)
        self.event_deal()
        if self._bids is not None:
            if self._bids < 4:
                self.event_ask_bid()
            else:
                self.event_force_bid()
        else:
            self.event_ask_play()
            # TODO: state

    def event_pass(self, user):
        if (self._bids is not None and self._bids < 4 and
                user == self.to_play()):
            self._bids += 1
            for idx, player in enumerate(self._players):
                sid = self._sids[idx]
                if sid is not None:
                    emit('pass',
                         {'player': str(user),
                          'to_play': str(self.to_play())},
                         room=sid)
            if self._bids == 4:
                self.event_force_bid()
            self.event_ask_bid()

    def event_play(self, user, card_dict):
        if self._bids is None and user == self.to_play():
            idx = self._players.index(user)
            round = self._rounds[-1]
            moves = round.legal_moves(self._hands[idx])
            card = card_from_dict(card_dict)
            if card not in moves:
                return
            self._hands[idx].remove(card)
            round.play_card(card)
            for idx, player in enumerate(self._players):
                sid = self._sids[idx]
                if sid is not None:
                    emit('play',
                         {'player': str(user),
                          'to_play': str(self.to_play()),
                          'card': card.to_dict()},
                         room=sid)
            if round.complete_trick():
                self.event_take_trick()
                if round.is_complete():
                    self._scores[0] += round.points()[0] + round.meld()[0]
                    self._scores[1] += round.points()[1] + round.meld()[1]
                    self.event_show_score()
                    if len(self._rounds) < 16:
                        self.deal()

    def to_play(self):
        if self._bids is not None:
            idx = self._players.index(self.dealer())
            return self._players[(idx + self._bids + 1) % 4]
        else:
            idx = self._rounds[-1].to_play()
            return self._players[idx]
