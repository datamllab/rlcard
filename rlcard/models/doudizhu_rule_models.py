''' Dou Dizhu rule models
'''

import numpy as np

import rlcard
from rlcard.games.doudizhu.utils import CARD_TYPE, INDEX
from rlcard.models.model import Model

class DouDizhuRuleAgentV1(object):
    ''' Dou Dizhu Rule agent version 1
    '''

    def __init__(self):
        self.use_raw = True

    def step(self, state):
        ''' Predict the action given raw state. A naive rule.
        Args:
            state (dict): Raw state from the game

        Returns:
            action (str): Predicted action
        '''
        state = state['raw_obs']
        trace = state['trace']
        # the rule of leading round
        if len(trace) == 0 or (len(trace) >= 3 and trace[-1][1] == 'pass' and trace[-2][1] == 'pass'):
            comb = self.combine_cards(state['current_hand'])
            min_card = state['current_hand'][0]
            for _, actions in comb.items():
                for action in actions:
                    if min_card in action:
                        return action
        # the rule of following cards
        else:
            target = state['trace'][-1][-1]
            target_player = state['trace'][-1][0]
            if target == 'pass':
                target = state['trace'][-2][-1]
                target_player = state['trace'][-1][0]
            the_type = CARD_TYPE[0][target][0][0]
            chosen_action = ''
            rank = 1000
            for action in state['actions']:
                if action != 'pass' and the_type == CARD_TYPE[0][action][0][0]:
                    if int(CARD_TYPE[0][action][0][1]) < rank:
                        rank = int(CARD_TYPE[0][action][0][1])
                        chosen_action = action
            if chosen_action != '':
                return chosen_action
            landlord = state['landlord']
            if target_player != landlord and state['self'] != landlord:
                return 'pass'
            return np.random.choice(state['actions'])

    def eval_step(self, state):
        ''' Step for evaluation. The same to step
        '''
        return self.step(state), []

    def combine_cards(self, hand):
        '''Get optimal combinations of cards in hand
        '''
        comb = {'rocket': [], 'bomb': [], 'trio': [], 'trio_chain': [],
                'solo_chain': [], 'pair_chain': [], 'pair': [], 'solo': []}
        # 1. pick rocket
        if hand[-2:] == 'BR':
            comb['rocket'].append('BR')
            hand = hand[:-2]
        # 2. pick bomb
        hand_cp = hand
        for index in range(len(hand_cp) - 3):
            if hand_cp[index] == hand_cp[index+3]:
                bomb = hand_cp[index: index+4]
                comb['bomb'].append(bomb)
                hand = hand.replace(bomb, '')
        # 3. pick trio and trio_chain
        hand_cp = hand
        for index in range(len(hand_cp) - 2):
            if hand_cp[index] == hand_cp[index+2]:
                trio = hand_cp[index: index+3]
                if len(comb['trio']) > 0 and INDEX[trio[-1]] < 12 and (INDEX[trio[-1]]-1) == INDEX[comb['trio'][-1][-1]]:
                    comb['trio'][-1] += trio
                else:
                    comb['trio'].append(trio)
                hand = hand.replace(trio, '')
        only_trio = []
        only_trio_chain = []
        for trio in comb['trio']:
            if len(trio) == 3:
                only_trio.append(trio)
            else:
                only_trio_chain.append(trio)
        comb['trio'] = only_trio
        comb['trio_chain'] = only_trio_chain
        # 4. pick solo chain
        hand_list = self.card_str2list(hand)
        chains, hand_list = self.pick_chain(hand_list, 1)
        comb['solo_chain'] = chains
        # 5. pick par_chain
        chains, hand_list = self.pick_chain(hand_list, 2)
        comb['pair_chain'] = chains
        hand = self.list2card_str(hand_list)
        # 6. pick pair and solo
        index = 0
        while index < len(hand) - 1:
            if hand[index] == hand[index+1]:
                comb['pair'].append(hand[index] + hand[index+1])
                index += 2
            else:
                comb['solo'].append(hand[index])
                index += 1
        if index == (len(hand) - 1):
            comb['solo'].append(hand[index])
        return comb

    @staticmethod
    def card_str2list(hand):
        hand_list = [0 for _ in range(15)]
        for card in hand:
            hand_list[INDEX[card]] += 1
        return hand_list

    @staticmethod
    def list2card_str(hand_list):
        card_str = ''
        cards = [card for card in INDEX]
        for index, count in enumerate(hand_list):
            card_str += cards[index] * count
        return card_str

    @staticmethod
    def pick_chain(hand_list, count):
        chains = []
        str_card = [card for card in INDEX]
        hand_list = [str(card) for card in hand_list]
        hand = ''.join(hand_list[:12])
        chain_list = hand.split('0')
        add = 0
        for index, chain in enumerate(chain_list):
            if len(chain) > 0:
                if len(chain) >= 5:
                    start = index + add
                    min_count = int(min(chain)) // count
                    if min_count != 0:
                        str_chain = ''
                        for num in range(len(chain)):
                            str_chain += str_card[start+num]
                            hand_list[start+num] = int(hand_list[start+num]) - int(min(chain))
                        for _ in range(min_count):
                            chains.append(str_chain)
                add += len(chain)
        hand_list = [int(card) for card in hand_list]
        return (chains, hand_list)


class DouDizhuRuleModelV1(Model):
    ''' Dou Dizhu Rule Model version 1
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        env = rlcard.make('doudizhu')

        rule_agent = DouDizhuRuleAgentV1()
        self.rule_agents = [rule_agent for _ in range(env.num_players)]

    @property
    def agents(self):
        ''' Get a list of agents for each position in a the game

        Returns:
            agents (list): A list of agents

        Note: Each agent should be just like RL agent with step and eval_step
              functioning well.
        '''
        return self.rule_agents
