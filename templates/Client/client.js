import {CreateCard, GetCardImageSrc} from './Modules/card.js';
import {SetDivPosition, DragDiv} from './Modules/utils.js'

// data
const BOARD = document.getElementById('DIV_gameContainer')
const BOARD_WIDTH = BOARD.offsetWidth
const BOARD_HEIGHT = BOARD.offsetHeight

export let topZIndex = 1


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
let card3 = {
    "code": "AS", 
    "image": "https://deckofcardsapi.com/static/img/AS.png", 
    "value": "A", 
    "suit": "SPADES"
}
let card4 = {
    "code": "4C", 
    "image": "https://deckofcardsapi.com/static/img/4C.png", 
    "value": "4", 
    "suit": "CLUBS"
}
let card5 = {
    "code": "6D", 
    "image": "https://deckofcardsapi.com/static/img/6D.png", 
    "value": "6", 
    "suit": "DIAMONDS"
}


// functions


function main() {
	DragDiv(CreateCard(BOARD, card1, 850, 300, false))
    DragDiv(CreateCard(BOARD, card1, 850, 295, false))
    DragDiv(CreateCard(BOARD, card1, 850, 290, false))
    DragDiv(CreateCard(BOARD, card1, 850, 285, false))
    DragDiv(CreateCard(BOARD, card1, 850, 280, true))

    DragDiv(CreateCard(BOARD, card2, 100, 450, true))
    DragDiv(CreateCard(BOARD, card3, 250, 450, true))
    DragDiv(CreateCard(BOARD, card4, 400, 450, true))
    DragDiv(CreateCard(BOARD, card5, 550, 450, true))
}

// init
main();