from flask import Flask, request, render_template, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask_session import Session 
import random
from game import Room, Game, War  
from flask_socketio import emit, join_room, leave_room, SocketIO

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
        room = Room(game_type, num_players)
        rooms[room.id] = room                # store rooms in a dict for quick access 
        print(game_type)
        return f"successfully created room with id {room.id}"
    except:
        return "error, something went wrong. source: creating a room" 

@app.route("/join_room", methods=["POST", "GET"])             # frontend sends a room id for the user to join 
def backend_join_room(): 
    # assumed frontend data format: 
    # form data with attributes: room_id
    try: 
        data = request.form 
        room_id = data["room_id"]
        if room_id in rooms.keys(): 
            if not session.get("room"):  
                if not session.get("player_index"): 
                    room = rooms[room_id]                                # fetch the room obj 
                    game = room.game                                       # fetch the game obj 
                    if room.player_count < room.num_players:            # store the player obj in session dict 
                        session["room"] = room.id 
                        session["player_index"] = room.player_count
                        room.player_count += 1 
                        return f"success - joined room with id {room.id}, player num {session['player_index']}"
                    else: 
                        return "The room is full"
                else: 
                    return "You are already in a room"
            else:
                return "You are already in a room"
        else: 
            return "Room ID does not exist"
    except: 
        return "error, something went wrong. source: joining room"

@app.route("/search_rooms", methods=["POST", "GET"])
def search_rooms(): 
    print([room for room in rooms])
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
                    socketio.emit("message", {"msg": f"{player_index} has played a card"})
                    return f"Discarded the card {status}"
        else: 
            return "User has not joined a room!"
    else: 
        return "Not provided with card code - cannot discard"

@app.route("/room")
def frontend_room(): 
    if "room" in session.keys(): 
        room_id = session["room"]
        if room_id in rooms.keys(): 
            room = rooms[room_id]
            if room.game_type == "war": 
                return render_template("war.html")
            elif room.game_type == "poker": 
                pass                                      # extension example 

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

@app.route("/get_roomid")
def get_roomid(): 
    if "room" in session.keys(): 
        room_id = session["room"]
        if room_id in rooms.keys(): 
            return room_id 

#socketio routes 
@socketio.on("connect")
def socket_connect(*arg):         # currently assumes the user is already in a room 
    if "room" in session.keys():
        room_id = session["room"]
        if room_id in rooms.keys(): 
            room = rooms[room_id]
            sid = request.sid 
            socketio_connected[sid] = room        # save the room 
            if room_id not in socketio_rooms:
                join_room(room_id)
                socketio_rooms.append(room_id) 
            else: 
                join_room(room_id)
            emit("message", {"msg":f"Successfully joined a room - room_id: {room_id}"})
    else: 
        print("Tried to connect frontend room - user is not in a backend room yet")

@socketio.on("disconnect")
def socket_disconnect(*arg): 
    if "room" in session.keys(): 
        room_id = session["room"]
        if room_id in rooms.keys(): 
            room = rooms[room_id]
            sid = request.sid 
            socketio_connected.pop(sid)
            leave_room(room_id)                 # WARNING: NO GARBAGE COLLECTION FOR SOCKETIO_ROOM
            emit("message", {"msg":"Successfully left a room"})
    else: 
        print("Tried to disconnect frontend room - user is not in a backend room yet")


if __name__ == '__main__': 
    app.run(host="0.0.0.0")
