import {PlayerInfo} from "../classes/playerinfo.js";
import { PlayerLabel } from "../classes/playerlabel.js";

console.log("blackjack.js is running...")

//// INITIALISATION ////

// References
let player_hand_container = document.getElementById("player-hand");
let dealer_hand_container = document.getElementById("dealer-hand");
let other_players_container = document.getElementById("other-players");

let hit_button = document.getElementById("hit-btn");
let stand_button = document.getElementById("stand-btn");

let title = document.getElementById("title")

// Data
// Create socket object;
var socket = io();

let this_player;

let players = new Map;
let player_labels = new Map;

let room_state = "unknown";

const title_base = title.innerHTML;

//// START ////
title.innerHTML = title_base.concat(" | waiting for state from server")
CanRequestActions(false);

// Events
hit_button.addEventListener("mousedown", HitButtonClicked);
stand_button.addEventListener("mousedown", StandButtonClicked);

//// METHODS ////

// Socket
socket.on('connect', function() {
    this_player = new PlayerInfo(socket.id)
    players.set(socket.id, this_player)

    socket.emit('blackjack_player_join');
});

socket.on('relay_game_state', function(data) {
    room_state = data.new_state

    switch (room_state) {
        case 'intermission' : Game_EnteredIntermissionState(); break;
        case 'round_start'  : Game_EnteredRoundStartState();   break;
        case 'players_turn' : Game_EnteredPlayersTurnState();  break;
        case 'dealer_turn'  : Game_EnteredDealersTurnState();  break;
        case 'score'        : Game_EnteredScoreState();        break;
        case 'cleanup'      : Game_EnteredCleanupState();      break;
    }
});

function UpdatePlayerField(id, field, value, thisplayer_callback=()=>{}, otherplayer_callback=()=>{}, dealer_callback=()=>{}) {
    let player = players.get(id)
    player[field] = value
    
    
    if (id==socket.id) {
        // This player is this client's player
        thisplayer_callback(id, value)
    } else if (id=="dealer") {
        // This player is the dealer
        dealer_callback(id, value)
    } else {
        // This player is some other player
        otherplayer_callback(id, value)
    }
}
function UpdatePlayerLabel(id, player) {
    let label = player_labels.get(id)
    if (!label) {
        label = new PlayerLabel(id)
        other_players_container.appendChild(label.e)
        player_labels.set(id, label)
    }

    label.update(player);
}
socket.on('relay_player_info', function(data) {
    let id = data.id;
    let player = players.get(id);
    if (player == null) {
        player = new PlayerInfo(id);
        players.set(id, player)
    }

    if (data.hand) 
        UpdatePlayerField(id, "hand", data.hand, ThisPlayer_HandUpdated, OtherPlayer_HandUpdated, Dealer_HandUpdated)
    if (data.hand_total) 
        UpdatePlayerField(id, "hand_total", data.hand_total, ThisPlayer_HandTotalUpdated, OtherPlayer_HandTotalUpdated, Dealer_HandTotalUpdated)
    if (data.game_score) 
        UpdatePlayerField(id, "game_score", data.game_score, ThisPlayer_GameScoreUpdated, OtherPlayer_GameScoreUpdated)
    if (data.state) 
        UpdatePlayerField(id, "state", data.state, ThisPlayer_StateUpdated, OtherPlayer_StateUpdated)
    if (data.is_bust)
        UpdatePlayerField(id, "is_bust", data.is_bust, ThisPlayer_IsBust_Updated, OtherPlayer_IsBust_Updated, Dealer_IsBust_Updated)
    if (data.has_blackjack)
        UpdatePlayerField(id, "has_blackjack", data.has_blackjack, ThisPlayer_HasBlackjack_Updated, OtherPlayer_HasBlackjack_Updated, Dealer_HasBlackjack_Updated)

    if (player != this_player && id != "dealer") 
        UpdatePlayerLabel(id, player)
})

// Player Actions
function HitButtonClicked() {
    if (this_player.state != "playing") return;
    if (room_state != "players_turn") return;

    socket.emit("blackjack_hit_request");
};
function StandButtonClicked() {
    if (this_player.state != "playing") return;
    if (room_state != "players_turn") return;
    
    socket.emit("blackjack_stand_request");
}

// This Player Handlers
function ThisPlayer_HandUpdated(playerid, new_hand) {
    player_hand_container.innerHTML = new_hand
}
function ThisPlayer_HandTotalUpdated(playerid, new_hand_total) {

}
function ThisPlayer_GameScoreUpdated(playerid, new_hand) {

}
function ThisPlayer_StateUpdated(playerid, new_state) {
    switch (new_state) {
        case "lobby" : {
            break;
        }

        case "playing" : {
            CanRequestActions(true);
            break;
        }

        case "finished" : {
            CanRequestActions(false);
            break;
        }
    }
}
function ThisPlayer_IsBust_Updated(playerid, is_bust) {
    if (is_bust)
        alert("You are bust!");
}
function ThisPlayer_HasBlackjack_Updated(playerid, has_blackjack) {
    if (has_blackjack)
        alert("Blackjack!");
}

// Other Player Handlers
function OtherPlayer_HandUpdated(playerid, new_hand) {
    
}
function OtherPlayer_HandTotalUpdated(playerid, new_hand_total) {

}
function OtherPlayer_GameScoreUpdated(playerid, new_hand) {
    
}
function OtherPlayer_StateUpdated(playerid, new_state) {
    switch (new_state) {
        case "lobby" : {
            break;
        }

        case "playing" : {
            break;
        }

        case "finished" : {
            break;
        }
    }
}
function OtherPlayer_IsBust_Updated(playerid, is_bust) {

}
function OtherPlayer_HasBlackjack_Updated(playerid, has_blackjack) {

}

// Dealer State Change Methods
function Dealer_HandUpdated(dealerid, new_hand) {
    dealer_hand_container.innerHTML = new_hand
}
function Dealer_HandTotalUpdated(dealerid, new_hand_total) {
    
}
function Dealer_IsBust_Updated(dealerid, is_bust) {
    if (is_bust)
        alert("Dealer went bust!");
}
function Dealer_HasBlackjack_Updated(dealerid, has_blackjack) {
    if (has_blackjack)
        alert("Dealer has blackjack!");
}



// Game State Change Methods
function Game_EnteredIntermissionState() {
    SetRoomStatus("Waiting for a round to begin...")
}   
function Game_EnteredRoundStartState() {
    SetRoomStatus("Dealing initial cards...")
}
function Game_EnteredPlayersTurnState() {
    SetRoomStatus("Player's turn")
}
function Game_EnteredDealersTurnState() {
    SetRoomStatus("Dealer is playing...")
}
function Game_EnteredScoreState() {
    SetRoomStatus("Evaluating round")
}
function Game_EnteredCleanupState() {

}

// Utility
function CanRequestActions(bool) {
    hit_button.disabled = !bool;
    stand_button.disabled = !bool;
}

function SetRoomStatus(room_status) {
    title.innerHTML = title_base.concat(" | ", room_status);
}