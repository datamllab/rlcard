""" A toy example of playing Doudizhu with random agents
"""

import rlcard
from rlcard.utils.utils import set_global_seed
from rlcard.agents.random_agent import RandomAgent

# Make environment
env = rlcard.make('doudizhu')
episode_num = 2

# Set a global seed
set_global_seed(1)

# Set up agents
agent = RandomAgent(action_num=env.action_num)
env.set_agents([agent, agent, agent])

for episode in range(episode_num):

    # Generate data from the environment
    trajectories, player_wins = env.run(is_training=False)
    print(trajectories)
    print(player_wins)
