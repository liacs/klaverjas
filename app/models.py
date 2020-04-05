from datetime import datetime
from hashlib import md5
import random
import uuid

from flask_login import UserMixin
from flask_socketio import emit, join_room
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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

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
        self._sids = {}
        self.deal()

    def deal(self):
        deck = [Card(Suit(idx // 8), Rank(idx % 8)) for idx in range(32)]
        random.shuffle(deck)
        self._hands = [sorted(deck[0:8]), sorted(deck[8:16]),
                       sorted(deck[16:24]), sorted(deck[24:32])]
        self._trump_suit = random.choice(list(Suit))
        self._bids = 0

    def dealer(self):
        return self._players[len(self._rounds) % 4]

    def eldest(self):
        return self._players[(len(self._rounds) + 1) % 4]

    def emit(self, event, data, user):
        sid = self._sids.get(user.username)
        if sid is not None:
            emit(event, data, room=sid)

    def event_bid(self, user, trump_suit):
        if self.is_bidding_phase():
            if user != self.next_bidder():
                return
            if trump_suit:
                self._bids = None
                self._trump_suit = trump_suit
                round = Round(self.player_idx(user), self.player_idx(self.eldest()), trump_suit)
                self._rounds.append(round)
                player = self.next_player()
                player_idx = self.player_idx(player)
                moves = round.legal_moves(self._hands[player_idx])
                self.emit('play', {'legal_moves': [card.to_dict() for card in moves]}, self.next_player())
            else:
                self._bids += 1
                if self._bids < 4:
                    self.emit('ask_bid', {'trump_suit': str(self._trump_suit)}, self.next_bidder())
                else:
                    self.emit('force_bid', {'trump_suit': [str(suit) for suit in Suit if suit != self._trump_suit]}, self.eldest())

    def event_join(self, user, sid):
        self._sids[user.username] = sid
        join_room(self.id)

        self.emit('log', self.state_for(user), user)
        if self.is_bidding_phase():
            if self._bids < 4:
                if user == self.next_bidder():
                    self.emit('ask_bid', {'trump_suit': str(self._trump_suit)}, user)
            else:
                if user == self.next_bidder():
                    self.emit('force_bid', {'trump_suit': [str(suit) for suit in Suit if suit != self._trump_suit]}, user)
        else:
            if user == self.next_player():
                player_idx = self.player_idx(user)
                moves = self._rounds[-1].legal_moves(self._hands[player_idx])
                self.emit('play', {'legal_moves': [card.to_dict() for card in moves]}, user)

    def is_bidding_phase(self):
        return self._bids is not None

    def next_bidder(self):
        return self._players[(self.player_idx(self.dealer()) +
                              self._bids + 1) % 4]

    def next_player(self):
        return self._players[self._rounds[-1].to_play()]

    def player_idx(self, user):
        return self._players.index(user)

    def state_for(self, user):
        idx = self.player_idx(user)
        state = {'dealer': str(self.dealer()),
                 'hand': [card.to_dict() for card in self._hands[idx]],
                 'trump_suit': str(self._trump_suit),
                 'north': str(self._players[(idx + 2) % 4]),
                 'east': str(self._players[(idx + 3) % 4]),
                 'west': str(self._players[(idx + 1) % 4])}
        if self.is_bidding_phase():
            state['bids'] = self._bids
            state['to_play'] = str(self.next_bidder())
        else:
            tricks = self._rounds[-1].tricks()
            trick = tricks[-1]
            state['trick'] = [card.to_dict() for card in trick.cards()]
        return state
