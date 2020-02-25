''' Leduc Hold 'em rule model
'''
import rlcard
from rlcard.models.model import Model
from rlcard.games.leducholdem.game import LeducholdemGame

class LeducholdemRuleAgentV1(object):
    ''' Leduc Hold 'em Rule agent version 1
    '''

    def __init__(self):
        self.use_raw = True

    def step(self, state):
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
        '''
        When having only 2 hand cards at the game start, choose fold to drop terrible cards:
        Acceptable hand cards:
        Pairs
        AK, AQ, AJ, AT
        A9s, A8s, ... A2s(s means flush)
        KQ, KJ, QJ, JT
        Fold all hand types except those mentioned above to save money
        '''
        if 'raise' in legal_actions:
            return 'raise'
        if 'call' in legal_actions:
            return 'call'
        if 'check' in legal_actions:
            return 'check'
        else:
            return 'fold'

    def step2(self, state):
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
        '''
        When having only 2 hand cards at the game start, choose fold to drop terrible cards:
        Acceptable hand cards:
        Pairs
        AK, AQ, AJ, AT
        A9s, A8s, ... A2s(s means flush)
        KQ, KJ, QJ, JT
        Fold all hand types except those mentioned above to save money
        '''
        #if len(public_cards) == 0:
        if public_card == None:
            if hand[0] == 'K':
                action = 'raise'
            elif hand[0] == 'Q':
                action = 'check'
            else:
                action = 'fold'
        if public_card != None:
            if public_cards[1] == hand[1]:
                action = 'raise'
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

    def eval_step(self, state):
        ''' Step for evaluation. The same to step
        '''
        return self.step(state), []

class LeducholdemRuleModelV1(Model):
    ''' Leduc holdem Rule Model version 1
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        env = rlcard.make('leduc-holdem')
        rule_agent = LeducholdemRuleAgentV1()
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
