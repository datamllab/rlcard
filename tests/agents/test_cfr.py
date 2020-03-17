import unittest
import numpy as np

import rlcard
from rlcard.agents.cfr_agent import CFRAgent

class TestNFSP(unittest.TestCase):

    def test_train(self):

        env = rlcard.make('leduc-holdem', config={'allow_step_back':True})
        agent = CFRAgent(env)

        for _ in range(100):
            agent.train()

        state = {'obs': np.array([1., 1., 0., 0., 0., 0.]), 'legal_actions': [0,2]}
        action, _ = agent.eval_step(state)

        self.assertIn(action, [0, 2])

    def test_save_and_load(self):
        env = rlcard.make('leduc-holdem', config={'allow_step_back':True})
        agent = CFRAgent(env)

        for _ in range(100):
            agent.train()

        agent.save()

        new_agent = CFRAgent(env)
        new_agent.load()
        self.assertEqual(len(agent.policy), len(new_agent.policy))
        self.assertEqual(len(agent.average_policy), len(new_agent.average_policy))
        self.assertEqual(len(agent.regrets), len(new_agent.regrets))
        self.assertEqual(agent.iteration, new_agent.iteration)

