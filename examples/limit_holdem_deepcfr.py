"""
A toy example of learning a Deep-Q Agent on Blackjack
"""

import rlcard
from rlcard.agents.deep_cfr import DeepCFR
from rlcard.utils.utils import *
import tensorflow as tf
import numpy as np

# make environment
set_global_seed(0)
evaluate_every = 10
evaluate_num = 10000
num_iteration = 1000
i = 0
rewards = 0
#train_env = rlcard.make('limit-holdem') 
#test_env = rlcard.make('limit-holdem') 
train_env = rlcard.make('leduc-holdem') 
test_env = rlcard.make('leduc-holdem') 
with tf.Session() as sess:
    deep_cfr = DeepCFR(sess,
                train_env,
                policy_network_layers=(1024, 1024),
                advantage_network_layers=(512, 512),
                num_traversals=3000,
                num_step=12800,
                learning_rate=1e-5,
                batch_size_advantage=64,
                batch_size_strategy=64,
                memory_capacity=1e5)

    for i in range(num_iteration):
        # Train the agent in training environment
        _, adv_loss, policy_loss = deep_cfr.train()

        # Evaluate the agent
        if i % evaluate_every == 0:
            rewards = 0
            for j in range(evaluate_num):
                state, player = test_env.init_game()
                while True:
                    action_prob = deep_cfr.action_probabilities(state['obs'])
                    action_prob /= action_prob.sum()
                    action = np.random.choice(np.arange(len(action_prob)), p=action_prob)
                    #action_prob = list(action_prob)
                    #action = action_prob.index(max(action_prob))
                    #print("Play:", state, action)
                    state, player = test_env.step(action)
                    if test_env.is_over():
                        payoffs = test_env.get_payoffs()
                        rewards += payoffs[0]
                        break
            print('############## Iteration '+str(i)+' #################')
            print('Reward: ', float(rewards)/evaluate_num)
            print('Advantage Loss: ', adv_loss)
            print('Policy Loss: ', policy_loss)
