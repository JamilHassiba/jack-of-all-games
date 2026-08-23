// Card and hand rendering helpers for the blackjack table.

import { getPlayerNum } from "./seats.js";
import { socket } from "./socket.js";

// Card Utility
export function createCard(id) {
  return `<img src="${createCardLink(id)}" class="OBJ_card" alt="${id}">`;
}

export function createCardLink(id) {
  return "https://deckofcardsapi.com/static/img/" + id + ".png";
}

export function addCardToHand(
  hand_container,
  card_id,
  selfplayer = false,
  dealer = false,
) {
  // if first 2 cards are invisible - replace their source with card
  // and make visible again - else add new card to hand
  let cards = hand_container.getElementsByClassName("OBJ_card");
  for (let i = 0; i < cards.length; i++) {
    if (cards[i].classList.contains("back")) {
      cards[i].src = createCardLink(card_id);
      cards[i].alt = card_id;
      cards[i].classList.remove("hidden");
      cards[i].classList.remove("back");
      animateDeal(cards[i]);

      if (selfplayer) {
        // If self player make cards bigger
        cards[i].classList.add("self");
      }
      return;
    }
  }
  let card = createCard(card_id);
  if (selfplayer) {
    card = card.replace("OBJ_card", "OBJ_card self");
  }
  hand_container.innerHTML += card;
  animateDeal(hand_container.lastElementChild);
}

export function animateDeal(cardEl) {
  // deals card with a flip animation for smoothness
  cardEl.classList.remove("dealing");
  void cardEl.offsetWidth; // force reflow so re-adding works
  cardEl.classList.add("dealing");
}

export function wipeHand(hand_container, is_dealer = false) {
  // Recommended because it preserves layout of page
  // make first 2 cards invisible - then remove extra cards
  let cards = hand_container.getElementsByClassName("OBJ_card");
  for (let i = cards.length - 1; i >= 0; i--) {
    // iterate backwards because hand is a live collection
    if (i < 2) {
      cards[i].src = "https://deckofcardsapi.com/static/img/back.png";
      cards[i].alt = "Card back";
      cards[i].classList.add("hidden");
      cards[i].classList.add("back");
    } else {
      cards[i].remove();
    }
  }
  if (is_dealer) {
    // Dealer should always show 2 back cards
    for (let i = 0; i < 2; i++) {
      cards[i].classList.remove("hidden");
    }
  }
}

export function bruteWipeHand(hand_container) {
  // Not Recommended because it will shift layout of page around
  hand_container.innerHTML = "";
}
export function updatePlayerLabelHand(player_id, hand) {
  let handcontainer;
  if (player_id == "dealer") {
    handcontainer = document.getElementById("dealer-hand");
  } else {
    handcontainer = document.getElementById("hand-p" + getPlayerNum(player_id));
  }
  let isSelfPlayer = player_id == socket.id || player_id == "dealer";
  wipeHand(handcontainer, player_id == "dealer");
  for (let card_id of hand) {
    addCardToHand(handcontainer, card_id, isSelfPlayer);
  }
}
