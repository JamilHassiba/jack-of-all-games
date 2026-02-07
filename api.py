import requests # used for api
import random 

# DOCUMENTATION 
#
# Developed by Ryan. 
# If you want to make a new deck just do Deck(). It will automatically call the api and make a new deck and assign the correct id. 
# You can customise the deck you want with the parameters, but right now I only support a single deck per deck object. 
# If you want multiple decks please make multiple deck objects. It's way less trouble for me. 
# 
# TODO 
# - Add reshuffle 
# - Add piles 

chars = ["abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()-+_="]

class Deck: 
    def __init__(self, id=None, shuffle=True, decks=1, jokers=False): 
        self.url = "https://deckofcardsapi.com/api/deck/"
        if id: 
            self.id = id 
        else: 
            self.id = self.new(shuffle, decks, jokers)
    
    def new(self, shuffle, decks, jokers):
        params = {
            "jokers_enabled": jokers, 
            "deck_count": decks, 
        }

        if shuffle: 
            url = self.url + "new/shuffle/" 
            response = requests.get(url, params=params)
        else: 
            url = self.url + "new/"
            response = requests.get(url, params=params)
        
        if response.status_code == 200: 
            data = response.json()
            deck_id = data["deck_id"]
            return deck_id
        else: 
            print("Error!! Source: creation of new deck")
            return None 


    def draw(self, count=1): 
        params = {
            "count":count
        }
        if self.id: 
            cards = []
            url = self.url + f"{self.id}/draw/" 
            response = requests.get(url, params=params)
            if response.status_code == 200: 
                data = response.json() 
                for i in data['cards']: 
                    cards.append(i)
            
            return cards 
        else: 
            raise AttributeError("No attribute id for class deck. You somehow removed the id from the deck object.")
    
    def reshuffle(self, remaining_only=True):
        params = {
            "remaining": remaining_only
        } 
        url = self.url + f"{self.id}/" + "shuffle/"
        response = requests.get(url, params=params)
        if response.status_code == 200: 
            # info for debug only
            data = response.json() 
            print(self.id)
            print(data)
            return 1 
        else: 
            print("Error!! Source: Reshuffling a deck")
            return None 
    
    def return_cards(self, cards=None): 
        # cards needs to be an array of card codes, not json object. parse with cards[i]['code'] 
        url = self.url + f"{self.id}/return/"
        params = {"cards":cards}
        response = requests.get(url, params=params)
        if response.status_code == 200: 
            data = response.json() 
            return 1 
        else: 
            print("Error!! Source: Returning cards to the deck")
            return None 
    
    def make_pile(self): 
        return Pile(self)

class Pile: 
    def __init__(self, deck: Deck): 
        self.deck = deck 
        self.userid = None 
        self.json_hand = []              # an array of card json objects.

    def add(self, card_json): 
        # explicitly add a specified card to the json_hand. 
        # Warning, does not validate whether the card has been drawn from the deck
        # Use draw from deck instead for safety. Only use this to move cards between piles 
        self.json_hand.append(card_json)
    
    def draw(self, count=1): 
        cards = self.deck.draw(count) 
        self.json_hand += cards 
    
    def pop_random(self): 
        index = random.randint(0, len(self.json_hand)-1)
        card = self.json_hand[index]
        self.json_hand.pop(index)
        return card
    
    def pop_specific(self, code): 
        valid_codes = [i["code"] for i in self.json_hand]
        if code in valid_codes: 
            index = valid_codes.index(code)
            card = self.json_hand[index]
            self.json_hand.pop(index)
            return card 
        else: 
            print("Invalid card code")
            return None  
    
    def shuffle(self): 
        random.shuffle(self.json_hand)
    
    def show(self): 
        # print the json_hand to the terminal, not used in the actual webapp 
        hand = [i["code"] for i in self.json_hand]
        return hand
    
    def return_cards(self, card_codes):
        cards = [i["code"] for i in self.json_hand]
        codes = [] 
        for code in card_codes: 
            if code in cards: 
                index = cards.index(code)
                self.json_hand.pop(index)
                codes.append(code)
        self.deck.return_cards(codes)

# test code 

# GameDeck = Deck(decks=5)
# Player1 = GameDeck.make_pile()
# Player2 = GameDeck.make_pile() 
# Player3 = GameDeck.make_pile() 

# count = 10
# Player1.draw(count=count)
# Player2.draw(count=count)
# Player3.draw(count=count)

# print("Before removal")
# Player1.show()
# card = Player1.json_hand[0]["code"]
# print(f"Test removing the card {card}")
# Player1.return_cards([card])
# Player1.show()

# print("Testing shuffle")
# Player1.shuffle() 
# Player1.show()
                
# print("Testing drawing random card from pile")
# card = Player1.pop_random()
# print(card["code"])
# Player1.show()
    

