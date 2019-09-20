from rlcard.games.uno.utils import cards2list

class UnoPlayer(object):

    def __init__(self, player_id):
        ''' Initilize a player.

        Args:
            player_id (int): The id of the player
        '''
        self.player_id = player_id
        self.hand = []

    def get_player_id(self):
        ''' Return the id of the player
        '''

        return self.player_id

    def print_hand(self):
        for card in self.hand:
            print(card.str, end=' ')
        print()
