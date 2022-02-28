import numpy as np

from rlcard.games.belote import Player
from rlcard.games.belote import Round
from rlcard.games.belote import Dealer
from rlcard.games.belote import Judger


NormalCardsPoints = {'7': 0, '8': 0, '9': 0, 'J': 2, 'Q': 3, 'K': 4, 'T': 10, 'A': 11}
TrumpCardsPoints = {'7': 0, '8': 0, 'Q': 3, 'K': 4, 'T': 10, 'A': 11, '9': 14, 'J': 20}


class BeloteGame:
    def __init__(self, allow_step_back=False):
        ''' Initialize the Belote game class
        '''
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()
        self.num_players = 2

    def init_game(self):
        ''' Initialize the game

        Returns:
            state (dict): the first state of the game
            player_id (int): current player's id
        '''
        # initialize dealer
        self.dealer = Dealer(self.np_random)

        # initialize players
        self.players = [Player(i, self.np_random)
                        for i in range(self.num_players)]

        # initialize judger
        self.judger = Judger(self.np_random)

        self.round = Round()
        self.state = self.get_state()

    def step(self, action):
        player = self.players[self.round.current_player]

        next_id = (player.player_id+1) % len(self.players)
        self.round.current_player = next_id

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            player_id (int): current player's id
        '''
        return self.game_pointer

    def get_num_players(self):
        ''' Return the number of players in the game
        '''
        return self.num_players

    @staticmethod
    def get_num_actions():
        ''' Return '''
