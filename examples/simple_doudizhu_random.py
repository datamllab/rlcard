''' An example of playing Simple Doudizhu with random agents
'''

import rlcard
from rlcard.utils.utils import set_global_seed
from rlcard.agents.random_agent import RandomAgent

# Make environment
env = rlcard.make('simple-doudizhu')
episode_num = 2

# Set a global seed
set_global_seed(0)

# Set up agents
agent = RandomAgent(action_num=env.action_num)
env.set_agents([agent, agent, agent])

for episode in range(episode_num):

    # Generate data from the environment
    trajectories, player_wins = env.run(is_training=False)
    # Print out the trajectories
    print('\nEpisode {}'.format(episode))
    for ts in trajectories[0]:
        print('State: {}, Action: {}, Reward: {}, Next State: {}, Done: {}'.format(ts[0], ts[1], ts[2], ts[3], ts[4]))
