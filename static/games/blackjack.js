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

socket.on('game_state_changed', function(data) {
    room_state = data.new_state
    SetRoomStatus(room_state)

    switch (room_state) {
        case 'round_start': WhenEnteredRoundStart(); break;
        case 'dealer_turn': WhenEnteredDealerTurn(); break;
    }
});

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

// State Change Methods
function WhenEnteredRoundStart() {
    CanRequestActions(true);
}
function WhenEnteredDealerTurn() {
    CanRequestActions(false);
}

// Buttons
function HitButtonClicked() {
    if (room_state != "players_turn") return;

    socket.emit("blackjack_hit_request");
};
function StandButtonClicked() {
    console.log("stand clicked");
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