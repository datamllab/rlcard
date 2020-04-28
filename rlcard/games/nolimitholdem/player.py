from rlcard.games.limitholdem import Player


class NolimitholdemPlayer(Player):

    def __init__(self, player_id, init_chips, np_random):
        ''' Initilize a player.

        Args:
            player_id (int): The id of the player
            init_chips (int): The number of chips the player has initially
        '''
        super(NolimitholdemPlayer, self).__init__(player_id, np_random)
        self.remained_chips = init_chips

    def bet(self, chips):
        quantity = chips if chips <= self.remained_chips else self.remained_chips
        self.in_chips += quantity
        self.remained_chips -= quantity
