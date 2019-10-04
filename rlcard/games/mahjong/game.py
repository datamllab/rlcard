import random
from copy import deepcopy

from rlcard.games.mahjong.dealer import MahjongDealer as Dealer
from rlcard.games.mahjong.player import MahjongPlayer as Player
from rlcard.games.mahjong.round import MahjongRound as Round
from rlcard.games.mahjong.judger import MahjongJudger as Judger
from rlcard.games.mahjong.utils import *


class MahjongGame(object):

    def __init__(self, allow_step_back=False):
        self.num_players = 4

    def init_game(self):
        # Initialize a dealer that can deal cards
        self.dealer = Dealer()

        # Initialize four players to play the game
        self.players = [Player(i) for i in range(self.num_players)]

        self.judger = Judger()
        self.round = Round(self.judger, self.dealer, self.num_players)

        # Deal 13 cards to each player to prepare for the game
        for player in self.players:
            self.dealer.deal_cards(player, 13)

        # Save the hisory for stepping back to the last state.
        self.history = []
        
        self.dealer.deal_cards(self.players[self.round.current_player], 1)
        state = self.get_state(self.round.current_player)
        self.cur_state = state
        return state, self.round.current_player

    def step(self, action):
        # First snapshot the current state
        #hist_dealer = deepcopy(self.dealer)
        #hist_round = deepcopy(self.round)
        #hist_players = deepcopy(self.players)
        #self.history.append((hist_dealer, hist_players, hist_round))

        self.round.proceed_round(self.players, action)
        state = self.get_state(self.round.current_player)
        self.cur_state = state
        return state, self.round.current_player

    def step_back(self):
        if not self.history:
            return False
        self.dealer, self.players, self.round = self.history.pop()
        return True

    def get_state(self, player_id, is_proceed=True):
        #if is_proceed:
        state = self.round.get_state(self.players, player_id)
        #else:
        #    state = self.cur_state
        return state

    def get_legal_actions(self, state):
        if state['valid_act'] == ['play']:
            state['valid_act'] = state['action_cards']
            return state['action_cards']
        else:
            return state['valid_act']

    def get_action_num(self):
        return 38 

    def get_player_num(self):
        return self.num_players

    def is_over(self):
        win, player = self.judger.judge_game(self)
        pile =[sorted([c.get_str() for c in s ]) for s in self.players[player].pile if self.players[player].pile != None]
        cards = sorted([c.get_str() for c in self.players[player].hand])
        count = len(cards) + sum([len(p) for p in pile])
        self.winner = player
        #print(win, self.round.current_player, player, cards, pile, count)
        return win

# For test
if __name__ == '__main__':
    import time
    random.seed(2)
    start = time.time()
    game = MahjongGame()
    for _ in range(100000):
        #print('*****init game*****')
        state, button = game.init_game()
        i = 0
        while not game.is_over():
            i += 1
            legal_actions = game.get_legal_actions(state)
            action = random.choice(legal_actions)
            flag=0
            #if len(legal_actions) < 3:
            #    flag=1
            #    print("Before:", state)
            #    print(game.round.current_player, action)
            state, button = game.step(action)
            #if action != 'stand' and flag==1:
            #    print("After:", state)
            #    print(state, game.round.current_player)
            #    exit()
            #print(button, state)
        winner_hand = [c.get_str() for c in game.players[game.winner].hand]
        winnder_pile = [[c.get_str() for c in s] for s in game.players[game.winner].pile]
        print(_, len(game.dealer.deck), game.winner, winner_hand, winnder_pile)
        if game.winner != -1:
            exit()
    end = time.time()
    print(end-start)
