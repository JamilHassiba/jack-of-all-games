import {CreateCard, CreateDeckVisual, MoveCard} from '../card.js';
import { io } from "https://cdn.socket.io/4.6.1/socket.io.esm.min.js";

console.log("war.js running...");

// Get references to html elements
const Title = document.getElementById("Title");

// const myHand_DIV = document.getElementById("DIV_myHand");
// const opponentHand_DIV = document.getElementById("DIV_opponentHand");

const gameboard_DIV = document.getElementById("DIV_gameBoard");
const gameboard_WIDTH = gameboard_DIV.offsetWidth;
const gameboard_HEIGHT = gameboard_DIV.offsetHeight; 

const mypile_position = {x : gameboard_WIDTH/2, y : gameboard_HEIGHT/4*3}
const theirpile_position = {x : gameboard_WIDTH/2, y : gameboard_HEIGHT/4}

// Create socket object;
var socket = io();

// Set the title
Title.innerHTML = "WAR | 0123";
// will be: Title.innerHTML = "WAR | {{ code }}"

// Create deck visual
let deck = CreateDeckVisual(gameboard_DIV, gameboard_WIDTH/2, gameboard_HEIGHT/2);

DealCards(deck)

function DealCards(deck) {
	let mypile_count = 0;
	let theirpile_count = 0;

	for (let i = 0; i <= deck.length; i++) {
		let topcard_index = deck.length - i

		setTimeout(function() {
			let card = deck[topcard_index]

			if (i%2 == 0) {
				let x_offset = mypile_count/4
				let y_offset = mypile_count/2
				MoveCard(card, mypile_position.x + x_offset, mypile_position.y + y_offset);
				mypile_count++;
			} else {
				let x_offset = theirpile_count/4
				let y_offset = theirpile_count/2
				MoveCard(card, theirpile_position.x + x_offset, theirpile_position.y + y_offset);
				theirpile_count++;
			}
			
		}, 0.05 * i * 1000)
	}
}