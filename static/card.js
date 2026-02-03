import {SetDivPosition} from './utils.js'

export function GetCardImageSrc(card, faceUp) {
	if (faceUp == true) {
		return card.image;
	} else {
		return 'https://deckofcardsapi.com/static/img/back.png';
	}
}

export function CreateCard(BOARD, card_object, x, y, faceUp) {
	// create the div element
	const e = document.createElement('img');
	e.className = 'OBJ_card'
	e.src = GetCardImageSrc(card_object, faceUp)

	BOARD.appendChild(e);
	SetDivPosition(e, x, y);

	return e
}

