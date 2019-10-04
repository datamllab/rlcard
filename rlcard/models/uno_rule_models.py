''' UNO rule models
'''

import rlcard
from rlcard.models.model import Model

class UNORuleAgentV1(object):
    ''' UNO Rule agent version 1
    '''

    def __init__(self):
        pass

    def step(self, state):
        ''' Predict the action given raw state. A naive rule. Choose the color
            that appears least in the hand from legal actions. Try to keep wild
            cards as long as it can.

        Args:
            state (dict): Raw state from the game

        Returns:
            action (str): Predicted action
        '''
        print('-------------------')
        print('Target: ', state['target'])
        print('Hand: ', state['hand'])
        print('Actions: ', state['legal_actions'])
        legal_actions = state['legal_actions']
        hand = self.filter_wild(state['hand'])

        min_color_num = 0
        min_index = 0
        for i, action in enumerate(legal_actions):
            color_num = self.count_color(action, hand)
            if color_num < min_color_num:
                min_color_num = color_num
                min_index = i
        
        action = legal_actions[min_index]

        return action

    def eval_step(self, state):
        ''' Step for evaluation. The same to step
        '''
        return self.step(state)

    @staticmethod
    def filter_wild(hand):
        ''' Filter the wild cards. If all are wild cards, we do not filter

        Args:
            hand (list): A list of UNO card string

        Returns:
            filtered_hand (list): A filtered list of UNO string
        '''
        filtered_hand = []
        for card in hand:
            if not card[2:6] == 'wild':
                filtered_hand.append(card)

        if len(filtered_hand) == 0:
            filtered_hand = hand

        return filtered_hand

    @staticmethod
    def count_color(card, hand):
        ''' Count the number of cards in hand that have same color as the card

        Args:
            card (str): A UNO card string
            hand (list): A list of UNO card string

        Returns:
            color_num (int): The number cards that have the same color
        '''
        color = card[0]
        color_num = 0
        for c in hand:
            if c[0] == color:
                color_num += 1

        return color_num

class UNORuleModelV1(Model):
    ''' UNO Rule Model version 1
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        env = rlcard.make('uno')

        rule_agent = UNORuleAgentV1()
        self.rule_agents = [rule_agent for _ in range(env.player_num)]

    @property
    def agents(self):
        ''' Get a list of agents for each position in a the game

        Returns:
            agents (list): A list of agents

        Note: Each agent should be just like RL agent with step and eval_step
              functioning well.
        '''
        return self.rule_agents
    
    @property
    def use_raw(self):
        ''' Indicate whether use raw state and action

        Returns:
            use_raw (boolean): True if using raw state and action
        '''
        return True



