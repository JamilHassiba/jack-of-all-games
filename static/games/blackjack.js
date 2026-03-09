import {Card} from '../card.js';
import {Deck} from '../deck.js';
import {SendData} from '../utils.js';

console.log("blackjack.js is running...")

// REFERENCES
let player_hand_container = document.getElementById("player-hand");
let dealer_hand_container = document.getElementById("dealer-hand");

// Create socket object;
var socket = io();
socket.on('connect', function() {
    socket.emit('blackjack_player_join');
});

// UTILITY METHODS

