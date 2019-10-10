import unittest
import tensorflow as tf

from rlcard.agents.nfsp_agent import *

class TestNFSP(unittest.TestCase):

    def test_init(self):

        sess = tf.InteractiveSession()
        tf.Variable(0, name='global_step', trainable=False)

        agent = NFSPAgent(sess=sess,
                         scope='nfsp',
                         action_num=10,
                         state_shape=[10],
                         hidden_layers_sizes=[10,10],
                         q_mlp_layers=[10,10])

        self.assertEqual(agent._action_num, 10)

        sess.close()
        tf.reset_default_graph()

    def test_train(self):

        norm_step = 100
        memory_init_size = 20
        step_num = 1000

        sess = tf.InteractiveSession()
        tf.Variable(0, name='global_step', trainable=False)
        agent = NFSPAgent(sess=sess,
                         scope='nfsp',
                         action_num=2,
                         state_shape=[2],
                         hidden_layers_sizes=[10,10],
                         reservoir_buffer_capacity=50,
                         batch_size=4,
                         min_buffer_size_to_learn=memory_init_size,
                         q_replay_memory_size=50,
                         q_replay_memory_init_size=memory_init_size,
                         q_batch_size=4,
                         q_norm_step=norm_step,
                         q_mlp_layers=[10,10])
        sess.run(tf.global_variables_initializer())

        predicted_action = agent.eval_step({'obs': np.random.random_sample((2,)), 'legal_actions': [0, 1]})
        self.assertGreaterEqual(predicted_action, 0)
        self.assertLessEqual(predicted_action, 1)

        for step in range(step_num):
            agent.sample_episode_policy()
            predicted_action = agent.step({'obs': np.random.random_sample((2,)), 'legal_actions': [0, 1]})
            self.assertGreaterEqual(predicted_action, 0)
            self.assertLessEqual(predicted_action, 1)

            ts = [{'obs': np.random.random_sample((2,)), 'legal_actions': [0, 1]}, np.random.randint(2), 0, {'obs': np.random.random_sample((2,)), 'legal_actions': [0, 1]}, True]
            agent.feed(ts)
            if step > norm_step + memory_init_size:
                agent.train_rl()

            agent.train_sl()
        sess.close()
        tf.reset_default_graph()

    def test_reservoir_buffer(self):
        buff = ReservoirBuffer(10)
        for i in range(5):
            buff.add(i)

        sampled_data = buff.sample(3)
        self.assertEqual(len(sampled_data), 3)

        with self.assertRaises(ValueError):
            buff.sample(100)

        for i, element in enumerate(buff):
            self.assertEqual(i, element)

        self.assertEqual(len(buff), 5)

        buff.clear()
        self.assertEqual(len(buff), 0)
