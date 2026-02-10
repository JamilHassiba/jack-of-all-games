import {Card} from '../card.js';
import {Deck} from '../deck.js'
import { io } from "https://cdn.socket.io/4.6.1/socket.io.esm.min.js";

console.log("war.js running...");

// Get references to html elements
const Title = document.getElementById("Title");

const gameboard_DIV = document.getElementById("DIV_gameBoard");
const gameboard_WIDTH = gameboard_DIV.offsetWidth;
const gameboard_HEIGHT = gameboard_DIV.offsetHeight; 

const mypile_position = {x : gameboard_WIDTH/2, y : gameboard_HEIGHT/4*3}
const theirpile_position = {x : gameboard_WIDTH/2, y : gameboard_HEIGHT/4}
const myplay_position = {x : gameboard_WIDTH/2 + 150, y : gameboard_HEIGHT/2}
const theirplay_position = {x : gameboard_WIDTH/2 - 150, y : gameboard_HEIGHT/2}

// Local state
let haveplayedcard = false;

// Create socket object;
var socket = io();

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
	let deck = new Deck(gameboard_DIV, card_jsons);
}

// let deck = CreateDeckVisual(gameboard_DIV, gameboard_WIDTH/2, gameboard_HEIGHT/2)
// let piles = await DealCards(deck)
// let mypile = piles[0]
// let theirpile = piles[1]

// console.log(mypile)
// console.log(theirpile)

// let mypile_clickbox = CreateCardClickbox(
// 	gameboard_DIV, 
// 	mypile_position.x + mypile.length/8, 
// 	mypile_position.y + mypile.length/4)
// mypile_clickbox.addEventListener("click", PlayMyCard)

function PlayMyCard() {
	let topcard = mypile[mypile.length-1]
	if (topcard != null && !haveplayedcard) {
		MoveCard(topcard, myplay_position.x, myplay_position.y);
		haveplayedcard = true;
	}
}

/*	@param deck: an array of card elements
	@returns piles[]: 0th element is an array of 'my cards', 1st element is an array of 'their cards'

	Takes the deck, and deals the cards, one at a time, alternating between me and them */
async function DealCards(deck) {
	let delay_in_seconds = 0.05
	let mypile = [];
	let theirpile = [];

	for (let i = 0; i < deck.length; i++) {
		let topcard_index = deck.length - i - 1
		let card = deck[topcard_index]

		if (i%2 == 0) {
			let x_offset = mypile.length/4
			let y_offset = mypile.length/2
			MoveCard(card, mypile_position.x + x_offset, mypile_position.y + y_offset);
			mypile.push(card);
		} else {
			let x_offset = theirpile.length/4
			let y_offset = theirpile.length/2
			MoveCard(card, theirpile_position.x + x_offset, theirpile_position.y + y_offset);
			theirpile.push(card);
		}
		await new Promise(resolve => setTimeout(resolve, delay_in_seconds/1000));
	}

	return [mypile, theirpile]
}