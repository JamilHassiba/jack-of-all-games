
export function SetDivPosition(div, x, y) {
	let width = div.offsetWidth;
	let height = div.offsetHeight;
	div.style.left = x-(width/2)+'px';
	div.style.top = y-(height/2)+'px';
}


export function GetCardImageSrc(card, faceUp) {
	if (faceUp == true) {
		return card.image
	} else {
		return 'https://deckofcardsapi.com/static/img/back.png';
	}
}

export function CreateCard(BOARD, card_object, x, y, faceUp) {
	// create the div element
	const e = document.createElement('div');
	e.className = 'OBJ_card'

	// create the image element (div > element)
	const i = document.createElement('img');
	i.className = 'IMG_card'
	i.src = GetCardImageSrc(card_object, faceUp);
	e.appendChild(i);

	BOARD.appendChild(e);
	SetDivPosition(e, x, y);
}

