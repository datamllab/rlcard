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


        

    def get_payoffs(self):
        return [self.game.winner['player']]
 








