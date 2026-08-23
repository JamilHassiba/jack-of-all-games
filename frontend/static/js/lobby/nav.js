// Top-level navigation: Play/Scoreboard and their sub-tabs, plus the user menu.

import { populateRoomList } from "./join-room.js";
import { populateWinsTable, populateGamesTable } from "./scoreboard.js";

/* --- Navigation Buttons Logic --- */

const joinButton = document.querySelector('button[data-view="join"]');
const createButton = document.querySelector('button[data-view="create"]');

const joinCard = document.getElementById('join-room-card');
const createCard = document.getElementById('create-room-card');

function switchToJoin() {
    createCard.style.display = 'none';
    joinCard.style.display = '';

    populateRoomList()

    joinButton.classList.add('active');
    createButton.classList.remove('active');
}

function switchToCreate() {
    joinCard.style.display = 'none';
    createCard.style.display = '';

    joinButton.classList.remove('active');
    createButton.classList.add('active');
}

joinButton.addEventListener('click', switchToJoin);
createButton.addEventListener('click', switchToCreate);

// Default to 'Join Room' when page loads
switchToJoin();


const winsButton = document.querySelector('button[data-view="wins"]');
const gamesButton = document.querySelector('button[data-view="games"]')

const winsCard = document.getElementById('wins-card');
const gamesCard = document.getElementById('games-card');

function switchToWins() {
    gamesCard.style.display = 'none';
    winsCard.style.display = '';

    populateWinsTable();

    winsButton.classList.add('active');
    gamesButton.classList.remove('active');
}

function switchToGames() {
    gamesCard.style.display = '';
    winsCard.style.display = 'none';

    populateGamesTable();

    winsButton.classList.remove('active');
    gamesButton.classList.add('active');
}

winsButton.addEventListener('click', switchToWins);
gamesButton.addEventListener('click', switchToGames);

// Default to 'Wins' when page loads
switchToWins()

const playButton = document.querySelector('button[data-view="play"]');
const scoreboardButton = document.querySelector('button[data-view="scoreboard"]');

const playCardGroupDiv = document.getElementById('play-card-group');
const scoreboardCardGroupDiv = document.getElementById('scoreboard-card-group');

const playNav = document.getElementById('play-nav');
const scoreboardNav = document.getElementById('scoreboard-nav')

function switchToPlay() {
    playCardGroupDiv.style.display = '';
    scoreboardCardGroupDiv.style.display = 'none'

    playNav.style.display = '';
    scoreboardNav.style.display = 'none';

    playButton.classList.add('active');
    scoreboardButton.classList.remove('active');
}

function switchToScoreboard() {
    scoreboardCardGroupDiv.style.display = '';
    playCardGroupDiv.style.display = 'none';

    playNav.style.display = 'none';
    scoreboardNav.style.display = '';

    playButton.classList.remove('active');
    scoreboardButton.classList.add('active');
}

playButton.addEventListener('click', switchToPlay);
scoreboardButton.addEventListener('click', switchToScoreboard);

// Default to 'Play' when page loads
switchToPlay();


/* --- User Menu Logic --- */

const userButton = document.getElementById('user-profile-button');
const userDropdown = document.getElementById('user-dropdown');
const signOutButton = document.getElementById('sign-out-button');

userButton.addEventListener('click', function (event) {
    event.stopPropagation() // To prevent the registration of multiple clicks
    if (userDropdown.style.display === 'block') {
        userDropdown.style.display = 'none';
    }
    else {
        userDropdown.style.display = 'block';
    }
});

// Hide dropdown if user clicks anywhere else
document.addEventListener('click', function () {
    userDropdown.style.display = 'none';
});

if (signOutButton) {
    signOutButton.addEventListener('click', function () {
        window.location.replace("\\logout");
    });
}

// Hide dropdown when page loads
userDropdown.style.display = 'none';

