import {Card} from '../classes/card.js';
import {Deck} from '../deck.js';
import {SendData} from '../utils.js';

console.log("blackjack.js is running...")

// REFERENCES
let player_hand_container = document.getElementById("player-hand");
let dealer_hand_container = document.getElementById("dealer-hand");
let other_players_container = document.getElementById("other-players");
let title = document.getElementById("title")
const title_base = title.innerHTML;
title.innerHTML = title_base.concat(" | waiting for state from server")

let player_labels = {}

// Create socket object;
var socket = io();
socket.on('connect', function() {
    socket.emit('blackjack_player_join');
});

socket.on('set_room_label', function(data) {
    title.innerHTML = title_base.concat(" | ", data.label);
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


// UTILITY METHODS
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