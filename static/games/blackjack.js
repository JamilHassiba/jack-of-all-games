// Some elemnts used throughout
const gameStatus = document.getElementById("game-status-p");


// SOCKET CODE FOR INTERACTING WITH BACKEND
// Create socket object;
var socket = io();
socket.on('connect', function() {
    socket.emit('blackjack_player_join');
});

socket.on('set_room_label', function(data) {
    // title.innerHTML = title_base.concat(" | ", data.label);
    console.log("Room Label", data.label)
    gameStatus.innerHTML = "Room Label: " + data.label
});

socket.on('write_hand', function(data) {
    let hand = data.hand

    if (data.id == socket.id) {
        console.log("Player Hand -> ", hand)
        // player_hand_container.innerHTML = hand
    } else if (data.id == "dealer") {
        // dealer_hand_container.innerHTML = hand
        console.log("Dealer Hand -> ", hand)
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

function CreatePlayerInfo(id, name, game_score, hand, status) {
    console.log("Player -> ", id, name, game_score, hand, status)
}


function createCard(id) {
    return `<img src="https://deckofcardsapi.com/static/img/${id}.png" class="OBJ_card" alt="${id}">`
}

function addCardToHand(hand_container, card_id) {
    hand_container.innerHTML += createCard(card_id)
}