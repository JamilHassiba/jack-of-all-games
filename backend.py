from flask import Flask, request, render_template, redirect, session, jsonify
from flask_session import Session 
from flask_socketio import emit, join_room, leave_room, SocketIO
from game import Room, Game, War  
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

import traceback
import random
import threading
import time

from static.states import fsm, state, blackjack_states

rooms = {}
socketio_connected = {} 
socketio_rooms = []                                        # WARNING: NO GARBAGE COLLECTION - POTENTIAL MEMORY LEAK 
app = Flask(__name__)
app.secret_key = "jack_of_all_games_secret_key"
app.config['SECRET_KEY'] = 'jack_of_all_games_secret_key'  
app.config['SESSION_TYPE'] = 'filesystem'                  # sessions stored server side 
app.config['SESSION_PERMANENT'] = True                     # persistent sessions even after browser closes 
app.config['PERMANENT_SESSION_LIFETIME'] = 3600            # keep session on server for x seconds  
Session(app)
socketio = SocketIO(app)

# need a secret key for the session retained data
def db():
    # best way to operate on db with sqlite
    conn = sqlite3.connect("../users.db")
    conn.row_factory = sqlite3.Row
    return conn

with db() as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    """)
    # creates user table if it doesnt exist

@app.route('/')
def home_page():
    session.clear()                               # temporarily used for conn_test
    server_ip = request.host_url.rstrip("/")

    player = session.get("player_obj")
    if not player:
        return render_template("index.html")
    else:
        redirect("/room")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # password validation (can add more strict requirements later)
        if len(username) < 3 or len(password) < 8:
            return "Username or password is invalid length", 400
        
        #generate hash and register to DB
        pw_hash = generate_password_hash(password)
        try:
            with db() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, pw_hash)
                )
        
        # except if user exists alredy
        except sqlite3.IntegrityError:
            return "User already exists", 400
        
        return "", 200
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/")
    
    if request.method == "POST": 
        username = request.form["username"]
        password = request.form["password"]

        # get user and hash from db
        with db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            ).fetchone()

            # if user doesnt exist or wrong password
            if not user or not check_password_hash(user["password_hash"], password):
                return "Invalid username or password", 401
            
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        # retain info for session and redirect to game
        return "", 200
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    # clear session data on logout
    session.clear()
    return redirect("/login")

@app.route("/create_room", methods=["POST", "GET"])    
def create_room():                   # frontend sends a POST request and we make a room and auto join 
    # assumed frontend data format: 
    # form data with attributes: game_type, num_players 
    # frontend people, pls follow register.html example of sending form data 
    try: 
        data = request.form 
        game_type = data["game_type"]
        if not game_type in ["war", "blackjack"]: 
            return "Cannot create room - game type not supported"
        num_players = int(data["num_players"])
        room = Room(socketio, game_type, num_players)
        rooms[room.id] = room                # store rooms in a dict for quick access 
        return f"successfully created room with id {room.id}"
    except:
        return "error, something went wrong. source: creating a room" 

@app.route("/join_room", methods=["POST", "GET"])
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


@app.route("/search_rooms", methods=["POST", "GET"])
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

     
@app.route("/draw_card", methods=["POST", "GET"])             # apply game logic and draw a card to the user's pile 
def draw_card():
    # assumed frontend data format: 
    # form data with attributes: none 
    if "room" in session.keys(): 
        room_id = session["room"]
        if room_id in rooms.keys(): 
            room = rooms[room_id]
            game = room.game 
            player_index = session["player_index"]
            player = game.players[player_index]
            result = player.draw() 
            if result[0] == "successfully drawn card":
                socketio.emit("message", {"msg": f"player {player_index} has drawn a card"})
                return f"successfully drawn card(s): {result[1]}"
            elif result[0] == "End of Deck": 
                game.game_finish()
                return f"The game has finished"
            else: 
                return result + " locked: " + str(player.lock)
        else: 
            return "Room does not exist"
    else: 
        return "User has not joined a room!"

@app.route("/play_card", methods=["POST", "GET"])             # remove a card from the player pile and add to discard pile 
def play_card(): 
    # assumed frontend data format: 
    # form data with attributes: card_code 
    data = request.form
    if "card_code" in data.keys():  
        card = data["card_code"]    
        if "room" in session.keys(): 
            room_id = session["room"]
            if room_id in rooms.keys(): 
                room = rooms[room_id]
                game = room.game 
                player_index = session["player_index"]
                player = game.players[player_index]
                status = player.discard(card)
                if status == []: 
                    return "Either player is locked or exceeded max discard count"
                else: 
                    socketio.emit("message", {"msg": f"{player_index} has played a card"}, to=room_id)
                    return f"Discarded the card {status}"
        else: 
            return "User has not joined a room!"
    else: 
        return "Not provided with card code - cannot discard"

@app.route("/room")
def frontend_room():
    if "room" not in session: return "You are not in a room"
    room_id = session["room"]

    if room_id not in rooms: return "Room does not exist"
    room = rooms[room_id]

    # Handle game types
    if room.game_type == "war":
        return render_template("war.html", code=room_id)

    if room.game_type == "blackjack":
        return render_template("blackjack.html", code=room_id)

    if room.game_type == "poker":
        pass  # extension example

    return "Unsupported game type"

@app.route("/update")
def game_update():
    if "room" in session.keys(): 
        room_id = session["room"]
        if room_id in rooms.keys(): 
            room = rooms[room_id]                         # may require additional validation if game needs to force a sequence of choices from the player before it can be updated
            status = room.game.update()
            return status 
        else: 
            return "room does not exist"
    else: 
        return "you haven't joined a room"

@app.route("/get_hand")
def get_hand(): 
    if "room" in session.keys(): 
        room_id = session["room"]
        if room_id in rooms.keys(): 
            room = rooms[room_id]
            game = room.game 
            player = game.players[session["player_index"]]
            return player.show()


# socketio routes

# Validates to check whether the user is in a room, and that the room exists
# Returns true/false
def socket_validate(session):
    room_id = session.get("room") # User must be in a backend room
    if not room_id: print("Tried to connect frontend room - user is not in a backend room yet"); return False

    # Room must exist
    room = rooms.get(room_id)
    if not room: print("Tried to connect frontend room - backend room no longer exists"); return False

    return True

@socketio.on("blackjack_player_join")
def blackjack_player_join():
    if not socket_validate(session): return

    room_id = session.get("room")
    room = rooms.get(room_id)
    game = room.game
    blackjack_player = game.AddPlayer(request.sid)
    session["player_obj"] = blackjack_player

    # Tell other players to render this new player as a label
    socketio.emit("relay_player_info", {"id" : request.sid,}, to=room_id)

    # Tell then newly connected player to render all previous players
    for player in game.players:
        socketio.emit("relay_player_info", {
            "id" : player.id,
            "game_score" : player.game_score,
            "hand" : player.hand,
            "hand_total" : player.hand_total,
            "state" : player.state,
        }, to=request.sid)
    # As well as the dealer
    socketio.emit("relay_player_info", {
            "id" : "dealer",
            "hand" : game.dealer.hand,
            "hand_total" : game.dealer.hand_total,
        }, to=request.sid)

@socketio.on("blackjack_hit_request")
def blackjack_hit_request():
    if not socket_validate(session): return
    
    room_id = session.get("room")
    room = rooms.get(room_id)
    sid = request.sid

    room.game.PlayerHitRequest(sid)

@socketio.on("blackjack_stand_request")
def blackjack_stand_request():
    if not socket_validate(session): return

    room_id = session.get("room")
    room = rooms.get(room_id)
    sid = request.sid

    room.game.PlayerStandRequest(sid)

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


def game_loop():
    last_time = time.time()
    TICK_RATE = 1/30  # 30 ticks/sec
    while True:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        try:
            for room_id, room in rooms.items():
                room.game.Update(dt)  # pass delta time in seconds
        except Exception as e:
            print("Error in game loop:", e)
            traceback.print_exc()

        time.sleep(TICK_RATE)

if __name__ == '__main__': 
    # Added by Thomas McPhee
    # Start game loop
    thread = threading.Thread(target=game_loop, daemon=True)
    thread.start()


    app.run(host="0.0.0.0")