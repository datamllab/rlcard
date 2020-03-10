import numpy as np

from rlcard.envs.env import Env
from rlcard.games.blackjack.game import BlackjackGame as Game


class BlackjackEnv(Env):
    ''' Blackjack Environment
    '''

    def __init__(self, config):
        ''' Initialize the Blackjack environment
        '''
        self.game = Game()
        super().__init__(config)
        self.rank2score = {"A":11, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "T":10, "J":10, "Q":10, "K":10}
        self.actions = ['hit', 'stand']
        self.state_shape = [2]

    def _get_legal_actions(self):
        ''' Get all leagal actions

        Returns:
            encoded_action_list (list): return encoded legal action list (from str to int)
        '''
        encoded_action_list = []
        for i in range(len(self.actions)):
            encoded_action_list.append(i)
        return encoded_action_list

    def _extract_state(self, state):
        ''' Extract the state representation from state dictionary for agent

        Args:
            state (dict): Original state from the game

        Returns:
            observation (list): combine the player's score and dealer's observable score for observation
        '''
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
                score -= 10
            return score, has_a

        my_score, _ = get_scores_and_A(my_cards)
        dealer_score, _ = get_scores_and_A(dealer_cards)
        obs = np.array([my_score, dealer_score])

        legal_actions = [i for i in range(len(self.actions))]
        extracted_state = {'obs': obs, 'legal_actions': legal_actions}
        if self.allow_raw_data:
            extracted_state['raw_obs'] = state
            extracted_state['raw_legal_actions'] = [a for a in self.actions]
        if self.record_action:
            extracted_state['action_record'] = self.action_recorder
        return extracted_state

    def get_payoffs(self):
        ''' Get the payoff of a game

        Returns:
           payoffs (list): list of payoffs
        '''
        if self.game.winner['player'] == 0 and self.game.winner['dealer'] == 1:
            return [-1]
        elif self.game.winner['dealer'] == 0 and self.game.winner['player'] == 1:
            return [1]
        elif self.game.winner['player'] == 1 and self.game.winner['dealer'] == 1:
            return [0]

    def _decode_action(self, action_id):
        ''' Decode the action for applying to the game

        Args:
            action id (int): action id

        Returns:
            action (str): action for the game
        '''
        return self.actions[action_id]
