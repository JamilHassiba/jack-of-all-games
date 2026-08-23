"""Room lifecycle routes: create, join, leave, search, and the in-game page."""

from flask import Blueprint, jsonify, redirect, render_template, request, session

from extensions import socketio
from registry import rooms
from room import Room

bp = Blueprint("rooms", __name__)


@bp.route("/create_room", methods=["POST", "GET"])    
def create_room():                   # frontend sends a POST request and we make a room and auto join 
    # assumed frontend data format: 
    # form data with attributes: game_type, num_players 
    # frontend people, pls follow register.html example of sending form data 
    try: 
        data = request.form 
        game_type = data["game_type"]
        if not game_type in ["blackjack", "crazyeights"]: 
            return "Cannot create room - game type not supported"
        num_players = int(data["num_players"])
        room = Room(socketio, game_type, num_players)
        rooms[room.id] = room                # store rooms in a dict for quick access 
        return room.id
    except:
        return "error, something went wrong. source: creating a room" 

@bp.route("/join_room", methods=["POST", "GET"])
def backend_join_room():
    try:
        data = request.form
        room_id = data["room_id"]

        # Validate
        if room_id not in rooms: return "Room ID does not exist"
        if session.get("room"): return "You are already in a room"
        if session.get("player_index"): return "You are already in a room"
            
        room = rooms[room_id]
        # Room must have space
        if room.player_count >= room.num_players:
            return "The room is full"

        # Main logic
        session["room"] = room.id
        session["player_index"] = room.player_count
        room.player_count += 1

        return f"success - joined room with id {room.id}, player num {session['player_index']}"

    except Exception:
        return "error, something went wrong. source: joining room"

@bp.route("/leave_room", methods=["POST"])
def backend_leaveroom():
    if "room" in session.keys():
        room_id = session["room"]
        room = rooms[room_id] 
        del session["room"]
    if "player_index" in session.keys(): 
        del session["player_index"]
    
    return redirect("/")


@bp.route("/search_rooms", methods=["POST", "GET"])
def search_rooms(): 
    #print([room for room in rooms])
    data = {
        room.id: {
            "type": room.game_type, 
            "max_players": room.num_players, 
            "current_players": room.player_count,
        }

        for room in [rooms[_key] for _key in rooms.keys()]
    }
    return jsonify(data)

     
@bp.route("/room")
def frontend_room():
    if "room" not in session: return "You are not in a room"
    room_id = session["room"]

    if room_id not in rooms: return "Room does not exist"
    room = rooms[room_id]

    # Handle game types
    if room.game_type == "blackjack":
        return render_template("blackjack.html", code=room_id)
    
    if room.game_type == "crazyeights":
        return render_template("crazyeights.html", code=room_id)

    return "Unsupported game type"

