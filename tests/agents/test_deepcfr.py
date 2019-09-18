import unittest
import tensorflow as tf
import rlcard

from rlcard.agents.deep_cfr import *

class TestUtilsMethos(unittest.TestCase):

    def test_init(self):

        sess = tf.InteractiveSession()
        env = rlcard.make('blackjack')
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


if __name__ == '__main__':
    unittest.main()
