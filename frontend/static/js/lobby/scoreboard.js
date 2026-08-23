// Scoreboard panels: wins and games leaderboards.

export async function populateWinsTable() {
    const winsTable = document.getElementById("wins-table")

    const response = await fetch("/get_wins")
    const players = await response.json()

    players.sort((a, b) => b[1] - a[1]);

    if (players.length == 0) {
        winsTable.innerHTML = `<p style="justify-self: center;">No scores yet!</p>`;
        return;
    }

    let _html = ``
    for (let i = 0; i < players.length; i++) {
        let playerName = players[i][0]
        let score = players[i][1]
        let number = i + 1

        // Number spacing is so that all numbers take same 
        // width on screen for allignment purposes
        let numberSpacing
        if (number < 10) {
            numberSpacing = "--"
        } else if (number < 100) {
            numberSpacing = "-"
        } else {
            numberSpacing = ""
        }
        let trophy = "&#127942" // trophy emoji
        let trophyClass = i < 3 ? "" : "scoreboard-trophy-hidden"
        let numberClass = i < 3 ? "scoreboard-number-top-3" : ""

        let template = `
        <div class="scoreboard-row">
            <div class="scoreboard-lhs">
                <span class="${numberClass} scoreboard-number">${number}</span>
                <span class="scoreboard-number-spacing">${numberSpacing}</span>
                <span class="${trophyClass} scoreboard-trophy">${trophy}</span>
                <span class="player-slot">\u{1F464}</span>
                <span class="scoreboard-name">${playerName}</span>
            </div>
            <div class="scoreboard-rhs">
                <span class="scoreboard-score">${score}</span>
            </div>
        </div>
        `
        _html += template
    }
    winsTable.innerHTML = _html
}

export async function populateGamesTable() {
    const gamesTable = document.getElementById("games-table")
    // Temporary until integrate with back end

    const response = await fetch("/get_games")
    const players = await response.json()

    players.sort((a, b) => b[1] - a[1]);

    let _html = ``
    for (let i = 0; i < players.length; i++) {
        let playerName = players[i][0]
        let score = players[i][1]
        let number = i + 1

        // Number spacing is so that all numbers take same 
        // width on screen for allignment purposes
        let numberSpacing
        if (number < 10) {
            numberSpacing = "--"
        } else if (number < 100) {
            numberSpacing = "-"
        } else {
            numberSpacing = ""
        }
        let trophy = "&#127942" // trophy emoji
        let trophyClass = i < 3 ? "" : "scoreboard-trophy-hidden"
        let numberClass = i < 3 ? "scoreboard-number-top-3" : ""

        // TODO - Implement profile picture. I was thinking default bitmap? - FINISHED
        let template = `
        <div class="scoreboard-row">
            <div class="scoreboard-lhs">
                <span class="${numberClass} scoreboard-number">${number}</span>
                <span class="scoreboard-number-spacing">${numberSpacing}</span>
                <span class="${trophyClass} scoreboard-trophy">${trophy}</span>
                <span class="player-slot">\u{1F464}</span>
                <span class="scoreboard-name">${playerName}</span>
            </div>
            <div class="scoreboard-rhs">
                <span class="scoreboard-score">${score}</span>
            </div>
        </div>
        `
        _html += template
    }
    gamesTable.innerHTML = _html
}

//
// End of @Author Cam Clarke
//
