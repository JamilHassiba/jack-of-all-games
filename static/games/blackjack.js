import {Card} from '../card.js';
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

// Create socket object;
var socket = io();
socket.on('connect', function() {
    socket.emit('blackjack_player_join');
});

socket.on('set_room_label', function(data) {
    title.innerHTML = title_base.concat(" | ", data.label);
});

socket.on('write_hand', function(data) {
    if (data.id == socket.id) {
        console.log("this hand belongs to me")
    } else if (data.id == "dealer") {
        console.log("this hand belongs to dealer")
    } else {
        console.log("this hand belongs to another player")
    }

});

socket.on('create_player_label', function(data) {
    if (data.id == socket.id) return
    CreatePlayerInfo(
        (data.id).substring(0,4),
        data.game_score,
        data.hand,
        data.status
    )
})


// UTILITY METHODS
function CreatePlayerInfo(name, game_score, hand, status) {
    let e = document.createElement("li")
    e.innerHTML = `${name} | Score: ${game_score} | ${hand} | ${status}`
    other_players_container.appendChild(e)
    return e
}
