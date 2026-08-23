"""Crazy Eights socket event handlers."""

from flask import request, session

from extensions import socketio
from registry import rooms, sid_player_obj_mapping
from sockets.validate import socket_validate


@socketio.on("crazyeights_player_join")
def crazyeights_player_join():
    if not socket_validate(session): return

    room_id = session.get("room")
    room = rooms.get(room_id)
    game = room.game
    username = session.get("username")
    print("DEBUG username:", username)  # add this
    print("DEBUG session:", dict(session))  # add this
    crazyeights_player = game.AddPlayer(request.sid, username)
    session["player_obj"] = crazyeights_player
    sid_player_obj_mapping[request.sid] = crazyeights_player 

    # Tell player the room size
    socketio.emit("crazyeights_room_size", {
        "room_size": room.num_players
    }, to=request.sid)

    # Tell everyone else in the room to render this new player
    socketio.emit("crazyeights_relay_player_info", {
        "id" : request.sid,
        "username": username,
        "hand": crazyeights_player.hand,
        "game_score": crazyeights_player.game_score
    }, to=room_id)

    # Tell this newly connected player about everyone who is already sitting at the table
    for player in game.players:
        socketio.emit("crazyeights_relay_player_info", {
            "id" : player.id,
            "username": player.username,
            "game_score" : player.game_score,
            "hand" : player.hand,
            "state" : player.state,
        }, to=request.sid)
        
    # If a round is already active, send them the current discard pile and active suit
    if game.discard_pile:
        socketio.emit("crazyeights_relay_board_info", {
            "top_card": game.discard_pile[-1]["code"],
            "current_suit": game.current_suit,
            "current_value": game.current_value
        }, to=request.sid)

@socketio.on("crazyeights_play_card")
def crazyeights_play_card(data):
    if not socket_validate(session): return
    
    room_id = session.get("room")
    room = rooms.get(room_id)
    sid = request.sid
    card_code = data.get("card_code")

    room.game.PlayCardRequest(sid, card_code)

@socketio.on("crazyeights_choose_suit")
def crazyeights_choose_suit(data):
    if not socket_validate(session): return

    room_id = session.get("room")
    room = rooms.get(room_id)
    sid = request.sid
    new_suit = data.get("suit")

    room.game.ChooseSuitRequest(sid, new_suit)

@socketio.on("crazyeights_leave_room")
def crazyeights_leave_room():
    if request.sid in sid_player_obj_mapping.keys():
        player_obj = sid_player_obj_mapping[request.sid]
        room_id = session.get("room")
        room = rooms.get(room_id)
        game = room.game

        if player_obj is not None: 
            player_obj.ClearHand()
            del sid_player_obj_mapping[request.sid]
            game.RemovePlayer(player_obj)
            room.player_count -= 1
            room.num_players -= 1
            print("Player left")
            socketio.emit("crazyeights_message", {"msg": f"{player_obj.username} left"}, to=room_id) 

            if len(game.players) == 1:
                last_player = game.players[0]

                socketio.emit("crazyeights_player_left", {
                    "id": last_player.id, 
                    "username":last_player.username
                }, to=room_id)
                
                game.RemovePlayer(last_player)
                del rooms[room_id]
                print("Room deleted")
            else:
                socketio.emit("crazyeights_player_left", {
                    "id": request.sid, 
                    "username": player_obj.username
                }, to=room_id)

