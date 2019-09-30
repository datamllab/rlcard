import random
import time
from copy import deepcopy

from rlcard.games.uno.dealer import UnoDealer as Dealer
from rlcard.games.uno.player import UnoPlayer as Player
from rlcard.games.uno.round import UnoRound as Round


class UnoGame(object):

    def __init__(self, allow_step_back=False):
        self.allow_step_back = allow_step_back
        self.num_players = 2
        self.payoffs = [0 for _ in range(self.num_players]

    def init_game(self):
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
        if not self.history:
            return False
        self.dealer, self.players, self.round = self.history.pop()
        return True

    def get_state(self, player_id):
        state = self.round.get_state(self.players, player_id)
        return state

    def get_payoffs(self):
        winner = self.round.winner
        if winner is not None and len(winner) == 1:
            self.payoffs[winner[0]] = 1
            self.payoffs[1 - winner[0]] = -1
        return self.payoffs

    def get_legal_actions(self):

        return self.round.get_legal_actions(self.players, self.round.current_player)

    def get_player_num(self):
        return self.num_players

    @staticmethod
    def get_action_num():
        return 61

    def get_player_id(self):
        return self.round.current_player

    def is_over(self):
        return self.round.is_over

'''
# For test
if __name__ == '__main__':
    import time
    #random.seed(0)
    #start = time.time()
    game = UnoGame()
    for _ in range(1):
        #print('*****init game*****')
        state, button = game.init_game()
        #print(button, state)
        i = 0
        legal_action_time = 0
        step_time = 0
        while not game.is_over():
            i += 1
            start1 = time.time()
            legal_actions = game.get_legal_actions()
            end1 = time.time()
            print('get_legal_action', end1 - start1)
            legal_action_time += (end1 - start1)
            print('legal_actions', legal_actions)
            if i == 3:
                print('step back')
                print(game.step_back())
                print(game.get_player_id())
                legal_actions = game.get_legal_actions()
                print('back legal actions', legal_actions)
                input()
            if not legal_actions:
                action = 'draw'
            else:
                action = random.choice(legal_actions)
            print('action', action)
            print()
            start2 = time.time()
            state, button = game.step(action)
            end2 = time.time()
            #print('step', end2 - start2)
            step_time += (end2 - start2)
            print(button, state)
        print(game.get_payoffs())
    #end = time.time()
    #print(end-start)
    print('legal_time', legal_action_time)
    print('step time', step_time)
    print(i)
'''
