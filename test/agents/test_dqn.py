import unittest
import tensorflow as tf

from rlcard.agents.dqn_agent import *

class TestUtilsMethos(unittest.TestCase):

    def test_init(self):

        sess = tf.InteractiveSession()

        agent = DQNAgent(sess=sess,
                         replay_memory_size=0,
                         replay_memory_init_size=0,
                         update_target_estimator_every=0,
                         discount_factor=0,
                         epsilon_start=0,
                         epsilon_end=0,
                         epsilon_decay_steps=0,
                         batch_size=0,
                         action_num=2,
                         state_shape=[1],
                         norm_step=0,
                         mlp_layers=[10,10])

        self.assertEqual(agent.replay_memory_init_size, 0)
        self.assertEqual(agent.update_target_estimator_every, 0)
        self.assertEqual(agent.discount_factor, 0)
        self.assertEqual(agent.epsilon_decay_steps, 0)
        self.assertEqual(agent.batch_size, 0)
        self.assertEqual(agent.action_num, 2)
        self.assertEqual(agent.norm_step, 0)

        sess.close()
        tf.reset_default_graph()

    def test_train(self):

        norm_step = 100
        memory_init_size = 100
        step_num = 300

        sess = tf.InteractiveSession()
        agent = DQNAgent(sess=sess,
                         replay_memory_init_size=memory_init_size,
                         update_target_estimator_every=10,
                         norm_step=norm_step,
                         state_shape=[2],
                         mlp_layers=[10,10])

        for step in range(step_num):
            ts = [np.random.random_sample((2,)), np.random.randint(2), 0, np.random.random_sample((2,)), True]
            agent.feed(ts)
            if step > norm_step + memory_init_size:
                agent.train()

        predicted_action = agent.eval_step(np.random.random_sample((2,)))
        self.assertGreaterEqual(predicted_action, 0)
        self.assertLessEqual(predicted_action, 1)

        self.assertGreaterEqual(predicted_action, 0)
        self.assertLessEqual(predicted_action, 1)

        sess.close()
        tf.reset_default_graph()
