import {SetDivPosition} from './utils.js'

export function GetCardImageSrc(card, faceUp) {
	if (faceUp == true) {
		return card.image;
	} else {
		return 'https://deckofcardsapi.com/static/img/back.png';
	}
}

export function CreateCard(root, card_object, x, y, faceUp) {
	// create the div element
	const e = document.createElement('img');
	e.className = 'OBJ_card'
	e.src = GetCardImageSrc(card_object, faceUp)

	root.appendChild(e);
	SetDivPosition(e, x, y);

	return e
}

export function CreateDeckVisual(root, x, y) {
	const deck = [];
	for (let i = 0; i <= 51; i++) {
  		deck.push(CreateCard(root, {}, x+i/4, y+i/2, false));
	} 
	return deck;
}