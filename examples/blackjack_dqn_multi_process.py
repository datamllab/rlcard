''' A toy example of learning a Deep-Q Agent on Blackjack
'''
import numpy as np
import tensorflow as tf
from multiprocessing import Process

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.utils.utils import set_global_seed
from rlcard.utils.logger import Logger

class Blackjack_Process(Process):

    def __init__(self, index, task_num):
        Process.__init__(self)
        self.task_num = task_num
        self.env = rlcard.make('blackjack')
        sess = tf.Session()
        agent = DQNAgent(sess,
                         scope='sub-dqn' + str(index),
                         action_num=env.action_num,
                         replay_memory_init_size=memory_init_size,
                         norm_step=norm_step,
                         state_shape=env.state_shape,
                         mlp_layers=[10, 10])
        self.env.set_agents([agent])
        sess.run(tf.global_variables_initializer())

    def run(self):
        for _ in range(self.task_num):
            trajectories, _ = self.env.run(is_training=True)
            print(trajectories)



# Make environment
env = rlcard.make('blackjack')
eval_env = rlcard.make('blackjack')

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
save_plot_every = 1000
evaluate_num = 10000
episode_num = 1000000

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 100
norm_step = 100

# The paths for saving the logs and learning curves
root_path = './experiments/blackjack_dqn_result/'
log_path = root_path + 'log.txt'
csv_path = root_path + 'performance.csv'
figure_path = root_path + 'figures/'

# Set a global seed
set_global_seed(0)

PROCESSES = [Blackjack_Process(index, 25) for index in range(4)]

with tf.Session() as sess:

    # Set agents
    global_step = tf.Variable(0, name='global_step', trainable=False)
    agent = DQNAgent(sess,
                     scope='dqn',
                     action_num=env.action_num,
                     replay_memory_init_size=memory_init_size,
                     norm_step=norm_step,
                     state_shape=env.state_shape,
                     mlp_layers=[10,10])
    env.set_agents([agent])
    eval_env.set_agents([agent])
    sess.run(tf.global_variables_initializer())

    # Count the number of steps
    step_counter = 0

    # Init a Logger to plot the learning curve
    logger = Logger(xlabel='timestep', ylabel='reward', legend='DQN on Blackjack', log_path=log_path, csv_path=csv_path)

    for episode in range(1):
        for p in PROCESSES:
            p.start()
        for p in PROCESSES:
            p.join()
        '''
        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train
        for ts in trajectories[0]:
            agent.feed(ts)
            step_counter += 1

            # Train the agent
            if step_counter > memory_init_size + norm_step:
                loss = agent.train()
                print('\rINFO - Step {}, loss: {}'.format(step_counter, loss), end='')

        # Evaluate the performance
        if episode % evaluate_every == 0:
            reward = 0
            for eval_episode in range(evaluate_num):
                _, payoffs = eval_env.run(is_training=False)
                reward += payoffs[0]

            logger.log('\n########## Evaluation ##########')
            logger.log('Timestep: {} Average reward is {}'.format(env.timestep, float(reward)/evaluate_num))

            # Add point to logger
            logger.add_point(x=env.timestep, y=float(reward)/evaluate_num)

        # Make plot
        if episode % save_plot_every == 0 and episode > 0:
            logger.make_plot(save_path=figure_path+str(episode)+'.png')

    # Make the final plot
    logger.make_plot(save_path=figure_path+'final_'+str(episode)+'.png')
    '''