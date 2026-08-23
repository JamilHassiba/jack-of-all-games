import requests

# DOCUMENTATION 
# If you want to make a new deck just do Deck(). It will automatically call the api and make a new deck and assign the correct id. 
# You can customise the deck you want with the parameters, but right now I only support a single deck per deck object. 
# If you want multiple decks please make multiple deck objects. It's way less trouble for me.

# ---------------------------
# Deck Class
# ---------------------------
class Deck:
    """
    Represents a deck of cards using the Deck of Cards API.
    Can handle multiple decks and optional jokers.
    """

    def __init__(self, id=None, shuffle=True, decks=1, jokers=False):
        """
        Initialize a new deck object.
        If `id` is provided, uses an existing deck from the API.
        Otherwise, creates a new deck automatically.
        """
        self.url = "https://deckofcardsapi.com/api/deck/"
        self.decks = decks
        self.jokers = jokers

        # If id is provided, use it; otherwise, create a new deck
        if id:
            self.id = id
        else:
            self.new(shuffle=shuffle, decks=decks, jokers=jokers)

        # Track remaining cards locally (initially)
        self.remaining = decks * (52 + 2 * jokers)

    def new(self, shuffle=True, decks=1, jokers=False):
        """
        Create a new deck (or multiple decks) with optional shuffling and jokers.
        Updates self.id and self.remaining based on API response.
        """
        params = {
            "jokers_enabled": jokers,
            "deck_count": decks,
        }

        # Determine endpoint: shuffle on creation or not
        url = self.url + ("new/shuffle/" if shuffle else "new/")
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            self.id = data["deck_id"]         # Store API deck ID
            self.remaining = data["remaining"]  # Sync remaining cards
            return self.id
        else:
            print("Error creating new deck")
            return None

    def draw(self, count=1):
        """
        Draw `count` cards from the deck.
        Returns a list of card JSON objects.
        If not enough cards, returns an empty list.
        """
        if self.remaining < count:
            return []

        if not self.id:
            raise AttributeError("Deck has no ID")

        url = self.url + f"{self.id}/draw/"
        params = {"count": count}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            self.remaining = data["remaining"]  # Sync remaining cards
            return data["cards"]                # List of card objects

        print("Error drawing cards from deck")
        return []

    def reshuffle(self, remaining_only=True):
        """
        Reshuffle the deck.
        `remaining_only=True` will only shuffle remaining cards.
        Updates self.remaining.
        """
        url = self.url + f"{self.id}/shuffle/"
        params = {"remaining": remaining_only}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            self.remaining = data["remaining"]
            return True

        print("Error reshuffling deck")
        return False

    def return_cards(self, cards=None):
        """
        Return specific cards to the deck.
        `cards` should be a list of card codes (e.g., ['AS', '10D']).
        Updates self.remaining.
        """
        url = self.url + f"{self.id}/return/"
        params = {"cards": cards}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            self.remaining = data["remaining"]
            return True

        print("Error returning cards to deck")
        return False
