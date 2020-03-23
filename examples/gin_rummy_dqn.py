'''
    File name: rlcard.examples.gin_rummy_dqn.py
    Author: William Hale
    Date created: 2/12/2020

    An example of learning a Deep-Q Agent on GinRummy
'''

import tensorflow as tf
import os

import rlcard

from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed, tournament
from rlcard.utils.logger import Logger

# Make environment
env = rlcard.make('gin-rummy')
eval_env = rlcard.make('gin-rummy')
env.game.settings.print_settings()

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
evaluate_num = 100  # mahjong_dqn has 1000
episode_num = 1000  # mahjong_dqn has 100000

# The initial memory size
memory_init_size = 1000

# Train the agent every X steps
train_every = 1

# The paths for saving the logs and learning curves
log_dir = './experiments/gin_rummy_dqn_result/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:
    # Set agents
    global_step = tf.Variable(0, name='global_step', trainable=False)
    agent = DQNAgent(sess,
                     scope='dqn',
                     action_num=env.action_num,
                     replay_memory_size=20000,
                     replay_memory_init_size=memory_init_size,
                     train_every=train_every,
                     state_shape=env.state_shape,
                     mlp_layers=[512, 512])

    random_agent = RandomAgent(action_num=eval_env.action_num)

    sess.run(tf.global_variables_initializer())

    env.set_agents([agent, random_agent])
    eval_env.set_agents([agent, random_agent])

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)

    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent
        for ts in trajectories[0]:
            agent.feed(ts)

        # extra logging
        if episode % evaluate_every == 0:
            reward = 0
            reward2 = 0
            for eval_episode in range(evaluate_num):
                _, payoffs = eval_env.run(is_training=False)
                reward += payoffs[0]
                reward2 += payoffs[1]
            logger.log("\n\n########## Evaluation {} ##########".format(episode))
            reward_text = "{}".format(float(reward)/evaluate_num)
            reward2_text = "{}".format(float(reward2)/evaluate_num)
            info = "Timestep: {} Average reward is {}, reward2 is {}".format(env.timestep, reward_text, reward2_text)
            logger.log(info)

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('DQN')

    # Save model
    save_dir = 'models/gin_rummy_dqn'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(save_dir, 'model'))
