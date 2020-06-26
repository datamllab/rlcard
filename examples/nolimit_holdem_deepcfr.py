''' An example of learning a DeepCFR Agent on No-Limit Texas Holdem
'''

import tensorflow as tf
import os

import rlcard
from rlcard.agents import DeepCFR
from rlcard.agents import RandomAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

# Make environment
env = rlcard.make('no-limit-holdem', config={'seed': 0, 'allow_step_back':True})
eval_env = rlcard.make('no-limit-holdem', config={'seed': 0})

# Set the iterations numbers and how frequently we evaluate the performance
evaluate_every = 1
evaluate_num = 100
episode_num = 100000

# The intial memory size
memory_init_size = 1000

# Train the agent every X steps
train_every = 64

# The paths for saving the logs and learning curves
log_dir = './experiments/nolimit_holdem_deepcfr_result/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:

    # Initialize a global step
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # Set up the agents
    agents = []
    for i in range(env.player_num):
        agent = DeepCFR(sess, scope='deepcfr'+str(i), env=env)
        agents.append(agent)
    random_agent = RandomAgent(action_num=eval_env.action_num)

    env.set_agents(agents)
    eval_env.set_agents([agents[0], random_agent])

    # Initialize global variables
    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)

    for episode in range(episode_num):
        for agent in agents:
            agent.train()

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('DeepCFR')
    
    # Save model
    save_dir = 'models/nolimit_holdem_deepcfr'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(save_dir, 'model'))
    
