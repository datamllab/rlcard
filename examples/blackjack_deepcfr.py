"""
A toy example of learning a Deep-Q Agent on Blackjack
"""

import rlcard
from rlcard.agents.deep_cfr import DeepCFR
from rlcard.utils.utils import *
import tensorflow as tf

# make environment
set_global_seed(0)
evaluate_every = 50
evaluate_num = 1000
num_iteration = 1000
i = 0
rewards = 0
train_env = rlcard.make('blackjack')
test_env = rlcard.make('blackjack')
with tf.Session() as sess:
    deep_cfr = DeepCFR(sess,
                train_env, 
                policy_network_layers=(32,32),
                advantage_network_layers=(32,32),
                num_traversals=40,
                num_step=40,
                learning_rate=1e-4,
                batch_size_advantage=32,
                batch_size_strategy=32,
                memory_capacity=1e7)

    for i in range(num_iteration):
        # Train the agent in training environment
        _, adv_loss, policy_loss = deep_cfr.train()

        # Evaluate the agent
        if i % evaluate_every == 0:
            rewards = 0
            for j in range(evaluate_num):
                state, player = test_env.init_game()
                while True:
                    action = deep_cfr.step(state)
                    state, player = test_env.step(action)
                    if test_env.is_over():
                        payoffs = test_env.get_payoffs()
                        rewards += payoffs[0]
                        break
            print('############## Iteration '+str(i)+' #################')
            print('Reward: ', float(rewards)/evaluate_num)
            print('Advantage Loss: ', adv_loss)
            print('Policy Loss: ', policy_loss)
