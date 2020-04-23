# Klaverjas

Play the game of [Klaverjas](https://en.wikipedia.org/wiki/Klaverjas) in
a browser.

## Installation

Prerequisites: Python 3

- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install .`

## Local server

Create an empty database:
- `python server.py --create_db`

Run the server:
- `python server.py`

By default the application is served at `localhost:5000`

## Heroku

The application is automatically deployed on
[heroku](https://www.heroku.com).

Extra requirements (`requirements.txt`) for deploying on Heroku:
- A Heroku Postgres add-on (Hobby Dev)
- gunicorn as frontend webserver (see the `Procfile`)
- Initialize the database (once) using Heroku CLI
