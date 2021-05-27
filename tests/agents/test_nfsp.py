import unittest
import torch
import numpy as np

from rlcard.agents.nfsp_agent import NFSPAgent

class TestNFSP(unittest.TestCase):

    def test_init(self):

        agent = NFSPAgent(num_actions=10,
                          state_shape=[10],
                          hidden_layers_sizes=[10,10],
                          q_mlp_layers=[10,10],
                          device=torch.device('cpu'))

        self.assertEqual(agent._num_actions, 10)

    def test_train(self):

        memory_init_size = 20
        num_steps = 1000

        agent = NFSPAgent(num_actions=2,
                          state_shape=[2],
                          hidden_layers_sizes=[10,10],
                          reservoir_buffer_capacity=50,
                          batch_size=4,
                          min_buffer_size_to_learn=memory_init_size,
                          q_replay_memory_size=50,
                          q_replay_memory_init_size=memory_init_size,
                          q_batch_size=4,
                          q_mlp_layers=[10,10],
                          device=torch.device('cpu'))

        predicted_action, _ = agent.eval_step({'obs': np.random.random_sample((2,)), 'legal_actions': {0: None, 1: None}, 'raw_legal_actions': ['call', 'raise']})
        self.assertGreaterEqual(predicted_action, 0)
        self.assertLessEqual(predicted_action, 1)

        for _ in range(num_steps):
            agent.sample_episode_policy()
            predicted_action = agent.step({'obs': np.random.random_sample((2,)), 'legal_actions': {0: None, 1: None}})
            self.assertGreaterEqual(predicted_action, 0)
            self.assertLessEqual(predicted_action, 1)

            ts = [{'obs': np.random.random_sample((2,)), 'legal_actions': {0: None, 1: None}}, np.random.randint(2), 0, {'obs': np.random.random_sample((2,)), 'legal_actions': {0: None, 1: None}, 'raw_legal_actions': ['call', 'raise']}, True]
            agent.feed(ts)
