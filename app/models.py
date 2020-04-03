from datetime import datetime
from hashlib import md5
import uuid

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


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
        self.username = str(username)
        self.email = str(email)

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
    north = db.Column(db.Integer, db.ForeignKey('user.id'))
    east = db.Column(db.Integer, db.ForeignKey('user.id'))
    south = db.Column(db.Integer, db.ForeignKey('user.id'))
    west = db.Column(db.Integer, db.ForeignKey('user.id'))

    def has_user(self, user):
        return (self.north == user.id or self.east == user.id or
                self.south == user.id or self.west == user.id)
