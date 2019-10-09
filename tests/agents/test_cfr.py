import unittest
import numpy as np

import rlcard
from rlcard.agents.cfr_agent import *

class TestNFSP(unittest.TestCase):

    def test_train(self):

        env = rlcard.make('leduc-holdem', allow_step_back=True)
        agent = CFRAgent(env)

        for _ in range(100):
            agent.train()

        state = {'obs': np.array([1., 1., 0., 0., 0., 0.]), 'legal_actions': [0,2]}
        action = agent.eval_step(state)

        self.assertIn(action, [0, 2])
