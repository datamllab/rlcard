import random
from copy import deepcopy
from rlcard.core import Game
from rlcard.games.limitholdem.dealer import LimitholdemDealer as Dealer
from rlcard.games.limitholdem.player import LimitholdemPlayer as Player
from rlcard.games.limitholdem.judger import LimitholdemJudger as Judger
from rlcard.games.limitholdem.round import LimitholdemRound as Round

class LimitholdemGame(Game):

    def __init__(self):
        ''' Initialize the class limitholdem Game
        '''

        super().__init__()
        
        # Some configarations of the game
        # You may specify them for your own purpose
        
        # Small blind and big blind
        self.small_blind = 1
        self.big_blind = 2 * self.small_blind

        # Raise amount and allowed times
        self.raise_amount = 2 * self.big_blind
        self.allowed_raise_num = 4

        self.num_players = 2

    def init_game(self):
        ''' Initialilze the game of Limit Texas Hold'em

        This version supports two-player limit texas hold'em

        Returns:
            state (dict): the first state of the game
            player_id (int): current player's id
        '''

        # Initilize a dealer that can deal cards
        self.dealer = Dealer()

        # Initilize two players who play the game
        self.players = [Player(0), Player(1)]

        # Initialize a judger class which will decide who wins in the end
        self.judger = Judger()

        # Deal cards to the two player to prepare for the first round
        self.players[0].hand.append(self.dealer.deal_card())
        self.players[1].hand.append(self.dealer.deal_card())
        self.players[0].hand.append(self.dealer.deal_card())
        self.players[1].hand.append(self.dealer.deal_card())

        # Initilize public cards
        self.public_cards = []

        # Randomly choose a big blind and a small blind
        b = random.randint(0, 1)
        s = (b + 1) % self.num_players
        self.players[b].in_chips = self.big_blind
        self.players[s].in_chips = self.small_blind

        # The small blind plays the first in two-palyer game
        self.button = s

        # Initilize a bidding round
        self.round = Round(self.raise_amount, self.allowed_raise_num)
        self.round.start_new_round(button=self.button, raised=[p.in_chips for p in self.players])
 
        self.round_counter = 0
        self.history = []

        state = self.get_state(self.button)

        return state, self.button
        
    def step(self, action):
        ''' Get the next state

        Args:
            action (str): a specific action. (call, raise, fold, or check)

        Returns:
            dict: next player's state
            int: next plater's id
        '''

        r = deepcopy(self.round)
        b = self.button
        r_c = self.round_counter
        d = deepcopy(self.dealer)
        p = deepcopy(self.public_cards)
        ps = deepcopy(self.players)
        self.history.append((r, b, r_c, d, p, ps))

        self.button = self.round.proceed_round(self.players[self.button], action)
        
        # If a round is over, we deal more public cards
        if self.round.is_over():
            if self.round_counter == 0:
                self.public_cards.append(self.dealer.deal_card())
                self.public_cards.append(self.dealer.deal_card())
                self.public_cards.append(self.dealer.deal_card())
            else:
                self.public_cards.append(self.dealer.deal_card())

            self.round_counter += 1
            self.round.start_new_round(self.button)

        state = self.get_state(self.button)
            
        return state, self.button

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            Status (bool): check if the step back is success or not
        '''

        if len(self.history) > 0:
            self.round, self.button, self.round_counter, self.dealer, self.public_cards, self.players = self.history.pop()
            return True
        return False

    def get_player_num(self):
        ''' Return the number of players in Limit Texas Hold'em

        Returns:
            number_of_player (int): Curent version has 2 players
        '''
        return 2

    def get_action_num(self):
        ''' Return the number of applicable actions

        Returns:
            number_of_actions (int): there are only two actions (call and raise)
        '''
        return 4

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            player_id (int): current player's id
        '''

        return self.button

    def get_state(self, player):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            state (dict): corresponding player's state
        '''
        state = self.players[player].get_state(self.public_cards, self.players[1-player].in_chips)
        return state


    def is_over(self):
        ''' Check if the game is over

        Returns:
            status (bool): True/False
        '''

        alive_players = [1 if p.status=='alive' else 0 for p in self.players]
        if sum(alive_players) == 1:
            return True

        if self.round_counter >= 3:
            return True
        return False

    def get_payoffs(self):
        ''' Return the payoffs of the game

        Returns:
            A list of the payoffs
        '''

        alive_players = [1 if p.status=='alive' else 0 for p in self.players]
        hands = [p.hand + self.public_cards if p.status=='alive' else None for p in self.players]
        payoffs = self.judger.judge_game(self.players, hands)
        return payoffs

    def get_legal_actions(self):
        ''' Return the legal actions for current player

        Returns:
            A list of legal actions
        '''

        return self.round.get_legal_actions()

    
# Test the game

if __name__ == "__main__":
    game = LimitholdemGame()
    while True:
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

