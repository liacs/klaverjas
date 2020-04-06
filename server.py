import argparse

from klaverjas import app, db, socketio
from klaverjas.models import Game, User


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="server")
    parser.add_argument('--create_db', dest='create_db', default=False,
                        action='store_true')
    args = parser.parse_args()

    if args.create_db:
        app.logger.warning('dropping database')
        db.drop_all()
        app.logger.warning('create database')
        db.create_all()

        users = [User('north', 'north@kj.nl'),
                 User('east', 'east@kj.nl'),
                 User('south', 'south@kj.nl'),
                 User('west', 'west@kj.nl')]
        for user in users:
            user.set_password('test')
            db.session.add(user)
        db.session.commit()

        game = Game(users[0], users[1], users[2], users[3])
        db.session.add(game)
        db.session.commit()

        app.logger.info('App exit')
        exit()

    socketio.run(app)
