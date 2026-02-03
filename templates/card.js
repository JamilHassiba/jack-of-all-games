

// FUNCTIONS
/* SetDivPosition()
@param div  : DOM div element
@param x    : x position of the elements centre
@param y    : y position of the elements centre
*/
export function SetDivPosition(div, x, y) {
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
export function GetCardImageSrc(rank, suit, faceUp) {
	if (faceUp == true) {
		return 'https://deckofcardsapi.com/static/img/' + rank + suit + '.png';
	} else {
		return 'https://deckofcardsapi.com/static/img/back.png';
	}
}

/* CreateCard()
@param xIn      : int
@param yIn      : int
@param rankIn   : RANK(s)
@param suitIn   : SUIT(s)
@param faceUpIn : boolean

Creates the DOM elements used for rendering the card, and adds them to the html
Sets the DOM's position on the screen
Returns a card object:
	fields
		x, y, rank, suit, faceUp, e (element)
*/
export function CreateCard(BOARD, xIn, yIn, rankIn, suitIn, faceUpIn) {
	// create the div element
	const e = document.createElement('div');
	e.className = 'OBJ_card'
	e.style.position = 'absolute';

	// create the image element (div > element)
	const i = document.createElement('img');
	i.style['object-fit'] = 'cover';
	i.style.width = 100+'%';
	i.style.height = 100+'%';
	i.src = GetCardImageSrc(rankIn, suitIn, faceUpIn);
	e.appendChild(i);

	BOARD.appendChild(e);
	SetDivPosition(e, xIn, yIn);

	const card = {
		x: xIn,
		y: yIn,
		rank: rankIn,
		suit: suitIn,
		faceUp: faceUpIn,
		e: e,
	}

	return card
}

