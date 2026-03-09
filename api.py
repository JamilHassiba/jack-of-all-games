import requests
import random

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

    def make_pile(self):
        """
        Create a new Pile associated with this deck.
        Useful for player hands or discard piles.
        """
        return Pile(self)


# ---------------------------
# Pile Class
# ---------------------------
class Pile:
    """
    Represents a pile of cards (e.g., a player's hand or discard pile).
    Pile draws from a Deck object and maintains its own local JSON list.
    """

    def __init__(self, deck: Deck):
        self.deck = deck
        self.userid = None
        self.json_hand = []  # List of card JSON objects

    def add(self, card_json):
        """
        Add a card to the pile.
        Note: does NOT validate against the deck; use draw() to safely draw from deck.
        """
        self.json_hand.append(card_json)

    def draw(self, count=1):
        """
        Draw `count` cards from the associated deck and add to this pile.
        Returns the drawn cards.
        """
        cards = self.deck.draw(count)
        if cards:
            self.json_hand += cards
        return cards

    def pop_random(self):
        """
        Remove and return a random card from the pile.
        """
        if not self.json_hand:
            return None
        index = random.randint(0, len(self.json_hand) - 1)
        return self.json_hand.pop(index)

    def pop_specific(self, code):
        """
        Remove and return a specific card from the pile using its code.
        """
        valid_codes = [i["code"] for i in self.json_hand]
        if code in valid_codes:
            index = valid_codes.index(code)
            return self.json_hand.pop(index)

        print("Invalid card code")
        return None

    def shuffle(self):
        """
        Shuffle the pile locally.
        """
        random.shuffle(self.json_hand)

    def show(self):
        """
        Return a list of card codes currently in the pile.
        """
        return [i["code"] for i in self.json_hand]

    def return_cards(self, card_codes):
        """
        Return specific cards from this pile back to the deck.
        Removes them from the pile and calls deck.return_cards().
        """
        codes_to_return = []
        cards_in_pile = [i["code"] for i in self.json_hand]

        for code in card_codes:
            if code in cards_in_pile:
                index = cards_in_pile.index(code)
                self.json_hand.pop(index)
                codes_to_return.append(code)

        if codes_to_return:
            self.deck.return_cards(codes_to_return)