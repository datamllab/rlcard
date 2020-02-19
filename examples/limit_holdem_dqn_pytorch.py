''' An example of learning a Deep-Q Agent on Texas Limit Holdem
'''
import torch

import rlcard
from rlcard.agents.dqn_agent_pytorch import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed, tournament
from rlcard.utils.logger import Logger

# Make environment
env = rlcard.make('limit-holdem')
eval_env = rlcard.make('limit-holdem')

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
save_plot_every = 1000
evaluate_num = 10000
episode_num = 1000000

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 1000
norm_step = 100

# The paths for saving the logs and learning curves
log_dir = './experiments/limit_holdem_dqn_result/'

# Set a global seed
set_global_seed(0)

agent = DQNAgent(scope='dqn',
                 action_num=env.action_num,
                 replay_memory_size=int(1e5),
                 replay_memory_init_size=memory_init_size,
                 norm_step=norm_step,
                 state_shape=env.state_shape,
                 mlp_layers=[512, 512],
                 device=torch.device('cpu'))

random_agent = RandomAgent(action_num=eval_env.action_num)

env.set_agents([agent, random_agent])
eval_env.set_agents([agent, random_agent])

# Count the number of steps
step_counter = 0

# Init a Logger to plot the learning curve
logger = Logger(log_dir)

for episode in range(episode_num):

    # Generate data from the environment
    trajectories, _ = env.run(is_training=True)

    # Feed transitions into agent memory, and train the agent
    for ts in trajectories[0]:
        agent.feed(ts)
        step_counter += 1

        # Train the agent
        train_count = step_counter - (memory_init_size + norm_step)
        if train_count > 0:
            loss = agent.train()
            print('\rINFO - Step {}, loss: {}'.format(step_counter, loss), end='')

    # Evaluate the performance. Play with random agents.
    if episode % evaluate_every == 0:
        logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

# Close files in the logger
logger.close_files()

# Plot the learning curve
logger.plot('DQN')
