from api import Deck, Pile
from time import sleep

# Thomas McPhee
from static.states.fsm import fsm
import static.states.blackjack_states as blackjack_states

import static.states.crazyeights_states as crazyeights_states

import random
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

class Game: 
    def __init__(self, num_decks, num_players, shuffle=True, jokers=False): 
        # documentation 
        # int num_decks = number of decks used for the game 
        # bool shuffle = whether the decks generated should be shuffled 
        # bool jokers = whether the decks generated should have jokers 
        # array of int num_players = an array of length num_decks representing the number of different players per deck.  
        deck = Deck(decks=num_decks, shuffle=shuffle, jokers=jokers)
        self.deck = deck
        self.players = [Player(self) for i in range(num_players)]
        self.lock = False 
        self.last_player = None 
        self.last_action = "" 
        self.player_index = -1
        self.active_player = None 
        self.max_draws = 1                             # modify this to change behaviour of games 
        self.max_discards = 1 
        self.discard_pile = self.deck.make_pile()


    def update(self):
        # use polymorphism to define new update function
        # this should be called when you want to go to the next state
        if not self.lock: 
            self.player_index += 1 
            if self.player_index >= len(self.players): 
                self.player_index = 0 
                self.game_turn()
            self.active_player = self.players[self.player_index]
            self.active_player.lock = False 
            self.active_player.draw_lock = False 
            self.active_player.discard_lock = False 
            self.lock = True 
            print("testing global locks")
            print(f"unlocked player{self.player_index}")
            return f"successfully updated game - unlocked player {self.player_index}"
        else: 
            return f"the game is locked - cannot update until player {self.player_index} has finished their turn"
    
    def game_turn(self): 
        # use polymorphism to define new game_turn
        # this action is applied once every player has acted once in a round
        pass

    def game_finish(self): 
        # use polymorphism to define new game_finish
        # this action is applied when the game finishes 
        print("game finished")
    

class War(Game): 
    def __init__(self, num_decks, num_players, shuffle=True, jokers=False): 
        super().__init__(num_decks, num_players, shuffle, jokers)
        self.max_draws = 1 
        self.max_discards = 1 

    def game_turn(self): 
        values = {f'{i}':i for i in range(11)}
        values["J"] = 11 
        values["Q"] = 12
        values["K"] = 13 
        values["A"] = 14   
        suitValues = {"C": 1, "D": 2, "H": 3, "S": 4}
        max_value = -10000 
        winning_player = None 
        winning_player_indx = 0 
        winning_card = None 
        for player_index in range(len(self.players)): 
            player = self.players[player_index]
            card = player.discarded[-1]["code"]
            value = values[card[0]] 
            if value > max_value: 
                max_value = value 
                winning_player = player 
                winning_player_indx = player_index
                winning_card = card 
            elif value == max_value: 
                print("triggered tiebreak")
                if value + suitValues[card[1]] > values[winning_card[0]] + suitValues[winning_card[1]]: 
                    max_value = value 
                    winning_player = player 
                    winning_player_indx = player_index
                    winning_card = card 
        winning_player.score += 1 
        print(f"player{winning_player_indx} won a round. Currrent score: {winning_player.score}")
    
    def game_finish(self): 
        max_score = max([i.score for i in self.players])
        winners = []
        winners_index = [] 
        for i in range(len(self.players)): 
            print(f"Player{i}, Score: {self.players[i].score}")
            if self.players[i].score == max_score: 
                winners.append(self.players[i])
                winners_index.append(i)
        print(winners_index)
        return winners 

class Player: 
    def __init__(self, game: Game): 
        self.game = game
        self.pile = Pile(game.deck)
        self.lock = True
        self.score = 0
        self.discarded = []             # for logging only. not an actual pile
        self.draw_count = 0  
        self.discard_count = 0 
        self.draw_lock = False 
        self.discard_lock = False 
    
    def draw(self, count=1):
        if not self.lock and not self.draw_lock:
            if self.draw_count < self.game.max_draws: 
                val = self.pile.draw(count)
                if val == None: 
                    self.check_end_turn()
                    return "End of Deck"
                else: 
                    self.draw_count += 1 
                    if self.draw_count >= self.game.max_draws: 
                        self.draw_count = 0 
                        self.draw_lock = True 
                    self.check_end_turn()
                    return "successfully drawn card", val
            else: 
                self.draw_count = 0 
                self.draw_lock = True 
                self.check_end_turn()
                return "exceeded maximum draw count - draw is locked"
        else: 
            self.check_end_turn()
            return "either the user is locked or draw count exceeded"
            

    def discard(self, code, random=False): 
        if not self.lock and not self.discard_lock: 
            if self.discard_count < self.game.max_discards:       # if u can discard, discard 
                if random:
                    card = self.pile.pop_random()                      # add the count 
                else:
                    card = self.pile.pop_specific(code)           
                if card != None: 
                    self.discard_count += 1 
                    self.game.discard_pile.add(card)
                    self.discarded.append(card)
                if self.discard_count >= self.game.max_discards: 
                    self.discard_count = 0 
                    self.discard_lock = True 
                self.check_end_turn()
                return card
            else: 
                self.discard_count = 0 
                self.discard_lock = True 
                self.check_end_turn()
                return []
        self.check_end_turn()
        return []
    
    def check_end_turn(self): 
        if self.discard_lock and self.draw_lock and not self.lock: 
            self.lock = True 
            self.discard_lock = False 
            self.draw_lock = False 
            self.discard_count = 0 
            self.draw_count = 0 
            self.game.lock = False 
            self.game.update()
    
    def show(self):
        return self.pile.show() 

class Room: 
    def __init__(self, socketio, game_type, num_players, id=None): 
        self.game_type = game_type 
        self.player_count = 0 
        self.num_players = num_players
        if id == None: 
            length = random.randint(4, 6)
            self.id = "".join([chars[random.randint(0, len(chars)-1)] for i in range(length)])
        else: 
            self.id = id

        if game_type == "war": 
            self.game = War(1, num_players)
        elif game_type == "poker": 
            pass 
            # this is an example of how we would extend
        elif game_type == "blackjack":
            self.game = Blackjack(socketio, num_players, self)
        elif game_type == "crazyeights":
            self.game = CrazyEights(socketio, num_players, self)
        else:
            pass  

### ADDED BY Thomas McPhee ###

##### BLACKJACK #####

class BlackjackPlayer():
    def __init__(self, sid, game, username):
        self.__game = game
        self.__id = sid
        self.__username = username
        self.__game_score = 0
        self.__hand = []
        self.__hand_total = 0
        self.__deck = Deck(id=None, shuffle=True, decks=1, jokers=False) 
        self.__state = "none"
        '''
            Player states:
                - none -> default state, no state assigned
                - lobby -> inside the blackjack game, but isn't participating in the current round, or is waiting for a round to start
                - playing -> actively pressing hit/stick
                - finished -> entered when: hit blackjack | stuck | bust | timeout
        '''

    def HitMe(self):
        cards_list = self.__deck.draw()

        # If deck is empty, reshuffle instead of creating a new deck
        if not cards_list:
            self.__deck.reshuffle(remaining_only=False)  # shuffle all cards back in
            cards_list = self.__deck.draw()

        card_data = cards_list[0]
        self.AddCardToHand(card_data)
        print(self)

    def Stand(self):
        self.SetState("finished")

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
    @id.setter
    def id(self, new_id):
        self.__id = new_id
    @property
    def game_score(self):
        return self.__game_score
    @property
    def hand(self):
        return self.__hand
    def set_hand(self, hand): 
        self.__hand = hand
    @property
    def hand_total(self):
        return self.__hand_total
    def set_hand_total(self, val): 
        self.__hand_total = val
    @property
    def deck(self):
        return self.__deck
    
    # Setters
    def SetState(self, new_state: str):
        self.__state = new_state

        # Broadcast this change to the room's clients
        self.__game.socketio.emit(
            'relay_player_info', 
            {"id": self.id, "state": new_state}, 
            to=self.__game.room.id)

    def AddGameScore(self, value):
        old_score = self.__game_score
        self.__game_score += value
        new_score = self.__game_score

        # Broadcast this change to the room's clients
        self.__game.socketio.emit(
            'relay_player_info', 
            {"id": self.id, "game_score": value}, 
            to=self.__game.room.id)

        # Broadcast player score event
        self.__game.socketio.emit(
            'player_score_event',
            {"id": self.id, "old_score": old_score, "delta_score": new_score-old_score, "new_score": new_score},
            to=self.__game.room.id)

    def AddCardToHand(self, card_data): # assumes the formatting returned by deckofcardsapi
        self.__hand_total += Blackjack.convert_card_value_to_int(card_data["value"])
        self.__hand.append(card_data["code"])

        BlackjackRound.IsEntityBust(self)
        fake_hand = [i if i[0]!="1" else "A"+i[1] for i in self.__hand]

        self.__game.socketio.emit(
            'relay_player_info',
            {"id": self.id, "hand": fake_hand, "hand_total": self.hand_total},
            to=self.__game.room.id)
        
    def ClearHand(self):
        self.__hand_total = 0
        self.__hand = []

        self.__game.socketio.emit(
            'relay_player_info',
            {"id": self.id, "hand": self.hand, "hand_total": self.hand_total},
            to=self.__game.room.id)

    def __str__(self):
        return f"Player Object | Hand: {self.__hand} | Total: {self.__hand_total}"

class BlackjackDealer():
    def __init__(self, game):
        self.__game = game
        self.__hand = []
        self.__hand_total = 0
        self.__deck = Deck(id=None, shuffle=True, decks=1, jokers=False) 

    def DealToSelf(self):
        cards_list = self.__deck.draw()

        if not cards_list:
            self.__deck.reshuffle(remaining_only=False)
            cards_list = self.__deck.draw()

        card_data = cards_list[0]
        self.AddCardToHand(card_data)
        print(self)

    # Getters
    @property
    def hand(self):
        return self.__hand
    def set_hand(self, hand): 
        self.__hand = hand 
    @property
    def hand_total(self):
        return self.__hand_total
    def set_hand_total(self, val): 
        self.__hand_total = val 
    @property
    def deck(self):
        return self.__deck
    
    def ShouldIDraw(self):
        return self.hand_total <= 16
    
    # Setters
    def AddCardToHand(self, card_data): # assumes the formatting returned by deckofcardsapi
        self.__hand_total += Blackjack.convert_card_value_to_int(card_data["value"])
        self.__hand.append(card_data["code"])

        BlackjackRound.IsEntityBust(self)
        fake_hand = [i if i[0]!="1" else "A"+i[1] for i in self.__hand]

        self.__game.socketio.emit(
            'relay_player_info',
            {"id": "dealer", "hand": fake_hand, "hand_total": self.hand_total},
            to=self.__game.room.id)
    
    def ClearHand(self):
        self.__hand_total = 0
        self.__hand = []

        self.__game.socketio.emit(
            'relay_player_info',
            {"id": "dealer", "hand": self.hand, "hand_total": self.hand_total},
            to=self.__game.room.id)
        
    def __str__(self):
        return f"Dealer Object | Hand: {self.__hand} | Total: {self.__hand_total}"

# Doesn't inherit from Game
class Blackjack():
    # STATIC
    @staticmethod
    def convert_card_value_to_int(card_value: str) -> int:
        match card_value:
            case "KING" | "QUEEN" | "JACK":
                card_value = "10"
            case "ACE":
                card_value = "11"

        return int(card_value)

    # CONSTRUCTOR
    def __init__(self, socketio, max_player_count, room_reference):
        self.__socketio = socketio
        self.__max_player_count = max_player_count
        self.__players = []
        self.__room = room_reference # parent object
        self.__dealer = BlackjackDealer(self)
        self.__current_round = None
       
        self.__FSM = fsm(self)
        self.__FSM.SetStates({
            "intermission" : blackjack_states.intermission(self.__FSM),
            "round_start" : blackjack_states.round_start(self.__FSM),
            "players_turn" : blackjack_states.players_turn(self.__FSM),
            "dealer_turn" : blackjack_states.dealer_turn(self.__FSM),
            "score" : blackjack_states.score(self.__FSM),
            "cleanup" : blackjack_states.cleanup(self.__FSM),
            "evaluate_game" : blackjack_states.evaluate_game(self.__FSM)
        })
        self.__FSM.Begin("intermission")

    # Methods
    def Update(self, dt):
        self.__FSM.Update(dt)

    def AddPlayer(self, sid, username):
        # Create a player object
        if len(self.__players) < self.__max_player_count:
            player = BlackjackPlayer(sid, self, username)
            for i in self.__players: 
                if i.username == username: 
                    i.id = sid 
                    return i 
            self.__players.append(player)
            return player 
        else: 
            return None 
    
    def RemovePlayer(self, player_obj):
        self.__players = [i for i in self.__players if i != player_obj] 
        self.__current_round.RemovePlayer(player_obj)

    # Game Routes
    def EvaluateGame(self):
        print("evaluating the game...")

    # Round Routes
    def NewRound(self):
        self.__current_round = BlackjackRound(self, self.players)
    def CleanupRound(self):
        for player in self.players: player.ClearHand()
        self.dealer.ClearHand()
        self.__current_round = None
    def EvaluateRound(self):
        if self.__current_round == None: return
        self.__current_round.EvaluateRound()
    def PlayerHitRequest(self, sid):
        if self.__current_round == None: return
        self.__current_round.PlayerHitRequest(sid)
    def PlayerStandRequest(self, sid):
        if self.__current_round == None: return
        self.__current_round.PlayerStandRequest(sid)

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
    def current_state(self):
        return self.__current_state
    @property
    def current_round(self):
        return self.__current_round
    
    @property
    def dealer(self):
        return self.__dealer
    @property
    def players(self):
        return self.__players
    @property
    def max_player_count(self):
        return self.__max_player_count

    
    ## Dunders
    def __str__(self):
        output = "\n==========\n"
        output += "BLACKJACK OBJECT\n"
        output += f"CurrentState: {self.__current_state}\n"
        output += f"RoomID: {self.__room.id}\n"
        output += "Players:\n"
        for player in self.players:
            output += f"     {player}\n"
        output += "\n==========\n"
        return output

class BlackjackRound():
    # entity in this context is either dealer or player (both implement a hand_total field)
    @staticmethod
    def IsEntityBust(entity):
        if entity.hand_total > 21: 
            temp_hand = entity.hand.copy()

            # scan for aces when bust 
            for card_index in range(len(temp_hand)): 
                card = temp_hand[card_index]
                if card[0] == "A": 
                    print("ACE DETECTED")
                    # treat it as a 1 instead 
                    entity.set_hand_total(entity.hand_total - 10)
                    if entity.hand_total <= 21: 
                        temp_hand[card_index] = "1" + card[1] 
                        entity.set_hand(temp_hand)
                        return False 
                        # don't scan for more aces if they are no longer bust
            return entity.hand_total > 21
        else: 
            return False 

    @staticmethod
    def DoesEntityHaveBlackjack(entity):
        return entity.hand_total == 21

    @staticmethod
    def WinPlayers(winners):
        from backend import record_win
        for player in winners:
            print(f"WinPlayers called for {player.username}")
            if BlackjackRound.DoesEntityHaveBlackjack(player): player.AddGameScore(2)
            else: player.AddGameScore(1)
            if player.username:
                record_win(player.username)

    @staticmethod
    def LosePlayers(losers):
        from backend import record_loss
        for player in losers:
            player.AddGameScore(0)
            if player.username:
                record_loss(player.username)
        pass

    def __init__(self, game, players):
        self.__game = game #reference to the parent game
        self.__players_in_round = players.copy()
        self.__players_finished = []

        self.DealInitialCards()

    def GetPlayerFromSID(self, sid):
        for player in self.__players_in_round:
            if player.id == sid: return player
        return None

    def DealInitialCards(self):
        self.__game.dealer.DealToSelf()
        for player in self.__players_in_round:
            player.SetState('playing')
            player.HitMe()
            player.HitMe()
            # 2 ACE TEST
            # fake_ace = {"value": "ACE", "code": "AS", "suit": "SPADES", "image": ""}
            # player.AddCardToHand(fake_ace)
            # player.AddCardToHand(fake_ace)

    def EvaluatePlayer(self, player):
        is_bust = BlackjackRound.IsEntityBust(player)
        has_blackjack = BlackjackRound.DoesEntityHaveBlackjack(player)

        if is_bust or has_blackjack:
            player.SetState("finished")
            self.__players_finished.append(player)

            if is_bust: 
                self.__game.socketio.emit(
                    "relay_player_info",
                    {"id": player.id, "is_bust": True},
                    to=self.__game.room.id)
                
            else:
                self.__game.socketio.emit(
                    "relay_player_info",
                    {"id": player.id, "has_blackjack": True},
                    to=self.__game.room.id)
                

    def EvaluateRound(self):
        match self.EvaluateDealer():
            case "bust": 
                winners = filter(lambda p: not BlackjackRound.IsEntityBust(p), self.__players_in_round)
                BlackjackRound.WinPlayers(winners)

            case "blackjack": 
                BlackjackRound.LosePlayers(self.__players_in_round.copy())

            case _:
                score_to_beat = self.__game.dealer.hand_total
                winners = filter(lambda p: p.hand_total > score_to_beat and not BlackjackRound.IsEntityBust(p), self.__players_in_round)
                losers = filter(lambda p: p.hand_total <= score_to_beat or BlackjackRound.IsEntityBust(p), self.__players_in_round)

                BlackjackRound.WinPlayers(winners)
                BlackjackRound.LosePlayers(losers)

    def EvaluateDealer(self):
        dealer = self.__game.dealer
        is_bust = BlackjackRound.IsEntityBust(dealer)
        has_blackjack = BlackjackRound.DoesEntityHaveBlackjack(dealer)

        if is_bust:
            self.__game.socketio.emit(
                "relay_player_info",
                {"id": "dealer", "is_bust": True},
                to=self.__game.room.id)
            
            return "bust"
        elif has_blackjack:
            self.__game.socketio.emit(
                "relay_player_info",
                {"id": "dealer", "has_blackjack": True},
                to=self.__game.room.id)
            
            return "blackjack"
        
        return ""

    def PlayerHitRequest(self, sid):
        if self.__game.FSM.current_state_name != "players_turn": return

        player = self.GetPlayerFromSID(sid)
        if not player: 
            print("Cannot find player")
            return 
        if player.state != "playing": return

        player.HitMe()
        self.EvaluatePlayer(player)

    def PlayerStandRequest(self, sid):
        if self.__game.FSM.current_state_name != "players_turn": return

        player = self.GetPlayerFromSID(sid)
        if not player: return
        if player.state != "playing": return

        player.Stand()
        self.UpdatePlayersFinished()


    def RemovePlayer(self, player_obj):
        self.__players_in_round.remove(player_obj)

    def AreAllPlayersFinished(self):
        self.UpdatePlayersFinished()
        return len(self.__players_in_round) == len(self.__players_finished)
    
    def UpdatePlayersFinished(self): 
        self.__players_finished = [i for i in self.__game.players if i.state == "finished"]
    

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
            {"id": self.id, "hand": self.hand},
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
        self.__players = [i for i in self.__players if i != player_obj] 

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
        from backend import record_win
        from backend import record_loss
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


### END ###

        
#region 
# for each game the update needs to include additional code to enforce the rules. 
# basic workflow currently: 
# - unlock the game 
# - game unlocks a player 
# - game locks itself to wait for a turn-terminating action (if you want a custom one, write a new function)
# - the player performs some action until their turn terminates 
# - upon turn termination they unlock the game and call it to resume 
# - the game decides who should go next. 


# in an actual game you wouldn't use a for loop. 
# in actual game use flask /route for to send backend requests
# each request needs to tell backend which player it is and what they want to do
# backend checks if player is locked, and if NOT locked, check what action it is
# apply the action. if it is turn-terminating, end the turn and move the game one step forward while applying game rules 

# def simGame():
#     simGame = Game(num_decks=1, num_players=2)
#     # model a game where players draw two cards and discard a random one 
#     while True:  
#         simGame.update()
#         player = simGame.active_player
#         val = player.draw(2)
#         if val == "End of Deck": 
#             break 
#         card = player.discard("", True)
#         print(f"player{simGame.player_index}: current hand is {player.show()} and previously discarded {card['code']}")
#         player.lock = True 
#         simGame.lock = False                # unlock the game 
#         sleep(0.5)
#     simGame.game_finish()

# simGame()

# def WarGame(): 
#     simGame = War(num_decks=3, num_players=4)   
#     while True: 
#         simGame.update()
#         player = simGame.active_player
#         val = player.draw(3)
#         if val == "End of Deck": 
#             break 
#         card = player.discard("", True)
#         print(f"player{simGame.player_index}: Discarded {card['code']}")
#         simGame.lock = False 
#         sleep(0.001)
#     simGame.game_finish()

# WarGame()
#endregion