"""SQLite access: connection helper, schema bootstrap, and win/loss recording."""

import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")


def db():
    """Open a connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the users table if it doesn't already exist."""
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                wins INTEGER NOT NULL DEFAULT 0,
                games INTEGER NOT NULL DEFAULT 0
            )
        """)


def record_win(username):
    with db() as conn:
        conn.execute("UPDATE users SET games = games + 1 WHERE username = ?", (username,))
        conn.execute("UPDATE users SET wins = wins + 1 WHERE username = ?", (username,))


def record_loss(username):
    with db() as conn:
        conn.execute("UPDATE users SET games = games + 1 WHERE username = ?", (username,))
