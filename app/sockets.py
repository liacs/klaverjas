import functools

from flask import request
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

from app import app, socketio
from app.models import Game


games = {}


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socketio.on('connect')
@authenticated_only
def connect():
    app.logger.info('connect {} {}'.format(request.sid, current_user.username))


@socketio.on('disconnect')
def disconnect():
    app.logger.info('disconnect {}'.format(request.sid))


@socketio.on('join')
@authenticated_only
def join(data):
    game_id = data.get('game')
    game = games.get(game_id)
    if game is None:
        try:
            game = Game.query.filter_by(id=game_id).first()
        except SQLAlchemyError as exp:
            app.logger.error(exp)
            return
        game.init()
        games[game.id] = game
    game.event_join(current_user, request.sid)


@socketio.on('bid')
@authenticated_only
def bid(data):
    game_id = data.get('game')
    game = games.get(game_id)
    if game is None:
        app.logger.error('unknown game {}'.format(game_id))
    game.event_bid(current_user, data)


@socketio.on('play')
@authenticated_only
def play(data):
    game_id = data.get('game')
    game = games.get(game_id)
    if game is None:
        app.logger.error('unknown game {}'.format(game_id))
    game.event_play(current_user, data)
