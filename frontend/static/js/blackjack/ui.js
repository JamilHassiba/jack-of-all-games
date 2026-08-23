// Scores/Events tab switching and the running event log.

export function setupTabListeners() {
  const tabButtons = document.querySelectorAll(".tab-button");
  tabButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const tabName = this.getAttribute("data-tab");
      switchTab(tabName);
    });
  });
}

export function switchTab(tabName) {
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabButtons.forEach((btn) => {
    if (btn.getAttribute("data-tab") === tabName) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  tabPanes.forEach((pane) => {
    if (pane.id === tabName + "-tab") {
      pane.classList.add("active");
    } else {
      pane.classList.remove("active");
    }
  });
}

export function addEvent(message) {
  const eventsDisplay = document.getElementById("events-display");
  const eventItem = document.createElement("div");
  eventItem.className = "event-item";
  eventItem.innerHTML = message;
  eventsDisplay.appendChild(eventItem);

  eventsDisplay.scrollTop = eventsDisplay.scrollHeight;
}

export function bustEvent(username = "You") {
  addEvent(`${username} went bust!`);
}

export function winEvent(username = "You") {
  addEvent(`${username} win!`);
}

export function dealerWinEvent() {
  addEvent(`Unlucky - Dealer wins!`);
}

export function joinRoomEvent(username) {
  addEvent(`${username} joined the room!`);
}

export function blackjackEvent(username = "You") {
  addEvent(`${username} got a blackjack!`);
}

export function roundStartEvent() {
  addEvent(`New round started!`);
}
