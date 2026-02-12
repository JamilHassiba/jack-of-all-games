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

	constructor(root, cards, x, y) {
		this.root = root;
		this.cards = cards;
		this.x = x
		this.y = y
		this.setPosition(x, y)
	}

	// constructor overload: generates a deck from a list of card jsons
	static fromJSONs(root, card_jsons, x, y) {
		return new Deck(root, Deck.#generateCardObjectsFromJSONs(root, card_jsons, x, y))
	}
	// constructor overload: generates a deck from a list of already made card objects
	static fromCards(root, cards, x, y) {
		return new Deck(root, cards, x, y)
	}
	// constructor overload: generates an empty deck
	static empty(root, x, y) {
		return new Deck(root, [], x, y)
	}

	setPosition(x, y) {
		this.x = x
		this.y = y
		for (let i = 0; i < this.cards.length; i++) {
			let x_offset = i/4;
			let y_offset = i/2;
			this.cards[i].setPosition(x + x_offset, y + y_offset)
		}
	}

	pushCard(card) {
		this.cards.push(card)
		card.setPosition(this.x + (this.cards.length-1)/4, this.y + (this.cards.length-1)/2)
	}

	peekTopCard() {
		return this.cards[this.cards.length-1]
	}

	getTopCard() {
		return this.cards.pop();
	}

	// currently only deals between 2 players, TODO: deal between n players
	dealCards() {
		let my_cards = [];
		let their_cards = [];

		for (let i = this.cards.length-1; i >= 0; i--) {
			let card = this.cards[i]

			if (i%2 == 0) {my_cards.push(card)}
			else {their_cards.push(card)}
			
		}

		this.cards = [];
		return [my_cards, their_cards]
	}

	destroy() {
		this.cards.forEach(function(card) {card.destroy()});
	}
}