''' A toy example of training single-agent algorithm on Leduc Hold'em
    The environment can be treated as normal OpenAI gym style single-agent environment
'''

import tensorflow as tf
import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.utils.utils import set_global_seed
from rlcard.utils.logger import Logger

# Make environment and enable single mode
env = rlcard.make('uno')
eval_env = rlcard.make('uno')
env.set_mode(single_agent_mode=True)
eval_env.set_mode(single_agent_mode=True)

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 1000
save_plot_every = 1000
evaluate_num = 10000
timesteps = 1000000

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 1000
norm_step = 100

# The paths for saving the logs and learning curves
root_path = './experiments/leduc_holdem_single_agent_dqn_result/'
log_path = root_path + 'log.txt'
csv_path = root_path + 'performance.csv'
figure_path = root_path + 'figures/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:
    global_step = tf.Variable(0, name='global_step', trainable=False)
    agent = DQNAgent(sess,
                     scope='dqn',
                     action_num=env.action_num,
                     replay_memory_size=int(1e5),
                     replay_memory_init_size=memory_init_size,
                     norm_step=norm_step,
                     state_shape=env.state_shape,
                     mlp_layers=[128, 128])

    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(xlabel='timestep', ylabel='reward', legend='DQN on Leduc Holdem', log_path=log_path, csv_path=csv_path)

    state = env.reset()

    for timestep in range(timesteps):
        action = agent.step(state)
        next_state, reward, done = env.step(action)
        ts = (state, action, reward, next_state, done)
        agent.feed(ts)

        train_count = timestep - (memory_init_size + norm_step)
        if train_count > 0:
            loss = agent.train()
            print('\rINFO - Step {}, loss: {}'.format(timestep, loss), end='')

        if timestep % evaluate_every == 0:
            rewards = []
            state = eval_env.reset()
            for _ in range(evaluate_num):
                action = agent.eval_step(state)
                _, reward, done = env.step(action)
                if done:
                    rewards.append(reward)
            logger.log('\n########## Evaluation ##########')
            logger.log('Timestep: {} Average reward is {}'.format(timestep, np.mean(rewards)))

            # Add point to logger
            logger.add_point(x=env.timestep, y=float(reward)/evaluate_num)

        # Make plot
        if timestep % save_plot_every == 0:
            logger.make_plot(save_path=figure_path+str(timestep)+'.png')

    # Make the final plot
    logger.make_plot(save_path=figure_path+'final_'+str(timestep)+'.png')
