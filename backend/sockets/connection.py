"""Connection lifecycle: joining and leaving the socket room."""

from flask import request, session
from flask_socketio import emit, join_room, leave_room

from extensions import socketio
from registry import rooms, socketio_connected, socketio_rooms
from sockets.validate import socket_validate


@socketio.on("connect")
def socket_connect(*arg):
    if not socket_validate(session): return

    room_id = session.get("room")
    room = rooms.get(room_id)
    sid = request.sid

    # Track connection
    socketio_connected[sid] = room

    # Join socketio room
    join_room(room_id)

    if room_id not in socketio_rooms:
        socketio_rooms.append(room_id)

    #
    emit("message", {"msg": f"Successfully joined a room - room_id: {room_id}"})

@socketio.on("disconnect")
def socket_disconnect(*arg):
    if not socket_validate(session): return

    room_id = session.get("room")
    room = rooms.get(room_id)
    sid = request.sid

    socketio_connected.pop(sid, None)

    leave_room(room_id)

    emit("message", {"msg": "Successfully left a room"})


