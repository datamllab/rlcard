"""
A toy example of learning a Deep-Q Agent on Blackjack
"""

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.utils.utils import *
import tensorflow as tf

# Make environment
env = rlcard.make('blackjack')

# Set the iterations numbers and how frequently we evaluate
evaluate_every = 100
evaluate_num = 1000
episode_num = 1000000

# Set a gloabel seed
set_global_seed(0)

with tf.Session() as sess:
    # Set agents
    agent_0 = DQNAgent(sess, action_size=env.action_num)
    env.set_agents([agent_0])

    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent and update the agent
        for ts in trajectories[0]:
            is_training = agent_0.feed(ts)

        if is_training and (episode) % evaluate_every == 0:
            reward = 0
            for eval_episode in range(evaluate_num):
                _, payoffs = env.run()
                reward += payoffs[0]

            print('INFO - Average reward is {}'.format(float(reward)/evaluate_num))

            










