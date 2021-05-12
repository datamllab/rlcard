''' An example of playing randomly in RLCard
'''
import argparse

import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import set_seed

def run(args):
    # Make environment
    env = rlcard.make(args.env, config={'seed': 42})
    episode_num = 1

    # Seed nmupy, torch, random
    set_seed(42)

    # Set agents
    agent = RandomAgent(action_num=env.action_num)
    env.set_agents([agent for _ in range(env.player_num)])

    for episode in range(episode_num):

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

