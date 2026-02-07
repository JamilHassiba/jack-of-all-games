from api import Deck, Pile
from time import sleep

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
            self.active_player = self.players[self.player_index]
            self.active_player.lock = False 
            self.lock = True 
            print("testing global locks")
            print(f"unlocked player{self.player_index}")

class Player: 
    def __init__(self, game: Game): 
        self.game = game
        self.pile = Pile(game.deck)
        self.lock = True 
    
    def draw(self, count=1):
        if not self.lock:
            self.pile.draw(count)

    def discard(self, code, discard: Pile, random=False): 
        if not self.lock: 
            if random:
                card = self.pile.pop_random()
            else:
                card = self.pile.pop_specific(code) 
                discard.add(card)
            self.lock = True 
            return card
    
    def show(self):
        return self.pile.show() 
    
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
def simGame():
    simGame = Game(num_decks=10, num_players=5)
    # unlock the first player 
    simGame.players[0].lock = False 
    discard = simGame.deck.make_pile()
    # model a game where players draw two cards and discard a random one 
    while True:  
        simGame.update()
        player = simGame.active_player
        player.draw(2)
        card = player.discard("", discard, True)
        print(f"player{simGame.player_index}: current hand is {player.show()} and previously discarded {card['code']}")
        simGame.lock = False                # unlock the game 
        sleep(1)

simGame()     


        

