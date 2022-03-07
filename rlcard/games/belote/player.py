

class BelotePlayer:

    def __init__(self, player_id, np_random):
        ''' Initialize a Belote-decouverte player class
        '''
        self.player_id = player_id
        self.np_random = np_random
        self.hand = []
        self.table = []  # Cards known by both players
        self.secret = []  # Cards covered up 
        self.score =0


    def remove_card(self,card):
        #supprime une carte du jeu du joueur
        for card in self.table:
            if card in self.table:
                self.table.remove(card)
        
        for card in self.hand:
            if card in self.hand:
                self.hand.remove(card)


    def get_player_id(self):
        ''' Return player's id
        '''
        return self.player_id