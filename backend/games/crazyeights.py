"""Crazy Eights game engine: player state and game orchestration."""

from cards import Deck
from states.fsm import fsm
import states.crazyeights_states as crazyeights_states
from db import record_win, record_loss


class CrazyEightsPlayer():
    def __init__(self, sid, game, username):
        self.__game = game
        self.__id = sid
        self.__username = username
        self.__game_score = 0
        self.__hand = []
        self.__draws_this_turn = 0
        self.__state = "none"
        '''
            Player states:
                - none -> default state, no state assigned
                - lobby -> inside the game room, waiting for the first round to start
                - waiting -> the round is active, but it is another player's turn (buttons locked)
                - playing -> it is actively this player's turn (can draw or play a card)
                - finished -> entered when the player drops their last card and wins the round
        '''

    # Getters
    @property
    def username(self): 
        return self.__username
    @property
    def state(self): 
        return self.__state
    @property
    def id(self): 
        return self.__id
    @property
    def game_score(self): 
        return self.__game_score
    @property
    def hand(self): 
        return self.__hand
    @property
    def draws_this_turn(self): 
        return self.__draws_this_turn

    # Setters & Actions
    @id.setter
    def id(self, new_id):
        self.__id = new_id

    @game_score.setter
    def game_score(self, new_score):
        self.__game_score = new_score

    def SetState(self, new_state: str):
        self.__state = new_state
        self.__game.socketio.emit(
            'crazyeights_relay_player_info', 
            {"id": self.id, 
             "username": self.username,
             "state": new_state}, 
            to=self.__game.room.id)

    def AddGameScore(self, value):
        self.__game_score += value
        self.__game.socketio.emit(
            'crazyeights_relay_player_info', 
            {"id": self.id, 
             "username": self.username,
             "game_score": self.__game_score}, 
            to=self.__game.room.id)

    def AddCardToHand(self, card_data):
        self.__hand.append(card_data["code"])
        self.__game.socketio.emit(
            'crazyeights_relay_player_info',
            {"id": self.id, "hand": self.hand},
            to=self.__game.room.id)

    def RemoveCardFromHand(self, card_code):
        if card_code in self.__hand:
            self.__hand.remove(card_code)
            self.__game.socketio.emit(
                'crazyeights_relay_player_info',
                {"id": self.id, "hand": self.hand},
                to=self.__game.room.id)
            
    def increment_draws(self):
        self.__draws_this_turn += 1
        
    def reset_draws(self):
        self.__draws_this_turn = 0
            
    def ClearHand(self):
        self.__hand = []
        self.__game.socketio.emit(
            'crazyeights_relay_player_info',
            {"id": self.id, "username": self.username, "hand": self.hand},
            to=self.__game.room.id)


class CrazyEights():
    def __init__(self, socketio, max_player_count, room_reference):
        self.__socketio = socketio
        self.__max_player_count = max_player_count
        self.__room = room_reference
        self.__players = []
        
        self.deck = Deck(id=None, shuffle=True, decks=1, jokers=False)
        self.discard_pile = []
        
        self.current_suit = None
        self.current_value = None
        self.active_player_index = 0
        self.pending_suit_choice = False # Becomes True when an 8 is played
       
        self.__FSM = fsm(self)
        self.__FSM.SetStates({
            "intermission" : crazyeights_states.intermission(self.__FSM),
            "round_start" : crazyeights_states.round_start(self.__FSM),
            "turn_start" : crazyeights_states.turn_start(self.__FSM),
            "auto_draw" : crazyeights_states.auto_draw(self.__FSM),
            "wait_for_action" : crazyeights_states.wait_for_action(self.__FSM),
            "score" : crazyeights_states.score(self.__FSM),
            "evaluate_game" : crazyeights_states.evaluate_game(self.__FSM),
            "game_end": crazyeights_states.game_end(self.__FSM)
        })
        self.__FSM.Begin("intermission")

    # Methods
    def Update(self, dt):
        self.__FSM.Update(dt)
    
    def AddPlayer(self, sid, username):
        for player in self.__players: 
            if player.username == username:
                player.id = sid  # Reconnect the player
                return player
                
        player = CrazyEightsPlayer(sid, self, username)
        self.__players.append(player)
        return player
    
    def RemovePlayer(self, player_obj):
        leaving_index = self.__players.index(player_obj)
        self.__players.remove(player_obj)

        if len(self.__players) == 0:
            return

        if leaving_index < self.active_player_index:
            self.active_player_index -= 1

        self.active_player_index = (self.active_player_index) % len(self.__players)

    def GetPlayerFromSID(self, sid):
        for player in self.__players:
            if player.id == sid: 
                return player
        return None
    
    def NextTurn(self):
        # Increments player index
        self.active_player_index = (self.active_player_index + 1) % len(self.__players)
    
    def draw_card_from_deck(self):
        cards = self.deck.draw(1)
        
        # Reshuffle the discard pile if deck is empty
        if not cards:
            top_card = self.discard_pile.pop()
            codes_to_return = ",".join([card["code"] for card in self.discard_pile])
            self.deck.return_cards(codes_to_return) 
            self.deck.reshuffle(remaining_only=True)
            self.discard_pile = [top_card]
            cards = self.deck.draw(1)
                
        return cards[0]

    def is_valid_play(self, card_code):
        value = card_code[0]
        suit = card_code[1]

        if value == '8': 
            return True
            
        if suit == self.current_suit or value == self.current_value:
            return True
            
        return False

    @staticmethod
    def get_card_score(card_code: str) -> int:
        value = card_code[0] 
        if value == '8': 
            return 50
        if value in ['K', 'Q', 'J', '0']: 
            return 10
        if value == 'A': 
            return 1
        return int(value)

    def EvaluateGame(self):
        for player in self.__players:
            if player.game_score >= 100:
                return True
        return False
        
    def FindWinner(self):
        lowest_score = 1000
        winner = None
        for player in self.__players:
            if player.game_score < lowest_score:
                lowest_score = player.game_score
                winner = player
        record_win(winner.username)
        for player in self.__players:
            if player.username != winner.username:
                record_loss(player.username)
        return winner
    
    def PlayCardRequest(self, sid, card_code):

        if self.__FSM.current_state_name != "wait_for_action": 
            return
        if self.pending_suit_choice: 
            return # Block playing cards if we are waiting for an 8's suit
        
        player = self.GetPlayerFromSID(sid)

        if not player or player.id != self.active_player.id: 
            return
        
        if card_code in player.hand and self.is_valid_play(card_code):
            
            player.RemoveCardFromHand(card_code)
            self.discard_pile.append({"code": card_code})
            self.current_value = card_code[0]

            if self.current_value == '8':
                self.current_suit = "?" 
                self.pending_suit_choice = True

                self.socketio.emit("crazyeights_message", {"msg": f"{player.username} played the crazy eight!"}, to=self.room.id)
            else:
                self.current_suit = card_code[1]
                self.socketio.emit("crazyeights_message", {"msg": f"{player.username} played a card"}, to=self.room.id)

            self.socketio.emit("crazyeights_relay_board_info", {
                "top_card": self.discard_pile[-1]["code"],
                "current_suit": self.current_suit,
                "current_value": self.current_value
            }, to=self.room.id)

            self.socketio.emit("crazyeights_relay_player_info", {
                "id": player.id,
                "username": player.username,
                "hand": player.hand
            }, to=self.room.id)
            
            if self.current_value == '8':
                self.pending_suit_choice = True
                self.socketio.emit("crazyeights_prompt_suit_choice", {"id": player.id}, to=self.room.id)
                
            elif len(player.hand) == 0:
                self.__FSM.SetState("score")
                
            else:
                self.NextTurn()
                self.__FSM.SetState("turn_start")

    def ChooseSuitRequest(self, sid, new_suit):
        if self.__FSM.current_state_name != "wait_for_action": 
            return
        if not self.pending_suit_choice: 
            return
        
        player = self.GetPlayerFromSID(sid)
        
        if not player or player.id != self.active_player.id: 
            return
        
        self.current_suit = new_suit
        self.pending_suit_choice = False

        self.socketio.emit("crazyeights_relay_board_info", {
                "top_card": self.discard_pile[-1]["code"],
                "current_suit": self.current_suit,
                "current_value": self.current_value
            }, to=self.room.id)
        
        self.socketio.emit("crazyeights_message", {"msg": f"{player.username} changed the suit!"}, to=self.room.id)

        if len(player.hand) == 0:
            self.__FSM.SetState("score")

        else:
            self.NextTurn()
            self.__FSM.SetState("turn_start")
    
    # Getters
    @property
    def room(self): 
        return self.__room
    @property
    def socketio(self): 
        return self.__socketio
    @property
    def FSM(self): 
        return self.__FSM
    @property
    def players(self): 
        return self.__players
    @property
    def max_player_count(self): 
        return self.__max_player_count
    @property
    def active_player(self):
        if not self.__players: 
            return None
        return self.__players[self.active_player_index]

