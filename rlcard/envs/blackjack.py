from rlcard.games.blackjack import *
from rlcard.envs.env import Env
from rlcard.games.blackjack.game import BlackjackGame as Game
from rlcard.utils.utils import * 
import numpy as np

import random

class BlackjackEnv(Env):
    """
    Blackjack Environment
    """

    def __init__(self):
        super().__init__(Game())
        self.rank2score = {"A":10, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":10, "Q":10, "K":10}


    def extract_state(self, state):
        cards = state['state']
        my_cards = cards[0]
        dealer_cards = cards[1]

        def get_scores_and_A(hand):
            score = 0
            has_a = 0
            for card in hand:
                score += self.rank2score[card[1:]]
                if card[1] == 'A':
                    has_a = 1
            if score > 21 and has_a == 1:
                score -= 9

            return score, has_a

        my_score, has_a = get_scores_and_A(my_cards)
        dealer_score, _ = get_scores_and_A(dealer_cards)
        obs = [my_score, dealer_score, has_a]
        return obs

    def encode_action(self, actions):
        a = []
        for i, act in enumerate(actions):
            a.append(i)
        return a

    def cfr_state(self, s, player):
        state = {}
        obs = self.extract_state(s)
        state['obs'] = obs
        state['player'] = player
        state['action'] = self.encode_action(s['actions'])
        return state
    
    def get_child_state(self, action):
        #print("Get Child")
        next_state, next_player = self.game.step(action)
        #self.game.step_back()
        #print(self.cfr_state(next_state, next_player))
        return self.cfr_state(next_state, next_player)

    def get_payoffs(self):
        payoff = 0
        if self.game.winner['player'] == 1 and self.game.winner['dealer'] == 0:
            payoff = 1
        elif self.game.winner['player'] == 0 and self.game.winner['dealer'] == 1:
            payoff = -1
        else:
            payoff = 0
        return payoff 
 

