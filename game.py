from api import Deck, Pile

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



    def update(self):
        # use polymorphism to define new update function
        # this should be called when you want to go to the next state
        if not self.lock: 
            self.player_index += 1 
            if self.player_index >= len(self.players): 
                self.player_index = 0 
            self.players[self.player_index].lock = False 
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

    def discard(self, code, discard: Pile): 
        if not self.lock: 
            card = self.pile.pop_specific(code) 
            discard.add(card)
            self.game.last_player = self 
            self.game.last_action = f"discard {code}"
            self.lock = True 
            self.game.lock = False 
            print("player has discarded")
            print("unlocked the game")
            print("game continues")
            self.game.update()
    
    def show(self):
        self.pile.show() 
    
# for each game the update needs to include additional code to enforce the rules. 
# basic workflow currently: 
# - unlock the game 
# - game unlocks a player 
# - game locks itself to wait for a turn-terminating action (if you want a custom one, write a new function)
#     - right now theoretically a player can draw infinite times in the simGame, so we need to change this 
# - the player performs some action until their turn terminates 
# - upon turn termination they unlock the game and call it to resume 
# - the game decides who should go next. 


simGame = Game(num_decks=10, num_players=5) 
discard = Pile(simGame.deck)
simGame.update() 
simGame.players[0].draw() 
print("player0 has drawn")
simGame.players[0].discard(simGame.players[0].pile.json_hand[0]["code"], discard)
        


        

