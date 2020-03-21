from copy import deepcopy

from rlcard.games.uno.dealer import UnoDealer as Dealer
from rlcard.games.uno.player import UnoPlayer as Player
from rlcard.games.uno.round import UnoRound as Round


class UnoGame(object):

    def __init__(self, allow_step_back=False):
        self.allow_step_back = allow_step_back
        self.num_players = 2
        self.payoffs = [0 for _ in range(self.num_players)]

    def init_game(self):
        ''' Initialize players and state

        Returns:
            (tuple): Tuple containing:

                (dict): The first state in one game
                (int): Current player's id
        '''
        # Initalize payoffs
        self.payoffs = [0 for _ in range(self.num_players)]

        # Initialize a dealer that can deal cards
        self.dealer = Dealer()

        # Initialize four players to play the game
        self.players = [Player(i) for i in range(self.num_players)]

        # Deal 7 cards to each player to prepare for the game
        for player in self.players:
            self.dealer.deal_cards(player, 7)

        # Initialize a Round
        self.round = Round(self.dealer, self.num_players)

        # flip and perfrom top card
        top_card = self.round.flip_top_card()
        self.round.perform_top_card(self.players, top_card)

        # Save the hisory for stepping back to the last state.
        self.history = []

        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

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
        state['player_num'] = self.get_player_num()
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

    def get_player_num(self):
        ''' Return the number of players in Limit Texas Hold'em

        Returns:
            (int): The number of players in the game
        '''
        return self.num_players

    @staticmethod
    def get_action_num():
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


## For test
#if __name__ == '__main__':
#    #import time
#    #random.seed(0)
#    #start = time.time()
#    game = UnoGame()
#    for _ in range(1):
#        state, button = game.init_game()
#        print(button, state)
#        i = 0
#        while not game.is_over():
#            i += 1
#            legal_actions = game.get_legal_actions()
#            print('legal_actions', legal_actions)
#            action = np.random.choice(legal_actions)
#            print('action', action)
#            print()
#            state, button = game.step(action)
#            print(button, state)
#        print(game.get_payoffs())
#    print('step', i)
