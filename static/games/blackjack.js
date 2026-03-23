import { PlayerInfo } from "../classes/playerinfo.js";
import { PlayerLabel } from "../classes/playerlabel.js";

console.log("blackjack.js is running...")

//// INITIALISATION ////

// References
let player_elements = {
    "hand": document.getElementById("player-hand"),
    "hand_total": document.getElementById("player-hand-total"),
    "game_score": document.getElementById("player-game-score"),
}

let dealer_elements = {
    "hand": document.getElementById("dealer-hand"),
    "hand_total": document.getElementById("dealer-hand-total"),
}

// let other_players_container = document.getElementById("other-players");

let hit_button = document.getElementById("hit-btn");
let stand_button = document.getElementById("stand-btn");

let title = document.getElementById("game-status-p")

// Data
// Create socket object;
var socket = io();

let this_player;

let players = new Map;
let player_labels = new Map;
let playerSeats;

let room_state = "unknown";

const title_base = "";

//// START ////
title.innerHTML = title_base.concat("Waiting for the next round to start...")
CanRequestActions(false);

// Events
hit_button.addEventListener("mousedown", HitButtonClicked);
stand_button.addEventListener("mousedown", StandButtonClicked);

//// METHODS ////

// Socket
socket.on('connect', function () {
    this_player = new PlayerInfo(socket.id)
    players.set(socket.id, this_player)
    playerSeats = {
        1: socket.id,
        2: null,
        3: null,
        4: null,
        5: null
    }
    document.getElementById("my-score-info").innerHTML = "You: 0 (+0)";
    socket.emit('blackjack_player_join');
});

socket.on('relay_game_state', function (data) {
    room_state = data.new_state

    switch (room_state) {
        case 'intermission': Game_EnteredIntermissionState(); break;
        case 'round_start': Game_EnteredRoundStartState(); break;
        case 'players_turn': Game_EnteredPlayersTurnState(); break;
        case 'dealer_turn': Game_EnteredDealersTurnState(); break;
        case 'score': Game_EnteredScoreState(); break;
        case 'cleanup': Game_EnteredCleanupState(); break;
        case 'evaluate_game': Game_EnteredEvaluateGameState(); break;
    }
});

function UpdatePlayerField(id, field, value, thisplayer_callback = () => { }, otherplayer_callback = () => { }, dealer_callback = () => { }) {
    let player = players.get(id)
    player[field] = value

    if (id == socket.id) {
        // This player is this client's player
        thisplayer_callback(id, value)
    } else if (id == "dealer") {
        // This player is the dealer
        dealer_callback(id, value)
    } else {
        // This player is some other player
        otherplayer_callback(id, value)
    }
}
function UpdatePlayerLabel(id, player) {
    let label = player_labels.get(id)
    if (!label) {
        label = new PlayerLabel(id) // RM?
        // other_players_container.appendChild(label.e) // RM
        player_labels.set(id, label)
    }

    label.update(player);
}
socket.on('relay_player_info', function (data) {
    console.log("relay_player_info received:", data);
    let id = data.id;
    let player = players.get(id);
    if (player == null) {
        player = new PlayerInfo(id);
        players.set(id, player)        // Assign seat for new players (not self, not dealer)
        if (id != socket.id && id != "dealer") {
            addPlayer(data.username, id); // Use id as name for now
        }
    }

    if (data.username !== undefined) {
        player.name = data.username;
    }

    if (data.hand !== undefined)
        UpdatePlayerField(id, "hand", data.hand, ThisPlayer_HandUpdated, OtherPlayer_HandUpdated, Dealer_HandUpdated)

    if (data.hand_total !== undefined)
        UpdatePlayerField(id, "hand_total", data.hand_total, ThisPlayer_HandTotalUpdated, OtherPlayer_HandTotalUpdated, Dealer_HandTotalUpdated)

    if (data.game_score !== undefined)
        UpdatePlayerField(id, "game_score", data.game_score, ThisPlayer_GameScoreUpdated, OtherPlayer_GameScoreUpdated)

    if (data.state !== undefined)
        UpdatePlayerField(id, "state", data.state, ThisPlayer_StateUpdated, OtherPlayer_StateUpdated)

    if (data.is_bust !== undefined)
        UpdatePlayerField(id, "is_bust", data.is_bust, ThisPlayer_IsBust_Updated, OtherPlayer_IsBust_Updated, Dealer_IsBust_Updated)

    if (data.has_blackjack !== undefined)
        UpdatePlayerField(id, "has_blackjack", data.has_blackjack, ThisPlayer_HasBlackjack_Updated, OtherPlayer_HasBlackjack_Updated, Dealer_HasBlackjack_Updated)

    if (player != this_player && id != "dealer")
        UpdatePlayerLabel(id, player)
})

socket.on('player_score_event', function (data) {
    let id = data.id
    let old_score = data.old_score
    let delta_score = data.delta_score
    let new_score = data.new_score

    if (id == this_player.id) {
        ThisPlayer_ScoreEvent(id, old_score, delta_score, new_score)
    } else {
        OtherPlayer_ScoreEvent(id, old_score, delta_score, new_score)
    }
})

// Player Actions
function HitButtonClicked() {
    if (this_player.state != "playing") return;
    if (room_state != "players_turn") return;

    socket.emit("blackjack_hit_request");

    lockHitButton()
    lockStandButton()
};

function lockHitButton() {
    hit_button.classList.add("disabled")
}

function unlockHitButton() {
    hit_button.classList.remove("disabled")
}

function lockStandButton() {
    stand_button.classList.add("disabled")
}

function unlockStandButton() {
    stand_button.classList.remove("disabled")
}

function StandButtonClicked() {
    if (this_player.state != "playing") return;
    if (room_state != "players_turn") return;

    socket.emit("blackjack_stand_request");

    lockHitButton()
    lockStandButton()
}

// This Player Handlers
function ThisPlayer_HandUpdated(playerid, new_hand) {
    // player_elements.hand.innerHTML = new_hand
    unlockHitButton()
    unlockStandButton()
    updatePlayerLabelHand(playerid, new_hand)
}
function ThisPlayer_HandTotalUpdated(playerid, new_hand_total) {
    // player_elements.hand_total.innerHTML = new_hand_total
    let seat = getPlayerNum(playerid)
    if (seat) {
        document.getElementById("score-p" + seat).innerHTML = new_hand_total
    }
}
function ThisPlayer_GameScoreUpdated(playerid, new_game_score) {
    console.log("my new score")
    console.log(new_game_score)
    // player_elements.game_score.innerHTML = new_game_score
}
function ThisPlayer_ScoreEvent(playerid, old_score, delta_score, new_game_score) {
    document.getElementById("my-score-info").innerHTML = `You: ${new_game_score} (+${delta_score})`;
}
function ThisPlayer_StateUpdated(playerid, new_state) {
    switch (new_state) {
        case "lobby": {
            break;
        }

        case "playing": {
            CanRequestActions(true);
            break;
        }

        case "finished": {
            CanRequestActions(false);
            break;
        }
    }
}
function ThisPlayer_IsBust_Updated(playerid, is_bust) {
    if (is_bust) {
        lockStandButton()
        lockHitButton()
    }
    // alert("You are bust!");
}
function ThisPlayer_HasBlackjack_Updated(playerid, has_blackjack) {
    // if (has_blackjack)
        // alert("Blackjack!");
}

// Other Player Handlers
function OtherPlayer_HandUpdated(playerid, new_hand) {
    updatePlayerLabelHand(playerid, new_hand)
}
function OtherPlayer_HandTotalUpdated(playerid, new_hand_total) {
    return ThisPlayer_HandTotalUpdated(playerid, new_hand_total)
}
function OtherPlayer_GameScoreUpdated(playerid, new_game_score) {
    // STUB
    return
}
function OtherPlayer_ScoreEvent(playerid, old_score, delta_score, new_score) {
    let player = players.get(playerid);
    let name = player ? (player.name || "Player") : "Player";
    let div = document.createElement("div");
    div.innerHTML = `${name}: ${new_score} (+${delta_score})`;
    div.id = `score-${playerid}`;
    // Remove existing if any
    let existing = document.getElementById(`score-${playerid}`);
    if (existing) existing.remove();
    document.getElementById("others-score-info").appendChild(div);
}
function OtherPlayer_StateUpdated(playerid, new_state) {
    switch (new_state) {
        case "lobby": {
            break;
        }

        case "playing": {
            break;
        }

        case "finished": {
            break;
        }
    }
}
function OtherPlayer_IsBust_Updated(playerid, is_bust) {

}
function OtherPlayer_HasBlackjack_Updated(playerid, has_blackjack) {

}

// Dealer State Change Methods
function Dealer_HandUpdated(dealerid, new_hand) {
    updatePlayerLabelHand("dealer", new_hand)
}
function Dealer_HandTotalUpdated(dealerid, new_hand_total) {
    // dealer_elements.hand_total.innerHTML = new_hand_total
    document.getElementById("dealer-score").innerHTML = new_hand_total
}
function Dealer_IsBust_Updated(dealerid, is_bust) {
    // if (is_bust)
        // alert("Dealer went bust!");
}
function Dealer_HasBlackjack_Updated(dealerid, has_blackjack) {
    // if (has_blackjack)
        // alert("Dealer has blackjack!");
}



// Game State Change Methods
function Game_EnteredIntermissionState() {
    SetRoomStatus("Waiting for a round to begin...")
}
function Game_EnteredRoundStartState() {
    SetRoomStatus("Dealing initial cards...")
}
function Game_EnteredPlayersTurnState() {
    unlockHitButton()
    unlockStandButton()
    SetRoomStatus("Player's turn")
}
function Game_EnteredDealersTurnState() {
    SetRoomStatus("Dealer is playing...")
}
function Game_EnteredScoreState() {
    SetRoomStatus("Evaluating round")
}
function Game_EnteredCleanupState() {
    SetRoomStatus("Finishing round...")
}
function Game_EnteredEvaluateGameState() {
    SetRoomStatus("Evaluating game...")
}

// Utility
function CanRequestActions(bool) {
    hit_button.disabled = !bool;
    stand_button.disabled = !bool;
}

function SetRoomStatus(room_status) {
    title.innerHTML = room_status;
}

// Card Utility
function createCard(id) {
    return `<img src="${createCardLink(id)}" class="OBJ_card" alt="${id}">`
}

function createCardLink(id) {
    return "https://deckofcardsapi.com/static/img/" + id + ".png"
}

function addCardToHand(hand_container, card_id, selfplayer = false, dealer = false) {
    // if first 2 cards are invisible - replace their source with card
    // and make visible again - else add new card to hand
    let cards = hand_container.getElementsByClassName("OBJ_card")
    for (let i = 0; i < cards.length; i++) {
        if (cards[i].classList.contains("back")) {
            cards[i].src = createCardLink(card_id)
            cards[i].alt = card_id
            cards[i].classList.remove("hidden")
            cards[i].classList.remove("back")
            animateDeal(cards[i])

            if (selfplayer) {
                // If self player make cards bigger
                cards[i].classList.add("self")
            }
            return;
        }
    }
    let card = createCard(card_id)
    if (selfplayer) {
        card = card.replace("OBJ_card", "OBJ_card self")
    }
    hand_container.innerHTML += card
    animateDeal(hand_container.lastElementChild)
}

function animateDeal(cardEl) {
    // deals card with a flip animation for smoothness
    cardEl.classList.remove("dealing")
    void cardEl.offsetWidth  // force reflow so re-adding works
    cardEl.classList.add("dealing")
}


function wipeHand(hand_container, is_dealer = false) {
    // Recommended because it preserves layout of page
    // make first 2 cards invisible - then remove extra cards
    let cards = hand_container.getElementsByClassName("OBJ_card")
    for (let i = cards.length - 1; i >= 0; i--) { // iterate backwards because hand is a live collection
        if (i < 2) {
            cards[i].src = "https://deckofcardsapi.com/static/img/back.png"
            cards[i].alt = "Card back"
            cards[i].classList.add("hidden")
            cards[i].classList.add("back")
        } else {
            cards[i].remove()
        }
    }
    if (is_dealer) {
        // Dealer should always show 2 back cards
        for (let i = 0; i < 2; i++) {
            cards[i].classList.remove("hidden")
        }
    }
}

function bruteWipeHand(hand_container) {
    // Not Recommended because it will shift layout of page around
    hand_container.innerHTML = ""
}
function updatePlayerLabelHand(player_id, hand) {
    let handcontainer
    if (player_id == "dealer") {
        handcontainer = document.getElementById("dealer-hand")
    } else {
        handcontainer = document.getElementById("hand-p" + getPlayerNum(player_id))
    }
    let isSelfPlayer = (player_id == socket.id) || (player_id == "dealer")
    wipeHand(handcontainer, player_id == "dealer")
    for (let card_id of hand) {
        addCardToHand(handcontainer, card_id, isSelfPlayer)
    }
}


// Adding Players to the game
document.getElementById("seat-p1").innerHTML = "You!"

function addPlayer(name, id) {
    // Find next available seat (2-5)
    for (let seat = 2; seat <= 5; seat++) {
        if (playerSeats[seat] === null) {
            playerSeats[seat] = id;
            document.getElementById("seat-p" + seat).innerHTML = name;
            // Initialize score display
            let div = document.createElement("div");
            div.innerHTML = `${name}: 0 (+0)`;
            div.id = `score-${id}`;
            document.getElementById("others-score-info").appendChild(div);
            break;
        }
    }
}

function getPlayerNum(player_id) {
    console.log(player_id, "----")
    for (let num in playerSeats) {
        console.log(playerSeats[num])
        if (playerSeats[num] == player_id) {
            return num
        }
    }
    return null
}