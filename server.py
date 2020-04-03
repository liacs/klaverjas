import argparse

from app import app, db, socketio


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
        app.logger.info('App exit')
        exit()

    socketio.run(app)
