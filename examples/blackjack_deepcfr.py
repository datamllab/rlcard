"""
A toy example of learning a Deep-Q Agent on Blackjack
"""

import rlcard
from rlcard.agents.deep_cfr import DeepCFR
from rlcard.utils.utils import *
import tensorflow as tf

# make environment
set_global_seed(0)
evaluate_every = 1
evaluate_num = 1000
num_iteration = 50
i = 0
rewards = 0
train_env = rlcard.make('blackjack')
test_env = rlcard.make('blackjack')
with tf.Session() as sess:
    deep_cfr = DeepCFR(sess,
                train_env, 
                policy_network_layers=(64,64),
                advantage_network_layers=(32,32),
                num_traversals=2,
                num_step=300,
                learning_rate=5e-5,
                batch_size_advantage=32,
                batch_size_strategy=32,
                memory_capacity=1e3)

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

            print(train_env.timestep, test_env.timestep)
            print('############## Iteration '+str(i)+' #################')
            print('Reward: ', float(rewards)/evaluate_num)
            print('Advantage Loss: ', adv_loss)
            print('Policy Loss: ', policy_loss)
