export class PlayerInfo {
    constructor(id) {
        this.id = id
        this.hand = []
        this.hand_total = 0
        this.game_score = []
        this.state = "unknown"
        this.is_bust = false
        this.has_blackjack = false
    }
}
