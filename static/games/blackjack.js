import {Card} from '../card.js';
import {Deck} from '../deck.js';
import {SendData} from '../utils.js';

console.log("blackjack.js is running...")

// REFERENCES
let player_hand_container = document.getElementById("player-hand");
let dealer_hand_container = document.getElementById("dealer-hand");
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
})


// UTILITY METHODS

