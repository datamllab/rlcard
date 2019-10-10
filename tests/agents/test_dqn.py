import unittest
import tensorflow as tf

from rlcard.agents.dqn_agent import *

class TestDQN(unittest.TestCase):

    def test_init(self):

        sess = tf.InteractiveSession()
        tf.Variable(0, name='global_step', trainable=False)

        agent = DQNAgent(sess=sess,
                         scope='dqn',
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

        norm_step = 1100
        memory_init_size = 100
        step_num = 1500

        sess = tf.InteractiveSession()
        tf.Variable(0, name='global_step', trainable=False)
        agent = DQNAgent(sess=sess,
                         scope='dqn',
                         replay_memory_size = 500,
                         replay_memory_init_size=memory_init_size,
                         update_target_estimator_every=100,
                         norm_step=norm_step,
                         state_shape=[2],
                         mlp_layers=[10,10])
        sess.run(tf.global_variables_initializer())

        predicted_action = agent.eval_step({'obs': np.random.random_sample((2,)), 'legal_actions': [0, 1]})
        self.assertGreaterEqual(predicted_action, 0)
        self.assertLessEqual(predicted_action, 1)

        for step in range(step_num):
            ts = [{'obs': np.random.random_sample((2,)), 'legal_actions': [0, 1]}, np.random.randint(2), 0, {'obs': np.random.random_sample((2,)), 'legal_actions': [0, 1]}, True]
            agent.feed(ts)
            if step > norm_step + memory_init_size:
                agent.train()

        predicted_action = agent.step({'obs': np.random.random_sample((2,)), 'legal_actions': [0, 1]})
        self.assertGreaterEqual(predicted_action, 0)
        self.assertLessEqual(predicted_action, 1)

        sess.close()
        tf.reset_default_graph()
