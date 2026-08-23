"""Blackjack game engine: player, dealer, round evaluation, and game orchestration."""

from cards import Deck
from states.fsm import fsm
import states.blackjack_states as blackjack_states
from db import record_win, record_loss


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
        for player in winners:
            print(f"WinPlayers called for {player.username}")
            if BlackjackRound.DoesEntityHaveBlackjack(player): player.AddGameScore(2)
            else: player.AddGameScore(1)
            if player.username:
                record_win(player.username)

    @staticmethod
    def LosePlayers(losers):
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
    
