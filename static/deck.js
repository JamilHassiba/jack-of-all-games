import {Card} from './card.js';

export class Deck {
	/*
	        {
            "code": "6H", 
            "image": "https://deckofcardsapi.com/static/img/6H.png", 
            "images": {
                          "svg": "https://deckofcardsapi.com/static/img/6H.svg", 
                          "png": "https://deckofcardsapi.com/static/img/6H.png"
                      }, 
            "value": "6", 
            "suit": "HEARTS"
        },
	*/
	static #generateCardObjectsFromJSONs(root, card_jsons) {
		let cards = []
		card_jsons.forEach(function(json) {
			cards.push(new Card(root, json, false));
		})
		return cards
	}

	constructor(root, card_jsons) {
		this.cards = Deck.generateCardObjectsFromJSONs
	}

}