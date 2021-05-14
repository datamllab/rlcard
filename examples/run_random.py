''' An example of playing randomly in RLCard
'''
import argparse

import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import set_seed

def run(args):
    # Make environment
    env = rlcard.make(args.env, config={'seed': 42})
    num_episodes = 1

    # Seed numpy, torch, random
    set_seed(42)

    # Set agents
    agent = RandomAgent(num_actions=env.num_actions)
    env.set_agents([agent for _ in range(env.num_players)])

    for episode in range(num_episodes):

        # Generate data from the environment
        trajectories, player_wins = env.run(is_training=False)
        # Print out the trajectories
        print('\nEpisode {}'.format(episode))
        print(trajectories)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Random example in RLCard")
    parser.add_argument('--env', type=str, default='leduc-holdem')

    args = parser.parse_args()

    run(args)

