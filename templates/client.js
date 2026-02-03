import {CreateCard, SetDivPosition, GetCardImageSrc} from './card.js';

// INITIAL DATA
const BOARD = document.getElementById('DIV_gameContainer')
const BOARD_WIDTH = BOARD.offsetWidth
const BOARD_HEIGHT = BOARD.offsetHeight

const SUITS = {
	HEARTS : 'H',
	SPADES : 'S',
	DIAMONDS : 'D',
	CLUBS : 'C',
}

const RANKS = {
	A : 'A',
	1 : '1',
	2 : '2',
	3 : '3',
	4 : '4',
	5 : '5',
	6 : '6',
	7 : '7',
	8 : '8',
	9 : '9',
	10 : '10',
	J : 'J',
	Q : 'Q',
	K : 'K',
}

main();

function main() {
	CreateCard(BOARD, BOARD_WIDTH/2, BOARD_HEIGHT/2, RANKS['5'], SUITS['HEARTS'], true)
	CreateCard(BOARD, BOARD_WIDTH/2 + 300, 300, RANKS['A'], SUITS['SPADES'], false)
}
