// Seat assignment: maps socket ids to the five table positions.

import { socket } from "./socket.js";

// Adding Players to the game
document.getElementById("seat-p1").innerHTML = "You!";

export function addPlayer(name, id) {
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

export function getPlayerNum(player_id) {
  // console.log(player_id, "----")
  if (player_id == socket.id) {
    return 1;
  }
  for (let num in playerSeats) {
    // console.log(playerSeats[num])
    if (playerSeats[num] == player_id) {
      return num;
    }
  }
  return null;
}

export function resetUsernameLabels() {
  for (let seat = 2; seat <= 5; seat++) {
    document.getElementById("seat-p" + seat).innerHTML =
      "Player " + seat + " - Empty";
    document.getElementById("score-p" + seat).innerHTML = "0";
    document.getElementById("hand-p" + seat).innerHTML = "";
  }
}
