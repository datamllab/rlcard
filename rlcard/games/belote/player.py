

class BelotePlayer:

    def __init__(self, player_id, np_random):
        ''' Initialize a Belote-decouverte player class
        '''
        self.player_id = player_id
        self.np_random = np_random
        self.hand = []
        self.table = []  # Cards known by both players
        self.secret = []  # Cards covered up 

    def get_player_id(self):
        ''' Return player's id
        '''
        return self.player_id