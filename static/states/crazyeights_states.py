'''
            Crazy Eights States:
                - intermission -> Waiting for room to get full
                - round_start -> Shuffles deck, deals 5 cards to everyone, and flips the first discard card
                - turn_start -> Determines whose turn it is next and evaluates if they have any valid cards to play
                - wait_for_action -> If player has a valid card, the game waits for them to play a card
                - auto_draw -> Else, the game draws cards for the player until they have a valid card or 3 cards are drawn
                - score -> Adds points to each player when the round is over
                - evaluate_game -> Checks if any player hit 100 points, if so, find winner and end game
                - game_end -> Resets the scores and waits few seconds for the popup
        '''

from static.states.state import State

class intermission(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("Intermission entered: Waiting for players...")
        self.elapsed = 0
        for player in self.fsm.root.players:
            player.SetState('lobby')

    def Update(self, dt):
        game = self.fsm.root
        
        if len(game.players) == game.max_player_count:
            self.elapsed += dt
            # Once full, wait 2 seconds before starting so the last player can load in
            if self.elapsed >= 2:
                self.fsm.SetState("round_start")
        else:
            # Keep the timer at 0 until the room is completely full
            self.elapsed = 0
    
    def OnExit(self):
        print("IntermissionState exited")

class round_start(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("Round Start: Dealing cards...")
        game = self.fsm.root
        game.deck.reshuffle(remaining_only=False)
        
        for player in game.players:
            player.ClearHand()
            cards = game.deck.draw(5)
            for card in cards:
                player.AddCardToHand(card)
        
        for player in game.players:
            game.socketio.emit("crazyeights_relay_player_info", {
                "id": player.id,
                "username": player.username,
                "hand": player.hand
            }, to=game.room.id)
                
        first_card = game.deck.draw()[0]
        game.discard_pile = [first_card]
        game.current_value = first_card["code"][0]
        game.current_suit = first_card["code"][1]

        game.socketio.emit("crazyeights_relay_board_info", {
            "top_card": game.discard_pile[-1]["code"],
            "current_suit": game.current_suit,
            "current_value": game.current_value
        }, to=game.room.id)
            
        self.elapsed = 0

    def Update(self, dt):
        self.elapsed += dt
        if self.elapsed >= 2:
            self.fsm.SetState("turn_start")

    def OnExit(self):
        print("RoundStartState exited")

class turn_start(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        game = self.fsm.root
        active_player = game.active_player
        print(f"Turn Start: Player {active_player.username}")
        
        for player in game.players:
            if player.id == active_player.id:
                player.SetState("playing")
                player.reset_draws()
            else:
                player.SetState("waiting")
                
    def Update(self, dt):
        game = self.fsm.root
        active_player = game.active_player
        
        has_valid_card = False
        for card_code in active_player.hand:
            if game.is_valid_play(card_code):
                has_valid_card = True
                break
                
        if has_valid_card:
            self.fsm.SetState("wait_for_action")
        else:
            self.fsm.SetState("auto_draw")

    def OnExit(self):
        print("PlayersTurnState exited")

class wait_for_action(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("Waiting for player to click a card...")

    def Update(self, dt):
        pass

    def OnExit(self):
        print("WaitForActionState exited")

class auto_draw(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("Auto Draw: Player has no valid cards.")
        self.elapsed = 1.0 # Set to 1.0 to force an immediate first draw

    def Update(self, dt):
        self.elapsed += dt
        
        # Every 1 second, draw a card
        if self.elapsed >= 1.0: 
            self.elapsed = 0
            
            game = self.fsm.root
            active_player = game.active_player
            
            new_card = game.draw_card_from_deck()
                
            active_player.AddCardToHand(new_card)
            active_player.increment_draws()
            
            if game.is_valid_play(new_card["code"]):
                self.fsm.SetState("wait_for_action")
            elif active_player.draws_this_turn >= 3:
                game.NextTurn()
                self.fsm.SetState("turn_start")
    
    def OnExit(self):
        print("AutoDrawState exited")

class score(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("Round over! Scoring remaining hands...")
        game = self.fsm.root
        self.elapsed = 0
        
        for player in game.players:
            points = 0
            for card_code in player.hand:
                points += game.get_card_score(card_code)
            
            if points > 0:
                player.AddGameScore(points)
        
        game.socketio.emit("crazyeights_message", {"msg": "Round Over!"}, to=game.room.id)

    def Update(self, dt):
        self.elapsed += dt
        if self.elapsed >= 1:
            self.fsm.SetState("evaluate_game")

    def OnExit(self):
        print("ScoreState exited")

class evaluate_game(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("Evaluating if anyone hit 100 points...")
        self.elapsed = 0

    def Update(self, dt):
        self.elapsed += dt
        if self.elapsed >= 1:
            game = self.fsm.root
            
            if game.EvaluateGame():
                winner = game.FindWinner()
                print(f"{winner.username} wins!")
                
                scores = [{"username": player.username, "score": player.game_score} for player in game.players]

                game.socketio.emit("crazyeights_game_over", {
                    "winner": winner.username,
                    "scores": scores
                }, to=game.room.id)
                
                self.fsm.SetState("game_end")

            else:
                self.fsm.SetState("round_start")
    
    def OnExit(self):
        print("EvalutateGameStateO exited")

class game_end(State):
    def __init__(self, fsm):
        super().__init__(fsm)

    def OnEnter(self):
        print("Game Over!")
        self.elapsed = 0

    def Update(self, dt):
        self.elapsed += dt
        
        if self.elapsed >= 8: 
            game = self.fsm.root
            
            for player in game.players:
                player.game_score = 0
                
                game.socketio.emit('crazyeights_relay_player_info', {
                    "id": player.id,
                    "username": player.username,
                    "game_score": 0
                }, to=game.room.id)
            
            game.socketio.emit("crazyeights_message", {"msg": f"Starting a new game..."}, to=game.room.id)

            self.fsm.SetState("round_start")
    
    def OnExit(self):
        print("GameEndState exited")