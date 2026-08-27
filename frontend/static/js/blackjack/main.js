import { socket } from "./socket.js";
import {
  createCardLink,
  addCardToHand,
  wipeHand,
  updatePlayerLabelHand,
} from "./cards.js";
import {
  addPlayer,
  getPlayerNum,
  resetSeats,
  resetUsernameLabels,
} from "./seats.js";
import {
  setupTabListeners,
  addEvent,
  bustEvent,
  winEvent,
  dealerWinEvent,
  joinRoomEvent,
  blackjackEvent,
  roundStartEvent,
} from "./ui.js";

console.log("blackjack.js is running...");

class PlayerInfo {
  constructor(id) {
    this.id = id;
    this.name = id.substring(1, 4).toLowerCase();
    this.hand = [];
    this.hand_total = 0;
    this.game_score = 0;
    this.state = "unknown";
    this.is_bust = false;
    this.has_blackjack = false;
  }
}

//// INITIALISATION ////

// References
let player_elements = {
  hand: document.getElementById("player-hand"),
  hand_total: document.getElementById("player-hand-total"),
  game_score: document.getElementById("player-game-score"),
};

let dealer_elements = {
  hand: document.getElementById("dealer-hand"),
  hand_total: document.getElementById("dealer-hand-total"),
};

// let other_players_container = document.getElementById("other-players");

let hit_button = document.getElementById("hit-btn");
let stand_button = document.getElementById("stand-btn");
const leave_button = document.getElementById("leave-btn");

let title = document.getElementById("game-status-p");

// Data
// Create socket object;


let this_player;

let players = new Map();

let room_state = "unknown";

const title_base = "";

//// START ////
title.innerHTML = title_base.concat("Waiting for the next round to start...");
CanRequestActions(false);
setupTabListeners();

// Events
hit_button.addEventListener("mousedown", HitButtonClicked);
stand_button.addEventListener("mousedown", StandButtonClicked);
leave_button.addEventListener("mousedown", LeaveButtonClicked);

//// METHODS ////

// Socket
socket.on("connect", function () {
  this_player = new PlayerInfo(socket.id);
  players.set(socket.id, this_player);
  resetSeats();
  document.getElementById("my-score-info").innerHTML = "You: 0 (+0)";
  socket.emit("blackjack_player_join");
});

socket.on("relay_game_state", function (data) {
  room_state = data.new_state;

  switch (room_state) {
    case "intermission":
      Game_EnteredIntermissionState();
      break;
    case "round_start":
      Game_EnteredRoundStartState();
      break;
    case "players_turn":
      Game_EnteredPlayersTurnState();
      break;
    case "dealer_turn":
      Game_EnteredDealersTurnState();
      break;
    case "score":
      Game_EnteredScoreState();
      break;
    case "cleanup":
      Game_EnteredCleanupState();
      break;
    case "evaluate_game":
      Game_EnteredEvaluateGameState();
      break;
  }
});

function UpdatePlayerField(
  id,
  field,
  value,
  thisplayer_callback = () => {},
  otherplayer_callback = () => {},
  dealer_callback = () => {},
) {
  let player = players.get(id);
  player[field] = value;

  if (id == socket.id) {
    // This player is this client's player
    thisplayer_callback(id, value);
  } else if (id == "dealer") {
    // This player is the dealer
    dealer_callback(id, value);
  } else {
    // This player is some other player
    otherplayer_callback(id, value);
  }
}
socket.on("relay_player_info", function (data) {
  console.log("relay_player_info received:", data);
  let id = data.id;
  let player = players.get(id);
  if (player == null) {
    player = new PlayerInfo(id);
    console.log(
      data.username,
      "joined the game with id",
      id,
      socket.id,
      "is this player",
    );
    if (data.username != undefined) {
      joinRoomEvent(data.username);
    }
    players.set(id, player); // Assign seat for new players (not self, not dealer)
    if (id != socket.id && id != "dealer") {
      addPlayer(data.username, id); // Use id as name for now
    }
  }

  if (data.username !== undefined) {
    player.name = data.username;
  }

  if (data.hand !== undefined)
    UpdatePlayerField(
      id,
      "hand",
      data.hand,
      ThisPlayer_HandUpdated,
      OtherPlayer_HandUpdated,
      Dealer_HandUpdated,
    );

  if (data.hand_total !== undefined)
    UpdatePlayerField(
      id,
      "hand_total",
      data.hand_total,
      ThisPlayer_HandTotalUpdated,
      OtherPlayer_HandTotalUpdated,
      Dealer_HandTotalUpdated,
    );

  if (data.game_score !== undefined)
    UpdatePlayerField(
      id,
      "game_score",
      data.game_score,
      ThisPlayer_GameScoreUpdated,
      OtherPlayer_GameScoreUpdated,
    );

  if (data.state !== undefined)
    UpdatePlayerField(
      id,
      "state",
      data.state,
      ThisPlayer_StateUpdated,
      OtherPlayer_StateUpdated,
    );

  if (data.is_bust !== undefined)
    UpdatePlayerField(
      id,
      "is_bust",
      data.is_bust,
      ThisPlayer_IsBust_Updated,
      OtherPlayer_IsBust_Updated,
      Dealer_IsBust_Updated,
    );

  if (data.has_blackjack !== undefined)
    UpdatePlayerField(
      id,
      "has_blackjack",
      data.has_blackjack,
      ThisPlayer_HasBlackjack_Updated,
      OtherPlayer_HasBlackjack_Updated,
      Dealer_HasBlackjack_Updated,
    );
});

socket.on("player_score_event", function (data) {
  let id = data.id;
  let old_score = data.old_score;
  let delta_score = data.delta_score;
  let new_score = data.new_score;

  if (id == this_player.id) {
    ThisPlayer_ScoreEvent(id, old_score, delta_score, new_score);
  } else {
    OtherPlayer_ScoreEvent(id, old_score, delta_score, new_score);
  }
});

socket.on("refresh_players", function (data) {
  // We need to clear all players, then the backend will
  // resend relay_player_info for remaining players
  console.log("refresh", data);
  players.clear();
  this_player = new PlayerInfo(socket.id);
  players.set(socket.id, this_player);
  resetSeats();
  resetUsernameLabels();
});

async function LeaveButtonClicked() {
  socket.emit("blackjack_player_leave");
  await fetch("/leave_room", {
    method: "POST",
    credentials: "same-origin",
  });
  window.location.href = "/";
}

// Player Actions
function HitButtonClicked() {
  if (this_player.state != "playing") return;
  if (room_state != "players_turn") return;

  socket.emit("blackjack_hit_request");

  lockHitButton();
  lockStandButton();
}

function lockHitButton() {
  hit_button.classList.add("disabled");
}

function unlockHitButton() {
  hit_button.classList.remove("disabled");
}

function lockStandButton() {
  stand_button.classList.add("disabled");
}

function unlockStandButton() {
  stand_button.classList.remove("disabled");
}

function StandButtonClicked() {
  if (this_player.state != "playing") return;
  if (room_state != "players_turn") return;

  socket.emit("blackjack_stand_request");

  lockHitButton();
  lockStandButton();
}

// This Player Handlers
function ThisPlayer_HandUpdated(playerid, new_hand) {
  // player_elements.hand.innerHTML = new_hand
  unlockHitButton();
  unlockStandButton();
  updatePlayerLabelHand(playerid, new_hand);
}
function ThisPlayer_HandTotalUpdated(playerid, new_hand_total) {
  // player_elements.hand_total.innerHTML = new_hand_total
  let seat = getPlayerNum(playerid);
  if (seat) {
    let player = players.get(playerid);
    if (new_hand_total > 21) {
      new_hand_total += " - Bust!";
    } else if (player.state == "finished") {
      new_hand_total += " - Stood!";
    } else if (player.state == "playing") {
      new_hand_total += " - Playing";
    } else if (player.state == "finished" && new_hand_total == 0) {
      // This has to be here bc the backend process goes like:
      // Round Ends
      // Players hand wiped and score set to 0
      // Players state then set to lobby

      // Otherwise there will be a brief period where the player total looks like:
      // 0 - Stood! which is wrong
      //
      new_hand_total = "0 - Waiting";
    }
    document.getElementById("score-p" + seat).innerHTML = new_hand_total;
  }
}
function ThisPlayer_GameScoreUpdated(playerid, new_game_score) {
  // console.log("my new score")
  // console.log(new_game_score)
  // player_elements.game_score.innerHTML = new_game_score
}
function ThisPlayer_ScoreEvent(
  playerid,
  old_score,
  delta_score,
  new_game_score,
) {
  document.getElementById("my-score-info").innerHTML =
    `You: ${new_game_score} (+${delta_score})`;
  if (delta_score > 0) {
    winEvent();
  } else if (delta_score == 0) {
    dealerWinEvent();
  }
}
function ThisPlayer_StateUpdated(playerid, new_state) {
  console.log(playerid, "state updated to", new_state);
  let player_seat = getPlayerNum(playerid);
  if (new_state == "finished") {
    let hand_total = document.getElementById("score-p" + player_seat).innerHTML;
    if (!hand_total.includes("Bust") && !hand_total.includes("Stood")) {
      hand_total = hand_total.replace(" - Playing", "");
      hand_total += " - Stood";
      document.getElementById("score-p" + player_seat).innerHTML = hand_total;
    }
  } else if (new_state == "lobby") {
    let hand_total = "0 - Waiting";
    document.getElementById("score-p" + player_seat).innerHTML = hand_total;
  }
  if (playerid == socket.id) {
    // This player's state changed so enable/disable btns
    // Kinda have to do this bc OtherPlayer_StateUpdated
    // calls this to avoid reusing logic
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
}

function ThisPlayer_IsBust_Updated(playerid, is_bust) {
  if (is_bust) {
    lockStandButton();
    lockHitButton();
    bustEvent();
  }
  // alert("You are bust!");
}
function ThisPlayer_HasBlackjack_Updated(playerid, has_blackjack) {
  // if (has_blackjack)
  // alert("Blackjack!");
  blackjackEvent();
}

// Other Player Handlers
function OtherPlayer_HandUpdated(playerid, new_hand) {
  updatePlayerLabelHand(playerid, new_hand);
}
function OtherPlayer_HandTotalUpdated(playerid, new_hand_total) {
  return ThisPlayer_HandTotalUpdated(playerid, new_hand_total);
}
function OtherPlayer_GameScoreUpdated(playerid, new_game_score) {
  // STUB
  return;
}
function OtherPlayer_ScoreEvent(playerid, old_score, delta_score, new_score) {
  let player = players.get(playerid);
  let name = player ? player.name || "Player" : "Player";
  let div = document.createElement("div");
  div.innerHTML = `${name}: ${new_score} (+${delta_score})`;
  div.id = `score-${playerid}`;
  // Remove existing if any
  let existing = document.getElementById(`score-${playerid}`);
  if (existing) existing.remove();
  document.getElementById("others-score-info").appendChild(div);
}
function OtherPlayer_StateUpdated(playerid, new_state) {
  ThisPlayer_StateUpdated(playerid, new_state); // Just reuse same logic - don't know why these need to be separate?
}
function OtherPlayer_IsBust_Updated(playerid, is_bust) {
  let playerName = players.get(playerid).name;
  bustEvent(playerName);
}
function OtherPlayer_HasBlackjack_Updated(playerid, has_blackjack) {
  let playerName = players.get(playerid).name;
  blackjackEvent(playerName);
}

// Dealer State Change Methods
function Dealer_HandUpdated(dealerid, new_hand) {
  updatePlayerLabelHand("dealer", new_hand);
}
function Dealer_HandTotalUpdated(dealerid, new_hand_total) {
  // dealer_elements.hand_total.innerHTML = new_hand_total
  new_hand_total =
    new_hand_total > 21 ? new_hand_total + " - Bust!" : new_hand_total;
  document.getElementById("dealer-score").innerHTML = new_hand_total;
}
function Dealer_IsBust_Updated(dealerid, is_bust) {
  // if (is_bust)
  // alert("Dealer went bust!");
  bustEvent("Dealer");
}
function Dealer_HasBlackjack_Updated(dealerid, has_blackjack) {
  // if (has_blackjack)
  // alert("Dealer has blackjack!");
  blackjackEvent("Dealer");
}

// Game State Change Methods
function Game_EnteredIntermissionState() {
  SetRoomStatus("Waiting for a round to begin...");
}
function Game_EnteredRoundStartState() {
  SetRoomStatus("Dealing initial cards...");
  roundStartEvent();
}
function Game_EnteredPlayersTurnState() {
  unlockHitButton();
  unlockStandButton();
  SetRoomStatus("Player's turn");
}
function Game_EnteredDealersTurnState() {
  SetRoomStatus("Dealer is playing...");
}
function Game_EnteredScoreState() {
  SetRoomStatus("Evaluating round");
}
function Game_EnteredCleanupState() {
  SetRoomStatus("Finishing round...");
}
function Game_EnteredEvaluateGameState() {
  SetRoomStatus("Evaluating game...");
}

// Utility
function CanRequestActions(bool) {
  hit_button.disabled = !bool;
  stand_button.disabled = !bool;
}

function SetRoomStatus(room_status) {
  title.innerHTML = room_status;
}
