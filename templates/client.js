
const BOARD = document.getElementById('DIV_gameContainer')
const BOARD_WIDTH = BOARD.offsetWidth
const BOARD_HEIGHT = BOARD.offsetHeight

/* SetDivPosition()
@param div  : DOM div element
@param x    : x position of the elements centre
@param y    : y position of the elements centre
*/
function SetDivPosition(div, x, y) {
	let width = div.offsetWidth;
	let height = div.offsetHeight;
	div.style.left = x-(width/2)+'px';
	div.style.top = y-(width/2)+'px';
}

/* CreateCardObject()

*/
function CreateCardObject(xIn, yIn, rankIn, suitIn) {
	// create the div element
	const e = document.createElement('div');
	e.className = 'OBJ_card'
	e.style.position = 'absolute';
	e.style.width = 100+'px';
	e.style.height = 140+'px';

	// create the image element (div > element)
	const i = document.createElement('img');
	i.style['object-fit'] = 'cover';
	i.style.width = 100+'%';
	i.style.height = 100+'%';
	i.src = 'https://deckofcardsapi.com/static/img/5S.png';
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

CreateCardObject(BOARD_WIDTH/2, BOARD_HEIGHT/2, "A", "H")