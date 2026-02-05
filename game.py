from api import Deck, Pile

class Game: 
    def __init__(self, num_decks, num_players, shuffle=True, jokers=False): 
        # documentation 
        # int num_decks = number of decks used for the game 
        # bool shuffle = whether the decks generated should be shuffled 
        # bool jokers = whether the decks generated should have jokers 
        # array of int num_players = an array of length num_decks representing the number of different players per deck. 
        # notes on limitations of the game: you cannot assign one person to multiple decks, though one deck can have multiple person 
        decks = [] 
        players = [] 
        for i in range(num_decks): 
            deck = Deck(shuffle=shuffle, jokers=jokers)
            decks.append(deck)
        self.decks = decks 

        if len(num_players) != len(decks): 
            raise ValueError("Size of num_players array does not match the number of decks!")

        for i in range(len(num_players)): 
            name = f"player{i}"
            player_count = num_players[i]   # number of players for this deck 
            deck = self.decks[i] 
            pile = deck.make_pile(name=name)
            player = Player(pile)
            players.append(player)
        players[0].lock = False 
        self.player_index = 0 
        self.players = players 

    
    def update(self):
        # use polymorphism to define new update function
        # this should be called when you want to go to the next state
        # player.lock locks the player from making a move 
        pass  


class Player: 
    # documentation 

    def __init__(self, pile): 
        self.pile = pile 
        self.can_show = False 
        self.lock = True 
    
    def draw(self, count=1): 
        if not self.lock: 
            cards = self.pile.parent.draw(count=count) 
            self.pile.add(cards)
            self.can_show = True 

    def show(self): 
        if self.can_show: 
            cards = self.pile.show() 
            print(cards)
            return cards
    

class Blackjack(Game): 
    def update(self): 
        active_player = self.players[self.player_index]
        active_player.draw()
        


        

