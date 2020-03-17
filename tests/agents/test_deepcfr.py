import unittest
import tensorflow as tf
import numpy as np
import rlcard

from rlcard.agents.deep_cfr_agent import DeepCFR, FixedSizeRingBuffer

class TestUtilsMethos(unittest.TestCase):

    def test_init(self):

        sess = tf.InteractiveSession()
        env = rlcard.make('leduc-holdem', config={'allow_step_back':True})
        agent = DeepCFR(session=sess,
                        env=env,
                        policy_network_layers=(4,4),
                        advantage_network_layers=(4,4),
                        num_traversals=1,
                        num_step=1,
                        learning_rate=1e-4,
                        batch_size_advantage=10,
                        batch_size_strategy=10,
                        memory_capacity=int(1e7))

        self.assertEqual(agent._num_traversals, 1)
        self.assertEqual(agent._num_step, 1)
        self.assertEqual(agent._batch_size_advantage, 10)
        self.assertEqual(agent._batch_size_strategy, 10)

        sess.close()
        tf.reset_default_graph()

    def test_train(self):

        num_iterations = 10

        sess = tf.InteractiveSession()
        env = rlcard.make('leduc-holdem', {'allow_step_back':True})
        agent = DeepCFR(session=sess,
                        env=env,
                        policy_network_layers=(128,128),
                        advantage_network_layers=(128,128),
                        num_traversals=1,
                        num_step=1,
                        learning_rate=1e-4,
                        batch_size_advantage=64,
                        batch_size_strategy=64,
                        memory_capacity=int(1e5))

        # Test train
        for _ in range(num_iterations):
            agent.train()

        # Test eval_step
        state = {'obs': np.random.random_sample(env.state_shape), 'legal_actions': [a for a in range(env.action_num)]}
        action, _ = agent.eval_step(state)
        self.assertIn(action, [a for a in range(env.action_num)])

        # Test simulate other
        action = agent.simulate_other(0, state)
        self.assertIn(action, [a for a in range(env.action_num)])

        # Test action advantage
        advantages = agent.action_advantage(state, 0)
        self.assertEqual(advantages.shape[0], env.action_num)

        sess.close()
        tf.reset_default_graph()

    def test_fixed_size_ring_buffer(self):
        buf = FixedSizeRingBuffer(10)

        # Test add data
        for i in range(50):
            buf.add(i)
        self.assertIn(49, buf._data)
        self.assertNotIn(1, buf._data)

        # Test sample
        self.assertEqual(len(buf.sample(3)), 3)
        with self.assertRaises(ValueError):
            buf.sample(100)

        # Test leagth
        self.assertEqual(len(buf), 10)

        # Test iteration
        for element in buf:
            self.assertIsInstance(element, int)

        # Test clear
        buf.clear()
        self.assertEqual(len(buf), 0)


if __name__ == '__main__':
    unittest.main()
