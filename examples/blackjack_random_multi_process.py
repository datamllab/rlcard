''' An example of playing Blackjack with random agents with multiple processes
Note that we must use if __name__ == '__main__' for multiprocessing
'''

import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import set_global_seed

def main():
    # Make environment
    env = rlcard.make('blackjack', config={'seed': 0, 'env_num': 4})
    iterations = 1

    # Set a global seed
    set_global_seed(0)

    # Set up agents
    agent = RandomAgent(action_num=env.action_num)
    env.set_agents([agent])

    for it in range(iterations):

        # Generate data from the environment
        trajectories, payoffs = env.run(is_training=False)

        # Print out the trajectories
        print('\nIteration {}'.format(it))
        for ts in trajectories[0]:
            print('State: {}, Action: {}, Reward: {}, Next State: {}, Done: {}'.format(ts[0], ts[1], ts[2], ts[3], ts[4]))

if __name__ == '__main__':
    main()
