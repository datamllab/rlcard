''' An example of solve Leduc Hold'em with CFR
'''
import numpy as np

import rlcard
from rlcard.agents.cfr_agent import CFRAgent
from rlcard import models
from rlcard.utils.utils import set_global_seed
from rlcard.utils.logger import Logger

# Make environment and enable human mode
env = rlcard.make('leduc-holdem', allow_step_back=True)
eval_env = rlcard.make('leduc-holdem')

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
save_plot_every = 1000
evaluate_num = 10000
episode_num = 10000000

# The paths for saving the logs and learning curves
root_path = './experiments/leduc_holdem_cfr_result/'
log_path = root_path + 'log.txt'
csv_path = root_path + 'performance.csv'
figure_path = root_path + 'figures/'

# Set a global seed
set_global_seed(0)

# Initilize CFR Agent
agent = CFRAgent(env)

# Evaluate CFR against pre-trained NFSP
eval_env.set_agents([agent, models.load('leduc-holdem-nfsp').agents[0]])

# Init a Logger to plot the learning curve
logger = Logger(xlabel='iteration', ylabel='reward', legend='CFR on Leduc Holdem', log_path=log_path, csv_path=csv_path)

for episode in range(episode_num):
    agent.train()
    print('\rIteration {}'.format(episode), end='')
    # Evaluate the performance. Play with NFSP agents.
    if episode % evaluate_every == 0:
        reward = 0
        for eval_episode in range(evaluate_num):
            _, payoffs = eval_env.run(is_training=False)

            reward += payoffs[0]

        logger.log('\n########## Evaluation ##########')
        logger.log('Iteration: {} Average reward is {}'.format(episode, float(reward)/evaluate_num))

        # Add point to logger
        logger.add_point(x=env.timestep, y=float(reward)/evaluate_num)

    # Make plot
    if episode % save_plot_every == 0 and episode > 0:
        logger.make_plot(save_path=figure_path+str(episode)+'.png')

# Make the final plot
logger.make_plot(save_path=figure_path+'final_'+str(episode)+'.png')

