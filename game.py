from api import Deck, Pile
from time import sleep
import random
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()-+_="

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
            self.lock = True 
            print("testing global locks")
            print(f"unlocked player{self.player_index}")
    
    def game_turn(self): 
        # use polymorphism to define new game_turn
        # this action is applied once every player has acted once in a round
        pass

    def game_finish(self): 
        # use polymorphism to define new game_finish
        # this action is applied when the game finishes 
        print("game finished")



class Player: 
    def __init__(self, game: Game): 
        self.game = game
        self.pile = Pile(game.deck)
        self.lock = True 
        self.score = 0
        self.discarded = []             # for logging only. not an actual pile 
    
    def draw(self, count=1):
        if not self.lock:
            val = self.pile.draw(count)
            if val == None: 
                return "End of Deck"

    def discard(self, code, discard: Pile, random=False): 
        if not self.lock: 
            if random:
                card = self.pile.pop_random()
                self.discarded.append(card)
            else:
                card = self.pile.pop_specific(code) 
                discard.add(card)
                self.discarded.append(card)
            self.lock = True 
            return card
    
    def show(self):
        return self.pile.show() 

class Room: 
    def __init__(self, game_type, num_players, players=None, id=None): 
        self.game_type = game_type 
        self.players = players 
        if id == None: 
            length = random.randint(6, 10)
            self.id = "".join([chars[random.randint(0, len(chars)-1)] for i in range(length)])
        else: 
            self.id = id

        if game_type == "war": 
            self.game = War(4, num_players)
        elif game_type == "poker": 
            pass 
            # this is an example of how we would extend 

class War(Game): 
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
#     discard = simGame.deck.make_pile()
#     # model a game where players draw two cards and discard a random one 
#     while True:  
#         simGame.update()
#         player = simGame.active_player
#         val = player.draw(2)
#         if val == "End of Deck": 
#             break 
#         card = player.discard("", discard, True)
#         print(f"player{simGame.player_index}: current hand is {player.show()} and previously discarded {card['code']}")
#         simGame.lock = False                # unlock the game 
#         sleep(0.5)
#     simGame.game_finish()

# def WarGame(): 
#     simGame = War(num_decks=3, num_players=4)   
#     discard = simGame.deck.make_pile()
#     while True: 
#         simGame.update()
#         player = simGame.active_player
#         val = player.draw(3)
#         if val == "End of Deck": 
#             break 
#         card = player.discard("", discard, True)
#         print(f"player{simGame.player_index}: Discarded {card['code']}")
#         simGame.lock = False 
#         sleep(0.001)
#     simGame.game_finish()

# WarGame()

myRoom = Room("war")
print(myRoom.id)