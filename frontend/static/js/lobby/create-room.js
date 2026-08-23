// Create Room panel: game selection, player-count slider, password toggle, submit.

import { SendData } from "./api.js";

/* --- Slider Logic --- */

const slider = document.getElementById('player-slider');
const countDisplay = document.getElementById('player-count-display');

function sliderEventFunct() {
    // Update displayed player count
    const playerCount = slider.value;
    countDisplay.textContent = playerCount;
}

slider.addEventListener('input', sliderEventFunct);
sliderEventFunct()

const gameLimits = {
    'poker': { min: 2, max: 4 },
    'war': { min: 2, max: 2 },
    'blackjack': { min: 2, max: 5 },
    'crazyeights': { min: 2, max: 4 }
};

const gameRadios = document.querySelectorAll('input[name="game_choice"]');
const playerSlider = document.getElementById('player-slider');
const playerDisplay = document.getElementById('player-count-display');

function updateSliderLimits(selectedGame) {
    const limits = gameLimits[selectedGame];

    if (selectedGame === 'war') {
        playerSlider.style.display = 'none';
    } else {
        playerSlider.style.display = '';
    }

    playerSlider.min = limits.min;
    playerSlider.max = limits.max;

    updateDisplay();
}

function updateDisplay() {
    playerDisplay.innerText = playerSlider.value;
}

gameRadios.forEach(radio => {
    radio.addEventListener('change', (e) => {
        if (e.target.checked) {
            updateSliderLimits(e.target.value);
        }
    });
});

playerSlider.addEventListener('input', updateDisplay);

const defaultGame = document.querySelector('input[name="game_choice"]:checked').value;
updateSliderLimits(defaultGame);


/* --- Password Lock Logic --- */

const lockToggle = document.getElementById('lock-toggle');
const passwordBox = document.getElementById('password-input');
passwordBox.style.display = 'none';

lockToggle.addEventListener('change', function () {
    if (lockToggle.checked) {
        passwordBox.style.display = 'block';
        passwordBox.focus()
    }
    else {
        passwordBox.style.display = 'none';
    }
});

//
// @Author Thomas McPhee
//

async function createRoom() {
    // Selected game (radio)
    const gameChoice = document.querySelector('input[name="game_choice"]:checked').value;

    // Player count (range slider)
    const playerCount = document.getElementById('player-slider').value;

    // Lock checkbox
    const isLocked = document.getElementById('lock-toggle').checked;

    // Password (only relevant if locked)
    const password = document.getElementById('password-input').value;

    const formData = {
        game_type: gameChoice,
        num_players: Number(playerCount),
        // isLocked,
        // password: isLocked ? password : null
    };

    let response = await SendData("/create_room", formData)

    console.log(formData);

    if (response) {
        response = await SendData("/join_room", {
            "room_id": response
        })

        console.log(response)
        if (response.startsWith("success")) {
            window.location.href = "/room"
        }
    }
}

//
// End of @author Thomas McPhee
//

document
    .getElementById("create-room-button")
    .addEventListener("click", createRoom);
