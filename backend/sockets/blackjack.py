"""Blackjack socket event handlers."""

from flask import request, session

from extensions import socketio
from registry import rooms, sid_player_obj_mapping
from sockets.validate import socket_validate


@socketio.on("blackjack_player_join")
def blackjack_player_join():
    if not socket_validate(session): return

    room_id = session.get("room")
    room = rooms.get(room_id)
    game = room.game
    username = session.get("username")
    print("DEBUG username:", username)  # add this
    print("DEBUG session:", dict(session))  # add this
    blackjack_player = game.AddPlayer(request.sid, username)
    if blackjack_player is not None:                                  # check if successfully added the player - game might be full 
        sid_player_obj_mapping[request.sid] = blackjack_player        # globally accessible dictionary - not bound to a room

        # Tell other players to render this new player as a label
        socketio.emit("relay_player_info", {"id" : request.sid, "username": username,}, to=room_id)

        # Tell then newly connected player to render all previous players
        for player in game.players:
            socketio.emit("relay_player_info", {
                "id" : player.id,
                "username": player.username,
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

@socketio.on("blackjack_player_leave")
def blackjack_player_leave():
    if request.sid in sid_player_obj_mapping.keys():          # if sid exists in the mapping 
        player_obj = sid_player_obj_mapping[request.sid]
        room_id = session.get("room")
        room = rooms.get(room_id)
        game = room.game
        print("Leave:", player_obj, room, sid_player_obj_mapping.keys())
        if player_obj is not None: 
            player_obj.ClearHand()
            del sid_player_obj_mapping[request.sid]
            try:
                game.RemovePlayer(player_obj)
            except:
                pass
            room.player_count -= 1

            if len(game.players) == 0:
                del rooms[room_id]
                print("Room deleted") 

            game.EvaluateRound()

                    # Tell other players to render this new player as a label
            # socketio.emit("relay_player_info", {"id" : request.sid, "username": username,}, to=room_id)

            # Tell then newly connected player to render all previous players
            socketio.emit("refresh_players")
            for player in game.players:
                socketio.emit("relay_player_info", {
                    "id" : player.id,
                    "username": player.username,
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

