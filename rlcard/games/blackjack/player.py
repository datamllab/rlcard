
class BlackjackPlayer(object):

    def __init__(self, player_id):
        ''' Initialize a Blackjack player class

        Args:
            player_id (int): id for the player
        '''
        self.player_id = player_id
        self.hand = []
        self.status = 'alive'
        self.score = 0

    def get_player_id(self):
        ''' Return player's id
        '''
        return self.player_id
