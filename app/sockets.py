import functools

from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room

from app import app, socketio


users = {}
sids = {}


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
    if current_user.username not in users:
        users[current_user.username] = []
    users[current_user.username].append(request.sid)
    sids[request.sid] = current_user.username


@socketio.on('disconnect')
def disconnect():
    app.logger.info('disconnect {}'.format(request.sid))
    users[sids[request.sid]].remove(request.sid)
    if len(users[sids[request.sid]]) == 0:
        del users[sids[request.sid]]
    del sids[request.sid]


@socketio.on('join')
@authenticated_only
def join(data):
    room = data['room']
    app.logger.info('join {} {} {}'.format(request.sid, current_user.username,
                                           room))
    join_room(room)
    emit('log', current_user.username + ' has entered the room.', room=room)
