from copy import deepcopy
import numpy as np

from rlcard.games.durak import Dealer
from rlcard.games.durak import Player
from rlcard.games.durak import Judger
from rlcard.games.durak import Round

class DurakGame:

    def __init__(self):
        ''' Initialize the class Blackjack Game
        '''
        self.np_random = np.random.RandomState()

    def configure(self):
        ''' Specifiy some game specific parameters, such as number of players
        '''
        self.num_players = 2
    
    def is_super_suite(self, card):
        ''' Determine if card is super suite
        Args:
            card (object): card to check
            dealer (object): Durak dealer instance
        Returns:/
            bool: if card is super suite
        '''
        return card.suite == self.dealer.super_suite

    def get_first_attacker(self):
        ''' 
            Determine which player is attacking first
        '''
        # Player with the lowest card attcks first
        attacker_id = min([0, 1], key= lambda i: "234567891JQKA".index(self.players[i].get_lowest_card().rank) )
        defender_id = 0 if attacker_id == 1 else 1
        
        

        print(f"Player {attacker_id} is the attacker }")
        return self.players[attacker_id], self.players[defender_id]
    
    
    def init_game(self):
        ''' Initialilze the game
        Returns:
            state (dict): the first state of the game
            player_id (int): current player's id
        '''
        self.configure()
        # Initialize a dealer that can deal cards
        self.dealer = Dealer(self.np_random)

        # Initialize 2 players to play the game
        self.players = [Player(i, self.np_random) for i in range(self.num_players)]

        # Deal 6 cards to each player to prepare for the game
        for player in self.players:
            self.dealer.deal_cards(player)
        
        attacker, defender = self.get_first_attacker()

        # Initialize a Round
        self.round = Round(self.dealer, attacker, defender, self.np_random)

    def step(self, action):
        ''' Get the next state

        Args:
            action (str): A specific action

        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next plater's id
        '''

        if self.allow_step_back:
            # First snapshot the current state
            his_dealer = deepcopy(self.dealer)
            his_round = deepcopy(self.round)
            his_players = deepcopy(self.players)
            self.history.append((his_dealer, his_players, his_round))

        self.round.proceed_round(self.players, action)
        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        '''
        if not self.history:
            return False
        self.dealer, self.players, self.round = self.history.pop()
        return True

    def get_state(self, player_id):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        '''
        state = self.round.get_state(self.players, player_id)
        state['num_players'] = self.get_num_players()
        state['current_player'] = self.round.current_player
        return state

    def get_payoffs(self):
        ''' Return the payoffs of the game

        Returns:
            (list): Each entry corresponds to the payoff of one player
        '''
        winner = self.round.winner
        if winner is not None and len(winner) == 1:
            self.payoffs[winner[0]] = 1
            self.payoffs[1 - winner[0]] = -1
        return self.payoffs

    def get_legal_actions(self):
        ''' Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        '''

        return self.round.get_legal_actions(self.players, self.round.current_player)

    def get_num_players(self):
        ''' Return the number of players in Limit Texas Hold'em

        Returns:
            (int): The number of players in the game
        '''
        return self.num_players

    @staticmethod
    def get_num_actions():
        ''' Return the number of applicable actions

        Returns:
            (int): The number of actions. There are 61 actions
        '''
        return 61

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            (int): current player's id
        '''
        return self.round.current_player

    def is_over(self):
        ''' Check if the game is over

        Returns:
            (boolean): True if the game is over
        '''
        return self.round.is_over