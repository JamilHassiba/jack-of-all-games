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
    
    def make_pile(self, name=None): 
        if name: 
            pile = Pile(name, self)
        else: 
            raise AttributeError("Pile needs a name!")
        return pile 
    
    def return_cards(self, cards=None): 
        url = self.url + f"{self.id}/return/"
        params = {"cards":cards}
        response = requests.get(url, params=params)
        if response.status_code == 200: 
            data = response.json() 
            return 1 
        else: 
            print("Error!! Source: Returning cards to the deck")
            return None 

    
class Pile: 
    def __init__(self, name=None, parent=None): 

        if name: 
            self.name = name 
        else: 
            raise AttributeError("Pile requires a name!")
        
        if parent: 
            self.parent = parent 
        else: 
            raise AttributeError("No parent found for pile!")
        
        self.url = "https://deckofcardsapi.com/api/deck/" + f"{self.parent.id}/pile/{self.name}"
    
    def add(self, cards): 
        url = self.url + "/add/"
        params = {"cards": cards}
        response = requests.get(url, params=params)
        if response.status_code == 200: 
            data = response.json() 
            return 1 
        else: 
            print("Error!! Source: Adding cards to a pile")
            return None 
    
    def shuffle(self):
        url = self.url + "/shuffle/"
        response = requests.get(url)
        if response.status_code == 200: 
            data = response.json() 
            return 1 
        else:
            print("Error!! Source: shuffling a pile") 
            return None 
    
    def show(self): 
        url = self.url + "/list/"
        print(url)
        response = requests.get(url) 
        if response.status_code == 200: 
            data = response.json() 
            cards = data["piles"][self.name]["cards"]
            return cards
            
        else: 
            print("Error!! Source: Showing a pile")
            print(response.status_code)
            return None 
    
    def return_to_deck(self, cards=None): 
        url = self.url + "/return/"
        params = {"cards": cards}
        response = requests.get(url, params)
        if response.status_code == 200: 
            data = response.json() 
            return 1 
        else: 
            print("Error!! Source: returning cards from a pile to the parent deck")
            return None 


