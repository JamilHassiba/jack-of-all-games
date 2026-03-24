// Some elements used throughout
const gameStatus = document.getElementById("game-status-p");

// SOCKET CODE FOR INTERACTING WITH BACKEND
// Create socket object;
var socket = io();
socket.on('connect', function () {
    socket.emit('blackjack_player_join');
});

socket.on('set_room_label', function (data) {
    // title.innerHTML = title_base.concat(" | ", data.label);
    // console.log("Room Label", data.label)
    gameStatus.innerHTML = "Room Label: " + data.label
});

socket.on('write_hand', function (data) {
    console.log(data)
    let hand = data.hand

    if (data.id == socket.id) { // CAN REDUCE THIS LATER
        updatePlayerLabelHand(socket.id, hand)
    } else if (data.id == "dealer") {
        updatePlayerLabelHand("dealer", hand)
    } else {
        updatePlayerLabelHand(data.id, hand)
    }

});

socket.on('create_player_label', function (data) {
    if (data.id == socket.id) {
        players[1] = data.id
        return
    }
    addPlayer(data.id, data.id) // UPDATE W UNAME WHEN IMPLEMENTED
    CreatePlayerInfo(
        data.id,
        (data.id).substring(0, 4),
        data.game_score,
        data.hand,
        data.status
    )
})

function CreatePlayerInfo(id, name, game_score, hand, status) {
    return
    // console.log("Player -> ", id, name, game_score, hand, status)
}



// Hand and Card Creation Logic
function createCard(id) {
    return `<img src="https://deckofcardsapi.com/static/img/${id}.png" class="OBJ_card" alt="${id}">`
}

function addCardToHand(hand_container, card_id) {
    hand_container.innerHTML += createCard(card_id)
}

function wipeHand(hand_container) {
    hand_container.innerHTML = ""
}

function updatePlayerLabelHand(player_id, hand) {
    let handcontainer
    if (player_id == "dealer") {
        handcontainer = document.getElementById("dealer-hand")
    } else {
        handcontainer = document.getElementById("hand-p" + getPlayerNum(player_id))
    }
    wipeHand(handcontainer)
    for (let card_id of hand) {
        addCardToHand(handcontainer, card_id)
    }
}


// Adding Players to the game
let player_num = 1   // number of players in game
document.getElementById("seat-p1").innerHTML = "You!"

let players = {
    1: socket.id, // self player
    2: null,
    3: null,
    4: null,
    5: null
}

function addPlayer(name, id) {
    player_num++;
    players[player_num] = id
    document.getElementById("seat-p" + player_num).innerHTML = name
}


function getPlayerNum(player_id) {
    console.log(player_id, "----")
    for (let num in players) {
        console.log(players[num])
        if (players[num] == player_id) {
            return num
        }
    }
    return null
}