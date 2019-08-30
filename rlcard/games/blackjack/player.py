
from rlcard.core import Player

class BlackjackPlayer(Player):

    def __init__(self, player_id):
        self.player_id = player_id
        self.hand = []
        self.status = 'alive'
        self.score = 0

    #def play(self, action):
    #    if action == 1:
    #        player

    def get_player_id(self):
        return self.player_id
