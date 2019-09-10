import unittest
import tensorflow as tf

from rlcard.agents.dqn_agent import *

class TestUtilsMethos(unittest.TestCase):

    def test_init(self):

        agent = DQNAgent(sess=tf.Session(),
                         replay_memory_size=0,
                         replay_memory_init_size=0,
                         update_target_estimator_every=0,
                         discount_factor=0,
                         epsilon_start=0,
                         epsilon_end=0,
                         epsilon_decay_steps=0,
                         batch_size=0,
                         action_size=0,
                         state_shape=[1],
                         norm_step=0)

        self.assertEqual(agent.replay_memory_init_size, 0)
        self.assertEqual(agent.update_target_estimator_every, 0)
        self.assertEqual(agent.discount_factor, 0)
        self.assertEqual(agent.epsilon_decay_steps, 0)
        self.assertEqual(agent.batch_size, 0)
        self.assertEqual(agent.action_size, 0)
        self.assertEqual(agent.norm_step, 0)

