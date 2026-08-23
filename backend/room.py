"""Room: a joinable lobby that owns one game instance."""

import random

from games.blackjack import Blackjack
from games.crazyeights import CrazyEights

chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"


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

        if game_type == "blackjack":
            self.game = Blackjack(socketio, num_players, self)
        elif game_type == "crazyeights":
            self.game = CrazyEights(socketio, num_players, self)
        else:
            pass
