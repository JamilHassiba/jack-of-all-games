import {CreateCard, GetCardImageSrc} from './Modules/card.js';
import {SetDivPosition, DragDiv} from './Modules/utils.js'

// data
const BOARD = document.getElementById('DIV_gameContainer')
const BOARD_WIDTH = BOARD.offsetWidth
const BOARD_HEIGHT = BOARD.offsetHeight

// Interacting with card api temporarily for ease of use
// (this will be replaced with information being sent from the server)
fetch('https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1')
  .then(r => r.json())
  .then(d => {main(d)})
  .catch(e => console.error("Fetch failed:", e));

// functions
function main(Deck) {
    fetch('https://deckofcardsapi.com/api/deck/' + Deck.deck_id + '/draw/?count=20')
        .then(r => r.json())
        .then(data => {

            if (data.success) {
                data.cards.forEach(HandleCard);
            }
            
        })
        .catch(e => console.error("Fetch failed: ", e));
}

function HandleCard(card, index) {
    if ( index >= 0 && index <= 14 ) {
        let faceUp = index == 14;
        // create a card onto the deck pile
        DragDiv(CreateCard(BOARD, card, BOARD_WIDTH/2, BOARD_HEIGHT/2 - index, faceUp));
    } else {
        // create a card into the 'hand'
        DragDiv(CreateCard(BOARD, card, BOARD_WIDTH/5 + (index-15) * 150, BOARD_HEIGHT/5*4, true));
    }
}