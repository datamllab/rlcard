import random
from copy import deepcopy
from rlcard.games.limitholdem.game import LimitholdemGame

from rlcard.games.unlimitholdem.dealer import UnlimitholdemDealer as Dealer
from rlcard.games.unlimitholdem.player import UnlimitholdemPlayer as Player
from rlcard.games.unlimitholdem.judger import UnlimitholdemJudger as Judger
from rlcard.games.unlimitholdem.round import UnlimitholdemRound as Round

class UnlimitholdemGame(LimitholdemGame):

    def __init__(self):
        ''' Initialize the class unlimitholdem Game
        '''

        # small blind and big blind
        self.small_blind = 1
        self.big_blind = 2 * self.small_blind
        
        # config players
        self.num_players = 2
        self.init_chips = 100

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
        self.players = [Player(i, self.init_chips) for i in range(self.num_players)]

        # Initialize a judger class which will decide who wins in the end
        self.judger = Judger()

        # Deal cards to each  player to prepare for the first round
        for i in range(2 * self.num_players):
            self.players[i % self.num_players].hand.append(self.dealer.deal_card())

        # Initilize public cards
        self.public_cards = []

        # Randomly choose a big blind and a small blind
        b = random.randint(0, self.num_players-1)
        s = (b + 1) % self.num_players
        self.players[b].in_chips = self.big_blind
        self.players[s].in_chips = self.small_blind

        # The player next to the small blind plays the first
        self.button = (s + 1) % self.num_players

        # Initilize a bidding round, in the first round, the big blind and the small blind needs to
        # be passed to the round for processing.
        self.round = Round(self.num_players)

        self.round.start_new_round(button=self.button, raised=[p.in_chips for p in self.players])

        # Count the round. There are 4 rounds in each game.
        self.round_counter = 0

        # Save the hisory for stepping back to the last state.
        self.history = []

        state = self.get_state(self.button)

        return state, self.button

    def get_legal_actions(self):
        ''' Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        '''

        return self.round.get_legal_actions(self.players) 

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

if __name__ == "__main__":
    game = UnlimitholdemGame()
    
    while True:
        print('New Game')
        state, button = game.init_game()
        print(button, state)
        i = 1
        while not game.is_over():
            i += 1
            legal_actions = game.get_legal_actions()
            if i == 3:
                print('Step back')
                print(game.step_back())
                button = game.get_player_id()
                print(button)
                legal_actions = game.get_legal_actions()

            action = random.choice(legal_actions)
            print(button, action, legal_actions)
            state, button = game.step(action)
            print(button, state)

        print(game.get_payoffs())
