""" A toy example of playing Doudizhu with random agents
"""
# Example of using doudizhu environment
import rlcard
from rlcard.utils.utils import set_global_seed
from rlcard.agents.random_agent import RandomAgent

# Make environment
env = rlcard.make('doudizhu')
episode_num = 10

# Set global seed to 0
set_global_seed(0)

# Set up agents
action_num = env.action_num
agent_0 = RandomAgent(action_num)
agent_1 = RandomAgent(action_num)
agent_2 = RandomAgent(action_num)
env.set_agents([agent_0, agent_1, agent_2])

for episode in range(episode_num):

    # Generate data from the environment
    trajectories, player_wins = env.run(False)
    print(trajectories)
    print(player_wins)
