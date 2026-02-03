import {CreateCard, SetDivPosition, GetCardImageSrc} from './card.js';

// INITIAL DATA
const BOARD = document.getElementById('DIV_gameContainer')
const BOARD_WIDTH = BOARD.offsetWidth
const BOARD_HEIGHT = BOARD.offsetHeight


let card1 = {
    "code": "5S", 
    "image": "https://deckofcardsapi.com/static/img/5S.png", 
    "value": "5", 
    "suit": "SPADES"
}

let card2 = {
    "code": "QH", 
    "image": "https://deckofcardsapi.com/static/img/QH.png", 
    "value": "Q", 
    "suit": "HEARTS"
}

main();


function main() {
	CreateCard(BOARD, card1, 500, 300, true)
	CreateCard(BOARD, card2, 200, 300, false)
}
