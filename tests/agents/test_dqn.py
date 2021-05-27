import unittest
import torch
import numpy as np

from rlcard.agents.dqn_agent import DQNAgent

class TestDQN(unittest.TestCase):

    def test_init(self):

        agent = DQNAgent(replay_memory_size=0,
                         replay_memory_init_size=0,
                         update_target_estimator_every=0,
                         discount_factor=0,
                         epsilon_start=0,
                         epsilon_end=0,
                         epsilon_decay_steps=0,
                         batch_size=0,
                         num_actions=2,
                         state_shape=[1],
                         mlp_layers=[10,10],
                         device=torch.device('cpu'))

        self.assertEqual(agent.replay_memory_init_size, 0)
        self.assertEqual(agent.update_target_estimator_every, 0)
        self.assertEqual(agent.discount_factor, 0)
        self.assertEqual(agent.epsilon_decay_steps, 0)
        self.assertEqual(agent.batch_size, 0)
        self.assertEqual(agent.num_actions, 2)

    def test_train(self):

        memory_init_size = 100
        num_steps = 500

        agent = DQNAgent(replay_memory_size = 200,
                         replay_memory_init_size=memory_init_size,
                         update_target_estimator_every=100,
                         state_shape=[2],
                         mlp_layers=[10,10],
                         device=torch.device('cpu'))

        predicted_action, _ = agent.eval_step({'obs': np.random.random_sample((2,)), 'legal_actions': {0: None, 1: None}, 'raw_legal_actions': ['call', 'raise']})
        self.assertGreaterEqual(predicted_action, 0)
        self.assertLessEqual(predicted_action, 1)

        for _ in range(num_steps):
            ts = [{'obs': np.random.random_sample((2,)), 'legal_actions': {0: None, 1: None}}, np.random.randint(2), 0, {'obs': np.random.random_sample((2,)), 'legal_actions': {0: None, 1: None}, 'raw_legal_actions': ['call', 'raise']}, True]
            agent.feed(ts)

        predicted_action = agent.step({'obs': np.random.random_sample((2,)), 'legal_actions': {0: None, 1: None}})
        self.assertGreaterEqual(predicted_action, 0)
        self.assertLessEqual(predicted_action, 1)
