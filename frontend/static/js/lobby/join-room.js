// Join Room panel: room list polling, search filtering, and joining.

//
// @Author Cam Clarke
// functionality for showing rooms in the "join room" tab
const room_list = document.getElementById("room-list")

function createRoomItem(ROOM_TYPE, ROOM_ID, max_players, current_players) {

    let player_slots_html = '';
    let player_icons = [];

    for (let i = 0; i < max_players; i++) {
        if (i < current_players) {
            player_slots_html += '<span class="player-slot">\u{1F464}</span>';
        }
        else {
            player_slots_html += '<span class="player-slot empty"></span>';
        }
    }

    let template = `
    <div class="room-item" data-room-id="${ROOM_ID}">
        <div class="room-info">
        <span class="room-type">${ROOM_TYPE}</span>
        <span class="card-room-id">
             |
            <span class="room-id">${ROOM_ID}</span>
        </span>
        </div>
        <div class="room-icons">
            ${player_slots_html}
        </div>
        <button class="join-button" type="button">Join</button>
    </div>
    `

    return template
}


export async function populateRoomList() {
    const rooms = await getRoomsFromServer()
    if (Object.keys(rooms).length == 0) {
        let _html = `
        <div style="height:10pc;"></div>
        <p style="justify-self: center;">No room available to join right now - Create One!</p>
        `
        room_list.innerHTML = _html
        return
    }

    let _html = ""

    for (let key in rooms) {
        let current_players = rooms[key]["current_players"]
        let max_players = rooms[key]["max_players"]
        let _room_type = rooms[key]["type"]
        let room_type = _room_type.charAt(0).toUpperCase() + _room_type.slice(1)
        let room_item = createRoomItem(room_type, key, max_players, current_players)
        _html += room_item
    }

    room_list.innerHTML = _html
}

room_list.addEventListener("click", (event) => {
        const btn = event.target.closest(".join-button")
        if (!btn) { return }

        const roomItem = btn.closest(".room-item")
        const roomID = roomItem.dataset.roomId

        joinRoom(roomID)
})

setInterval(populateRoomList, 2000)

async function getRoomsFromServer() {
    // create some rooms for test data
    // for (let i = 0; i < 10; i++) {
    //     const postdata = new FormData();
    //     postdata.append("game_type", "war");
    //     postdata.append("num_players", "5");
    //     const response = await fetch("/create_room", {
    //         method: "POST",
    //         body: postdata,
    //     });
    // }

    const response = await fetch("/search_rooms");
    let data = await response.json();
    // let newdata = JSON.stringify(data, null, 2);
    return data
}


async function joinRoom(room_id) {
    const postdata = new FormData();
    postdata.append("room_id", room_id);
    const response = await fetch("/join_room", {
        method: "POST",
        body: postdata,
    });

    const data = await response.text()
    if (data.startsWith("success")) {
        window.location.href = "/room"
    }
}


// 
// End of @Author Cam Clarke
//

/* --- Join Room Search Logic --- */

const searchBar = document.getElementById('room-search');

function applySearchFilter() {
    let roomItems = document.querySelectorAll('.room-item');
    const searchValue = searchBar.value.toLowerCase();

    roomItems.forEach(function (room) {
        const roomText = room.querySelector('.room-id').textContent.toLowerCase(); 

        if (roomText.includes(searchValue)) {
            room.style.display = '';
        }
        else {
            room.style.display = 'none';
        }
    });
}

searchBar.addEventListener('input', applySearchFilter);

/* --- Refresh Button Active State --- */

// const refreshButton = document.getElementById('refresh-button');

// refreshButton.addEventListener('mousedown', function () {
//     refreshButton.classList.add('active');
// });

// refreshButton.addEventListener('mouseup', function () {
//     refreshButton.classList.remove('active');
// });
