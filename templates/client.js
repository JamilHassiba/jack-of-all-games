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

// FUNCTIONS
/* SetDivPosition()
@param div  : DOM div element
@param x    : x position of the elements centre
@param y    : y position of the elements centre
*/
function SetDivPosition(div, x, y) {
	let width = div.offsetWidth;
	let height = div.offsetHeight;
	div.style.left = x-(width/2)+'px';
	div.style.top = y-(height/2)+'px';
}

/* GetCardImageSrc()
@param rank  : RANK
@param suit  : SUIT
@returns src : a url for that cards image
*/
function GetCardImageSrc(rank, suit) {
	console.log('https://deckofcardsapi.com/static/img/' + rank + suit + '.png')
	return 'https://deckofcardsapi.com/static/img/' + rank + suit + '.png';
}

/* CreateCardObject()

*/
function CreateCardObject(xIn, yIn, rankIn, suitIn) {
	// create the div element
	const e = document.createElement('div');
	e.className = 'OBJ_card'
	e.style.position = 'absolute';

	// create the image element (div > element)
	const i = document.createElement('img');
	i.style['object-fit'] = 'cover';
	i.style.width = 100+'%';
	i.style.height = 100+'%';
	i.src = GetCardImageSrc(rankIn, suitIn);
	e.appendChild(i);

	BOARD.appendChild(e);
	SetDivPosition(e, xIn, yIn);

	const card = {
		x: xIn,
		y: yIn,
		rank: rankIn,
		suit: suitIn,
		e: e,
	}

	return card
}

function main() {
	CreateCardObject(BOARD_WIDTH/2, BOARD_HEIGHT/2, RANKS['5'], SUITS['HEARTS'])
}
