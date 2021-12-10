class DurakPlayer:

    def __init__(self, player_id, np_random):
        ''' Initialize a Durak player class
        Args:
            player_id (int): id for the player
        '''
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []
        self.status = 'alive'
        self.score = 0

    def get_player_id(self):
        ''' Return player's id
        '''
        return self.player_id
    
    def get_lowest_card(self):
        sorted_hand = sorted(self.hand,key=lambda x:"234567891JQKA".index(x.rank))
        return sorted_hand[0]
    
    def missing_cards(self):
        return max(6 - len(self.hand), 0)
