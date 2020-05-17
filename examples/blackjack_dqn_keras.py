''' An example of learning a Dqqp-Q Agent on Blackjack
'''

import tensorflow as tf
import os

import rlcard
#from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.dqn_agent_keras import DQNAgent

from rlcard.utils.utils import set_global_seed, tournament
from rlcard.utils.logger import Logger

# Make environment
env = rlcard.make('blackjack')
eval_env = rlcard.make('blackjack')

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
evaluate_num = 10000
episode_num = 100000

# The intial memory size
memory_init_size = 100

# Train the agent every X steps
train_every = 1

# The paths for saving the logs and learning curves
log_dir = './experiments/blackjack_dqn_keras_result/'

# Set a global seed
set_global_seed(0)


agent = DQNAgent(scope='dqn',
                 action_num=env.action_num,
                 replay_memory_init_size=memory_init_size,
                 train_every=train_every,
                 state_shape=env.state_shape,
                 mlp_layers=[10,10])
env.set_agents([agent])
eval_env.set_agents([agent])

# Init a Logger to plot the learning curve
logger = Logger(log_dir)

for episode in range(episode_num):
    # Generate data from the environment
    trajectories, _ = env.run(is_training=True)

    # Feed transitions into agent memory, and train the agent
    for ts in trajectories[0]:
        agent.feed(ts)

    # Evaluate the performance. Play with random agents.
    if episode % evaluate_every == 0:
        logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])


# Close files in the logger
logger.close_files()

# Plot the learning curve
logger.plot('DQN_Keras')

# Save model
save_dir = 'models/blackjack_dqn_keras'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
model_path = os.path.join(save_dir, 'model.keras')
agent.save_model(model_path)
print("model saved")
