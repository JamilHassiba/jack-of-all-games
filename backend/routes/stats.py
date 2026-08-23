"""Scoreboard routes: aggregate win and game counts."""

from flask import Blueprint

from db import db

bp = Blueprint("stats", __name__)


@bp.route("/get_wins")
def get_wins():
    with db() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT username, wins FROM users""")
        rows = cur.fetchall()
        wins = [[row[0], row[1]] for row in rows]
        return wins

@bp.route("/get_games")
def get_games():
    with db() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT username, games FROM users""")
        rows = cur.fetchall()
        games = [[row[0], row[1]] for row in rows]
        return games

# socketio routes

