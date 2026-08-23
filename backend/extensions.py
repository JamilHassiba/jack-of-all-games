"""Flask extensions, instantiated unbound so modules can import them without a circular dependency on app.py."""

from flask_socketio import SocketIO

socketio = SocketIO()
