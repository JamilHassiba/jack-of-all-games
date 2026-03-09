import {Card} from '../card.js';
import {Deck} from '../deck.js';
import {SendData} from '../utils.js';

console.log("blackjack.js is running...")

// REFERENCES
let player_hand_container = document.getElementById("player-hand");
let dealer_hand_container = document.getElementById("dealer-hand");
let title = document.getElementById("title")
const title_base = title.innerHTML;


// Setup Socket
// Use a global variable to prevent multiple connections on hot reload
if (!window.blackjackSocket) {
    window.blackjackSocket = io();

    const socket = window.blackjackSocket;

    socket.on('connect', () => {
        console.log("Socket connected with id:", socket.id);

        // Emit join event only once
        if (!socket.joinedBlackjack) {
            socket.emit('blackjack_player_join');
            socket.joinedBlackjack = true;
        }
    });


    socket.off('set_room_label');
    socket.on('set_room_label', (data) => {
        console.log("REC");
        title.innerHTML = `${title_base} | ${data.label}`;
    });

}

// Reuse the global socket anywhere in this module
const socket = window.blackjackSocket;