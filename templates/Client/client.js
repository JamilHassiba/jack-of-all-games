import {CreateCard, GetCardImageSrc} from './Modules/card.js';
import {SetDivPosition, DragDiv} from './Modules/utils.js'

// data
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


// functions


function main() {
	let e1 = CreateCard(BOARD, card1, 500, 300, true)
	let e2 = CreateCard(BOARD, card2, 200, 300, false)
    DragDiv(e1)
}

// init
main();