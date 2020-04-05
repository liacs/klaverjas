from datetime import datetime
from hashlib import md5
import random
import uuid

from flask_login import UserMixin
from flask_socketio import emit
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login
from app.klaverjas.cards import Card, Rank, Suit
from app.klaverjas.rounds import Round


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

    def dealer(self):
        return self._players[(self.round_nr() - 1) % 4]

    def event_bid(self, player, data):
        try:
            lead = self._players.index(player)
        except ValueError:
            return
        trump_suit = data.get('trump_suit')
        if trump_suit is not None:
            self._bids = None
            self._trump_suit = trump_suit
            eldest = (self._players.index(self.dealer()) + 1) % 4
            self._rounds.append(Round(lead, eldest, trump_suit))
        else:
            self._bids += 1
        self.notify_all()

    def event_join(self, player, sid):
        try:
            idx = self._players.index(player)
        except ValueError:
            return
        self._sids[idx] = sid
        self.notify(player)

    def event_play(self, player, data):
        pass

    def notify(self, player):
        idx = self._players.index(player)
        trick = []
        try:
            round = self._rounds[-1]
            current_trick = round.current_trick()
            if current_trick is not None:
                trick = [card.to_dict() for card in current_trick.cards()]
        except IndexError:
            pass
        state = {'north': str(self._players[(idx + 2) % 4]),
                 'east': str(self._players[(idx + 3) % 4]),
                 'west': str(self._players[(idx + 1) % 4]),
                 'dealer': str(self.dealer()),
                 'round': self.round_nr(),
                 'scores': self._scores,
                 'trick': trick,
                 'hand': [card.to_dict() for card in self._hands[idx]],
                 'trump_suit': str(self._trump_suit),
                 'bids': self._bids}
        sid = self._sids[idx]
        if sid is not None:
            emit('notify', state, room=sid)
            if player == self.to_play():
                if self._bids is None:
                    moves = self._rounds[-1].legal_moves(self._hands[idx])
                    state = {'legal_moves': [card.to_dict() for card in moves]}
                    emit('play', state, room=sid)
                elif self._bids < 4:
                    state = {'trump_suit': str(self._trump_suit)}
                    emit('ask_bid', state, room=sid)
                else:
                    state = {'trump_suit': [str(suit) for suit in Suit
                                            if suit != self._trump_suit]}
                    emit('force_bid', state, room=sid)

    def notify_all(self):
        for player in self._players:
            self.notify(player)

    def round_nr(self):
        return max(len(self._rounds), 1)

    def to_play(self):
        if self._bids is not None:
            idx = self._players.index(self.dealer())
            return self._players[(idx + self._bids + 1) % 4]
        else:
            idx = self._rounds[-1].to_play()
            return self._players[idx]
