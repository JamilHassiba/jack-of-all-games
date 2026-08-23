"""Flask application entry point: configuration, blueprint registration, and startup."""

import os
import threading

from flask import Flask
from flask_session import Session

from db import init_db
from extensions import socketio
from game_loop import game_loop
from routes import auth, rooms, stats

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

SECRET_KEY = os.environ.get("SECRET_KEY", "jack_of_all_games_secret_key")


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(FRONTEND_DIR, "templates"),
        static_folder=os.path.join(FRONTEND_DIR, "static"),
    )

    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SESSION_TYPE"] = "filesystem"        # sessions stored server side
    app.config["SESSION_PERMANENT"] = True           # persist across browser restarts
    app.config["PERMANENT_SESSION_LIFETIME"] = 3600  # seconds

    Session(app)
    socketio.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(rooms.bp)
    app.register_blueprint(stats.bp)

    # Registering the handlers happens on import.
    import sockets  # noqa: F401

    init_db()
    return app


app = create_app()


if __name__ == "__main__":
    threading.Thread(target=game_loop, daemon=True).start()
    # allow_unsafe_werkzeug lets the Werkzeug dev server handle websockets locally.
    # For deployment, run under a production server (e.g. gunicorn with an eventlet worker).
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
