''' Leduc Hold 'em rule model
'''
import rlcard
from rlcard.models.model import Model

class LeducHoldemRuleAgentV1(object):
    ''' Leduc Hold 'em Rule agent version 1
    '''
    def __init__(self):
        self.use_raw = True

    @staticmethod
    def step(state):
        ''' Predict the action when given raw state. A simple rule-based AI.
        Args:
            state (dict): Raw state from the game

        Returns:
            action (str): Predicted action
        '''
        legal_actions = state['raw_legal_actions']
        # Aggressively play 'raise' and 'call'
        if 'raise' in legal_actions:
            return 'raise'
        if 'call' in legal_actions:
            return 'call'
        if 'check' in legal_actions:
            return 'check'
        else:
            return 'fold'

    def eval_step(self, state):
        ''' Step for evaluation. The same to step
        '''
        return self.step(state), []

class LeducHoldemRuleAgentV2(object):
    ''' Leduc Hold 'em Rule agent version 2
    '''
    def __init__(self):
        self.use_raw = True

    @staticmethod
    def step(state):
        ''' Predict the action when given raw state. A simple rule-based AI.
        Args:
            state (dict): Raw state from the game

        Returns:
            action (str): Predicted action
        '''
        legal_actions = state['raw_legal_actions']
        state = state['raw_obs']
        hand = state['hand']
        public_card = state['public_card']
        action = 'fold'
        # When having only 2 hand cards at the game start, choose fold to drop terrible cards:
        # Acceptable hand cards:
        # Pairs
        # AK, AQ, AJ, AT
        # A9s, A8s, ... A2s(s means flush)
        # KQ, KJ, QJ, JT
        # Fold all hand types except those mentioned above to save money
        if public_card:
            if public_card[1] == hand[1]:
                action = 'raise'
            else:
                action = 'fold'
        else:
            if hand[0] == 'K':
                action = 'raise'
            elif hand[0] == 'Q':
                action = 'check'
            else:
                action = 'fold'

        #return action
        if action in legal_actions:
            return action
        else:
            if action == 'raise':
                return 'call'
            if action == 'check':
                return 'fold'
            if action == 'call':
                return 'raise'
            else:
                return action

class LeducHoldemRuleModelV1(Model):
    ''' Leduc holdem Rule Model version 1
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        env = rlcard.make('leduc-holdem')
        rule_agent = LeducHoldemRuleAgentV1()
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

class LeducHoldemRuleModelV2(Model):
    ''' Leduc holdem Rule Model version 2
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        env = rlcard.make('leduc-holdem')
        rule_agent = LeducHoldemRuleAgentV2()
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
