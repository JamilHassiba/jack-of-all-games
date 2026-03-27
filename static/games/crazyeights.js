/*
==================================
        SERVER -> CLIENT
==================================

* crazyeights_relay_player_info
    data: { 
        "id": string, 
        "username": string, 
        "hand": list[str], 
        "state": string, 
        "game_score": int
    }

* crazyeights_relay_board_info
    data: { 
        "top_card": string, 
        "current_suit": string,
        "current_value": string
    }

* crazyeights_message
    data: { 
        "msg": string
    }

* crazyeights_prompt_suit_choice
    data: { 
        "id": string
    }

* crazyeights_room_size
    data: {
        "room_size": int
    }

* crazyeights_game_over
    data: {
        "winner": string,
        "scores": list[int]
    }

==================================
        CLIENT -> SERVER
==================================

* crazyeights_player_join
  data: {}

* crazyeights_play_card
    data: { 
        "card_code": string
    }

* crazyeights_choose_suit
    data: { 
        "suit": string (e.g., "H") 
    }
*/


console.log("crazyeights.js is running...")

const statusText = document.getElementById("status-text");
const myHand = document.getElementById("hand-bottom");
const discardPile = document.getElementById("discard-pile");
const suitIcon = document.getElementById("current-suit-icon");
const suitPicker = document.getElementById("suit-picker");
const suitButtons = document.querySelectorAll(".suit-button");
const leaveButton = document.getElementById("leave-button");

let myId = null;
let opponentSeats = {}; 
let availableSeats = [];

const socket = io();

socket.on('connect', function () {
    myId = socket.id;
    statusText.innerText = "Connected!";
    socket.emit('crazyeights_player_join'); 
});

socket.on('crazyeights_room_size', function (data) {
    const roomSize = data.room_size;

    if (roomSize === 2) {
        availableSeats = ["top"]; 
        document.getElementById("area-top").classList.remove("hidden");
    } 
    else if (roomSize === 3) {
        availableSeats = ["left", "top"]; 
        document.getElementById("area-left").classList.remove("hidden");
        document.getElementById("area-top").classList.remove("hidden");
    } 
    else if (roomSize >= 4) {
        availableSeats = ["left", "top", "right"];
        document.getElementById("area-left").classList.remove("hidden");
        document.getElementById("area-top").classList.remove("hidden");
        document.getElementById("area-right").classList.remove("hidden");
    }
});

socket.on('crazyeights_relay_player_info', function (data) {

    const gameEndPopup = document.getElementById("game-end-popup");
    if (gameEndPopup) gameEndPopup.classList.add("hidden");

    if (data.id === myId) {
        if (data.hand) {
            drawMyHand(data.hand);
        }
        if (data.game_score !== undefined) {
            document.getElementById("score-bottom").innerText = `${data.game_score} pts`;
        }
    } 
    else {
        if (!opponentSeats[data.username]) {
            opponentSeats[data.username] = availableSeats.shift(); 
        }

        const position = opponentSeats[data.username];

        const nameElement = document.getElementById(`name-${position}`);
        if (data.username !== undefined) {
            nameElement.innerText = data.username;
        }

        const scoreElement = document.getElementById(`score-${position}`);
        if (data.game_score !== undefined) {
            scoreElement.innerText = `${data.game_score} pts`;
        }

        if (data.hand) {
            drawOpponentHand(position, data.hand.length);
        }
    }

    if (data.state !== undefined) {
        let areaElement = null;

        if (data.id === myId) {
            areaElement = document.getElementById("area-bottom");
        } 
        else {
            areaElement = document.getElementById(`area-${opponentSeats[data.username]}`);
        }

        if (data.state === "playing") {

            document.querySelectorAll('.player-area').forEach(element => {
                element.classList.remove('active-turn');
            });
            
            areaElement.classList.add('active-turn');
        } 
        else {
            areaElement.classList.remove('active-turn');
        }
    }
});

socket.on('crazyeights_relay_board_info', function (data) {
    discardPile.innerHTML = `<img src="https://deckofcardsapi.com/static/img/${data.top_card}.png" class="card-image" alt="${data.top_card}">`;
    updateSuitIcon(data.current_suit);
});

socket.on('crazyeights_message', function (data) {
    console.log("Game Server:", data.msg);
    statusText.innerText = data.msg;
});

socket.on('crazyeights_prompt_suit_choice', function (data) {
    if (data.id === myId) {
        suitPicker.classList.remove("hidden");
    }
});

socket.on('crazyeights_game_over', function (data) {
    document.getElementById("game-winner-text").innerText = `🏆 ${data.winner} is the Winner! 🏆`;

    let sortedScores = data.scores.sort((a, b) => a.score - b.score);

    const scoreList = document.getElementById("game-scores-list");
    scoreList.innerHTML = ""; 

    sortedScores.forEach(player => {
        let li = document.createElement("li");
        
        if (player.username === data.winner) {
            li.style.color = "#ffd700";
            li.innerHTML = `<strong>${player.username}: ${player.score} pts 👑</strong>`;
        } else {
            li.innerText = `${player.username}: ${player.score} pts`;
        }
        
        scoreList.appendChild(li);
    });

    document.getElementById("game-end-popup").classList.remove("hidden");
});

// ------------------------------- //

suitButtons.forEach(btn => {
    btn.addEventListener("click", function (event) {
        const chosenSuit = event.target.dataset.suit; 
        socket.emit("crazyeights_choose_suit", {suit: chosenSuit});
        suitPicker.classList.add("hidden"); 
    });
});

leaveButton.addEventListener("click", async function (event) {
    socket.emit("blackjack_leave_room");
    await fetch("/leave_room", {
        method:"POST", 
        credentials: "same-origin"
    });
    window.location.href = "/";
});

// Functions

function drawMyHand(handArray) {
    myHand.innerHTML = ""; 
    
    handArray.forEach(cardCode => {
        let img = document.createElement("img");
        img.src = `https://deckofcardsapi.com/static/img/${cardCode}.png`;
        img.className = "card-image clickable-card";
        img.dataset.code = cardCode; 
        
        img.addEventListener("click", () => {
            console.log("Attempting to play:", cardCode);
            socket.emit("crazyeights_play_card", {card_code: cardCode});
        });
        
        myHand.appendChild(img);
    });
}

function drawOpponentHand(position, cardCount) {
    const handContainer = document.getElementById(`hand-${position}`);

    handContainer.innerHTML = "";

    for (let i = 0; i < cardCount; i++) {
        let img = document.createElement("img");
        img.src = "https://deckofcardsapi.com/static/img/back.png"; 
        img.className = "card-image opponent-card"; 
        handContainer.appendChild(img);
    }
}

function updateSuitIcon(suitLetter) {
    if (suitLetter === 'H') suitIcon.innerText = "♥️";
    if (suitLetter === 'D') suitIcon.innerText = "♦️";
    if (suitLetter === 'C') suitIcon.innerText = "♣️";
    if (suitLetter === 'S') suitIcon.innerText = "♠️";
    if (suitLetter === "?") suitIcon.innerHTML = "❓";
    
    if (suitLetter === 'H' || suitLetter === 'D') {
        suitIcon.style.color = "#d32f2f";
    } else {
        suitIcon.style.color = "#212121";
    }
}