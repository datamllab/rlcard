''' A toy example of playing Doudizhu with random agents in multi processes pool
'''

import time
import multiprocessing
import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed

if __name__ == '__main__':
    # Timer start
    start = time.time()

    # Avoid RuntimeError
    multiprocessing.freeze_support()

    # Set the number of process
    process_num = 8

    # Initialize process pool
    pool = multiprocessing.Pool(process_num)

    # Set game and make environment
    env = rlcard.make('doudizhu')

    # Set episode_num
    episode_num = 10000

    # Set global seed
    set_global_seed(1)

    # Set up agents
    agent_num = env.game.num_players
    env.set_agents([RandomAgent(action_num=env.action_num)
                    for _ in range(agent_num)])

    # Run game
    trajectories_set = []
    for episode in range(episode_num):

        # Generate data from the environment
        result = pool.apply_async(env.run, args=(False, np.random.randint(10000000)))
        trajectories_set.append(result)
    for result in trajectories_set:
        trajectories, player_wins = result.get()
        # print(trajectories, player_wins)
    end = time.time()
    pool.close()
    pool.join()
    print('run time:', end-start)
