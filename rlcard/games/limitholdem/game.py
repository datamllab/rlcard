from copy import deepcopy
import numpy as np

from rlcard.games.limitholdem.dealer import LimitholdemDealer as Dealer
from rlcard.games.limitholdem.player import LimitholdemPlayer as Player
from rlcard.games.limitholdem.judger import LimitholdemJudger as Judger
from rlcard.games.limitholdem.round import LimitholdemRound as Round

class LimitholdemGame(object):

    def __init__(self, allow_step_back=False):
        ''' Initialize the class limitholdem Game
        '''

        self.allow_step_back = allow_step_back

        # Some configarations of the game
        # These arguments can be specified for creating new games

        # Small blind and big blind
        self.small_blind = 1
        self.big_blind = 2 * self.small_blind

        # Raise amount and allowed times
        self.raise_amount = self.big_blind
        self.allowed_raise_num = 4

        self.num_players = 2

    def init_game(self):
        ''' Initialilze the game of Limit Texas Hold'em

        This version supports two-player limit texas hold'em

        Returns:
            (tuple): Tuple containing:

                (dict): The first state of the game
                (int): Current player's id
        '''

        # Initilize a dealer that can deal cards
        self.dealer = Dealer()

        # Initilize two players to play the game
        self.players = [Player(i) for i in range(self.num_players)]

        # Initialize a judger class which will decide who wins in the end
        self.judger = Judger()

        # Deal cards to each  player to prepare for the first round
        for i in range(2 * self.num_players):
            self.players[i % self.num_players].hand.append(self.dealer.deal_card())

        # Initilize public cards
        self.public_cards = []

        # Randomly choose a small blind and a big blind
        s = np.random.randint(0, self.num_players)
        b = (s + 1) % self.num_players
        self.players[b].in_chips = self.big_blind
        self.players[s].in_chips = self.small_blind

        # The player next to the big blind plays the first
        self.game_pointer = (b + 1) % self.num_players

        # Initilize a bidding round, in the first round, the big blind and the small blind needs to
        # be passed to the round for processing.
        self.round = Round(raise_amount=self.raise_amount,
                           allowed_raise_num=self.allowed_raise_num,
                           num_players=self.num_players)

        self.round.start_new_round(game_pointer=self.game_pointer, raised=[p.in_chips for p in self.players])

        # Count the round. There are 4 rounds in each game.
        self.round_counter = 0

        # Save the hisory for stepping back to the last state.
        self.history = []

        state = self.get_state(self.game_pointer)

        return state, self.game_pointer

    def step(self, action):
        ''' Get the next state

        Args:
            action (str): a specific action. (call, raise, fold, or check)

        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next plater's id
        '''

        if self.allow_step_back:
            # First snapshot the current state
            r = deepcopy(self.round)
            b = self.game_pointer
            r_c = self.round_counter
            d = deepcopy(self.dealer)
            p = deepcopy(self.public_cards)
            ps = deepcopy(self.players)
            self.history.append((r, b, r_c, d, p, ps))

        # Then we proceed to the next round
        self.game_pointer = self.round.proceed_round(self.players, action)

        # If a round is over, we deal more public cards
        if self.round.is_over():
            # For the first round, we deal 3 cards
            if self.round_counter == 0:
                self.public_cards.append(self.dealer.deal_card())
                self.public_cards.append(self.dealer.deal_card())
                self.public_cards.append(self.dealer.deal_card())
            # For the following rounds, we deal only 1 card
            elif self.round_counter <= 2:
                self.public_cards.append(self.dealer.deal_card())

            # Double the raise amount for the last two rounds
            if self.round_counter == 1:
                self.round.raise_amount = 2 * self.raise_amount

            self.round_counter += 1
            self.round.start_new_round(self.game_pointer)

        state = self.get_state(self.game_pointer)

        return state, self.game_pointer

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        '''

        if len(self.history) > 0:
            self.round, self.game_pointer, self.round_counter, self.dealer, self.public_cards, self.players = self.history.pop()
            return True
        return False

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
            (int): The number of actions. There are 4 actions (call, raise, check and fold)
        '''

        return 4

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            (int): current player's id
        '''

        return self.game_pointer

    def get_state(self, player):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        '''

        chips = [self.players[i].in_chips for i in range(self.num_players)]
        legal_actions = self.get_legal_actions()
        state = self.players[player].get_state(self.public_cards, chips, legal_actions)

        return state


    def is_over(self):
        ''' Check if the game is over

        Returns:
            (boolean): True if the game is over
        '''

        alive_players = [1 if p.status=='alive' else 0 for p in self.players]
        # If only one player is alive, the game is over.
        if sum(alive_players) == 1:
            return True

        # If all rounds are finshed
        if self.round_counter >= 4:
            return True
        return False

    def get_payoffs(self):
        ''' Return the payoffs of the game

        Returns:
            (list): Each entry corresponds to the payoff of one player
        '''

        hands = [p.hand + self.public_cards if p.status=='alive' else None for p in self.players]
        chips_payoffs = self.judger.judge_game(self.players, hands)
        payoffs = np.array(chips_payoffs) / (self.big_blind)
        return payoffs

    def get_legal_actions(self):
        ''' Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        '''

        return self.round.get_legal_actions()

# Test the game

#if __name__ == "__main__":
#    game = LimitholdemGame()
#    while True:
#        print('New Game')
#        state, game_pointer = game.init_game()
#        print(game_pointer, state)
#        i = 1
#        while not game.is_over():
#            i += 1
#            legal_actions = game.get_legal_actions()
#            if i == 3:
#                print('Step back')
#                print(game.step_back())
#                game_pointer = game.get_player_id()
#                print(game_pointer)
#                legal_actions = game.get_legal_actions()
#
#            action = np.random.choice(legal_actions)
#            print(game_pointer, action, legal_actions)
#            state, game_pointer = game.step(action)
#            print(game_pointer, state)
#
#        print(game.get_payoffs())

