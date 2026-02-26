import {Card} from '../card.js';
import {Deck} from '../deck.js';
import {SendData} from '../utils.js';
//import { io } from "https://cdn.socket.io/4.6.1/socket.io.esm.min.js";

console.log("war.js running...");

// Get references to html elements
const Title = document.getElementById("Title");

const BOARD = document.getElementById("DIV_gameBoard");
const WIDTH = BOARD.offsetWidth;
const HEIGHT = BOARD.offsetHeight; 

const DECK_POSITIONS = {
	player1: {
		drawDeck: {x: WIDTH/2, y: HEIGHT/4*3},
		fightDeck: {x: WIDTH/2 + 150, y: HEIGHT/2},
		winDeck: {x: WIDTH/2 - 150, y: HEIGHT/4*3},
	},
	player2: {
		drawDeck: {x: WIDTH/2, y: HEIGHT/4},
		fightDeck: {x: WIDTH/2 - 150, y: HEIGHT/2},
		winDeck: {x: WIDTH/2 + 150, y: HEIGHT/4},
	}
}

// Local state
let haveplayedcard = false;

// Create socket object;
//var socket = io();

// Set the title
Title.innerHTML = "WAR | 0123";
// will be: Title.innerHTML = "WAR | {{ code }}"


////// TEMP CODE FOR GENERATING A FAKE DECK //////
fetch('https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1')
	.then(r => r.json())
	.then(deck => {
		console.log("\tdeck fetched")
		fetch('https://deckofcardsapi.com/api/deck/' + deck.deck_id + '/draw/?count=52')
			.then(r => r.json())
			.then(data => {
					console.log("\tcards fetched")

					let card_jsons = []
					if (data.success) {
					    data.cards.forEach(function(card_json) {card_jsons.push(card_json)});
					}
					main(card_jsons);

				})
			.catch(e => console.error("Fetch failed: ", e));
		})
  	.catch(e => console.error("Fetch failed:", e));

function main(card_jsons) {
	console.log("main is running")
	let main_deck = Deck.fromJSONs(BOARD, card_jsons);
	main_deck.setPosition(WIDTH/2, HEIGHT/2)

	setTimeout(function() {
		let cards = main_deck.dealCards()

		let p1 = {
			drawDeck: Deck.fromCards(BOARD, cards[0], DECK_POSITIONS.player1.drawDeck.x, DECK_POSITIONS.player1.drawDeck.y),
			fightDeck: Deck.empty(BOARD, DECK_POSITIONS.player1.fightDeck.x, DECK_POSITIONS.player1.fightDeck.y),
			winDeck: Deck.empty(BOARD, DECK_POSITIONS.player1.winDeck.x, DECK_POSITIONS.player1.winDeck.y)
		}
		let p2 = {
			drawDeck: Deck.fromCards(BOARD, cards[1], DECK_POSITIONS.player2.drawDeck.x, DECK_POSITIONS.player2.drawDeck.y),
			fightDeck: Deck.empty(BOARD, DECK_POSITIONS.player2.fightDeck.x, DECK_POSITIONS.player2.fightDeck.y),
			winDeck: Deck.empty(BOARD, DECK_POSITIONS.player2.winDeck.x, DECK_POSITIONS.player2.winDeck.y),
		}

		let clickbox = Card.CreateCardClickbox(BOARD, p1.drawDeck.x, p1.drawDeck.y)
		clickbox.addEventListener("click", function() {PlayMyCard(p1.drawDeck, p1.fightDeck)})
	}, 1000)
}

async function PlayMyCard(drawDeck, fightDeck) {
	if (haveplayedcard && false) {return;}

	let card = drawDeck.getTopCard();
	if (card != null) {
		haveplayedcard = true;
		card.flip();
		fightDeck.pushCard(card);

		// send data to server

		let response = await SendData("/test_give_data", {})
		console.log(response)
		console.log(response["name"])
		console.log(typeof(response))

		let response2 = await SendData("/draw_card", {})
		console.log(response2)

		// const formData = new FormData();
		// formData.append("card", "5H");
		// console.log(formData);

		// fetch("/draw_card", {
		// 	method: "POST",
		// 	body: formData,
		// })
	}
}
