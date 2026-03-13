export class PlayerLabel {
    constructor(id) {
        this.id = id
        this.e = document.createElement("li")
    }

    update(playerinfo) {
        this.e.innerHTML = `<b>${playerinfo.name}</b> 
                            | Game Score: ${playerinfo.game_score}
                            | Hand: ${playerinfo.hand}
                            | Total: ${playerinfo.hand_total}`
    }
}