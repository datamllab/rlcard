
class UnoPlayer(object):

    def __init__(self, player_id):
        ''' Initilize a player.

        Args:
            player_id (int): The id of the player
        '''
        self.player_id = player_id
        self.hand = []
        self.stack = []

    def get_player_id(self):
        ''' Return the id of the player
        '''

        return self.player_id
