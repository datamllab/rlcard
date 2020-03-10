''' An example of loading a pre-trained NFSP model on Leduc Hold'em
'''
import tensorflow as tf
import os

import rlcard
from rlcard.agents.nfsp_agent import NFSPAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed, tournament

# Make environment
env = rlcard.make('leduc-holdem')

# Set a global seed
set_global_seed(0)

# Load pretrained model
graph = tf.Graph()
sess = tf.Session(graph=graph)

with graph.as_default():
    nfsp_agents = []
    for i in range(env.player_num):
        agent = NFSPAgent(sess,
                          scope='nfsp' + str(i),
                          action_num=env.action_num,
                          state_shape=env.state_shape,
                          hidden_layers_sizes=[128,128],
                          q_mlp_layers=[128,128])
        nfsp_agents.append(agent)

# We have a pretrained model here. Change the path for your model.
check_point_path = os.path.join(rlcard.__path__[0], 'models/pretrained/leduc_holdem_nfsp')

with sess.as_default():
    with graph.as_default():
        saver = tf.train.Saver()
        saver.restore(sess, tf.train.latest_checkpoint(check_point_path))

# Evaluate the performance. Play with random agents.
evaluate_num = 10000
random_agent = RandomAgent(env.action_num)
env.set_agents([nfsp_agents[0], random_agent])
reward = tournament(env, evaluate_num)[0]
print('Average reward against random agent: ', reward)

