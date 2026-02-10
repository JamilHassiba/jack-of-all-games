import {CreateCard, CreateDeckVisual} from '../card.js';
import { io } from "https://cdn.socket.io/4.6.1/socket.io.esm.min.js";

console.log("war.js running...");

// Get references to html elements
const Title = document.getElementById("Title");

const myHand_DIV = document.getElementById("DIV_myHand");
const opponentHand_DIV = document.getElementById("DIV_opponentHand");

const gameboard_DIV = document.getElementById("DIV_gameBoard");
const gameboard_WIDTH = gameboard_DIV.offsetWidth;
const gameboard_HEIGHT = gameboard_DIV.offsetHeight; 

// Create socket object;
var socket = io();

// Set the title
Title.innerHTML = "WAR | 0123";
// will be: Title.innerHTML = "WAR | {{ code }}"

// Create deck visual
CreateDeckVisual(gameboard_DIV, gameboard_WIDTH/2, gameboard_HEIGHT/2);