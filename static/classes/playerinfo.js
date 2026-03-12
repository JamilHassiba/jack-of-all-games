export class PlayerInfo {
    constructor(id) {
        this.id = id
        this.name = id.substring(1,4).toLowerCase();
        this.hand = []
        this.hand_total = 0
        this.game_score = 0
        this.state = "unknown"
        this.is_bust = false
        this.has_blackjack = false
    }
}
