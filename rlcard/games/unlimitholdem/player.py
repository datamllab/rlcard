from rlcard.games.limitholdem.player import LimitholdemPlayer

class UnlimitholdemPlayer(LimitholdemPlayer):

    def __init__(self, player_id, init_chips):
        ''' Initilize a player.

        Args:
            player_id (int): The id of the player
            init_chips (int): The number of chips the player has initially
        '''
        
        super(UnlimitholdemPlayer, self).__init__(player_id)
        self.remained_chips = init_chips
