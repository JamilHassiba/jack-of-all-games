import {Card} from '../card.js';
import {Deck} from '../deck.js';
import {SendData} from '../utils.js';

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
let player_labels = {}
let room_state = "unknown";
let player_state = "unknown";

const title_base = title.innerHTML;

// Create socket object;
var socket = io();

//// START ////
title.innerHTML = title_base.concat(" | waiting for state from server")
CanRequestActions(false);

// Events
hit_button.addEventListener("mousedown", HitButtonClicked);
stand_button.addEventListener("mousedown", StandButtonClicked);

//// METHODS ////

// Socket
socket.on('connect', function() {
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
socket.on('relay_player_state', function(data) {
    if (data.id == socket.id) {
        player_state = data.new_state
        
        switch (player_state) {
            case 'lobby'    : ThisPlayer_EnteredLobbyState();    break;
            case 'playing'  : ThisPlayer_EnteredPlayingState();  break;
            case 'finished' : ThisPlayer_EnteredFinishedState(); break;
        }
    } else {
        switch(data.new_state) {
            case 'lobby'    : OtherPlayer_EnteredLobbyState();    break;
            case 'playing'  : OtherPlayer_EnteredPlayingState();  break;
            case 'finished' : OtherPlayer_EnteredFinishedState(); break;
        }

    }
})
socket.on('entity_goes_bust_or_blackjack', function(data) {
    if (data.id == socket.id) {
        if (data.type == "bust") ThisPlayer_WentBust();
        else ThisPlayer_HasBlackjack();

    } else if (data.id == "dealer") {
        if (data.type == "bust") Dealer_WentBust();
        else Dealer_HasBlackjack();

    } else {
        if (data.type == "bust") OtherPlayer_WentBust(data.id);
        else OtherPlayer_HasBlackjack();
    }
})

socket.on('write_hand', function(data) {
    let hand = data.hand

    if (data.id == socket.id) {
        player_hand_container.innerHTML = hand
    } else if (data.id == "dealer") {
        dealer_hand_container.innerHTML = hand
    } else {
        UpdatePlayerLabelHand(data.id, hand)
    }

});

socket.on('create_player_label', function(data) {
    if (data.id == socket.id) return
    CreatePlayerInfo(
        data.id,
        (data.id).substring(0,4),
        data.game_score,
        data.hand,
        data.status
    )
})

// Player State Change Methods
function ThisPlayer_EnteredLobbyState() {

}
function ThisPlayer_EnteredPlayingState() {
    CanRequestActions(true);
}
function ThisPlayer_EnteredFinishedState() {
    CanRequestActions(false);
}
function ThisPlayer_WentBust() {
    alert("You are bust!");
}
function ThisPlayer_HasBlackjack() {
    alert("Blackjack!");
}

// Other Player State Change Methods
function OtherPlayer_EnteredLobbyState(playerid) {

}
function OtherPlayer_EnteredPlayingState(playerid) {

}
function OtherPlayer_EnteredFinishedState(playerid) {

}
function OtherPlayer_WentBust(playerid) {

}
function OtherPlayer_HasBlackjack(playerid) {

}

// Dealer State Change Methods
function Dealer_HasBlackjack() {
    alert("Dealer has blackjack!");
}
function Dealer_WentBust() {
    alert("Dealer went bust!");
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

// Buttons
function HitButtonClicked() {
    if (player_state != "playing") return;
    if (room_state != "players_turn") return;

    socket.emit("blackjack_hit_request");
};
function StandButtonClicked() {
    if (player_state != "playing") return;
    if (room_state != "players_turn") return;
    
    socket.emit("blackjack_stand_request");
}

// Utility
function CanRequestActions(bool) {
    hit_button.disabled = !bool;
    stand_button.disabled = !bool;
}

function SetRoomStatus(room_status) {
    title.innerHTML = title_base.concat(" | ", room_status);
}

function CreatePlayerInfo(id, name, game_score, hand, status) {
    let e = document.createElement("li")
    other_players_container.appendChild(e)

    player_labels[id] = {
        "id" : id,
        "name" : name,
        "game_score" : game_score,
        "hand" : hand,
        "status" : status,
        "e" : e
    }

    SetPlayerLabelText(id)
    return e
}

function UpdatePlayerLabelHand(id, hand) {
    let data = player_labels[id]
    data.hand = hand
    SetPlayerLabelText(id)
}

function SetPlayerLabelText(id) {
    let data = player_labels[id]
    data.e.innerHTML = `${data.name} | Score: ${data.game_score} | ${data.hand} | ${data.status}`
}