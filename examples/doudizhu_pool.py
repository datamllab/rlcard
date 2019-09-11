""" A toy example of playing Doudizhu with random agents in multi processes
"""
import time
import random
import multiprocessing
import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed

if __name__ == '__main__':
    start = time.time()
    # Avoid RuntimeError
    multiprocessing.freeze_support()

    # Initialize process pool
    pool = multiprocessing.Pool()

    # Make environment
    env = rlcard.make('doudizhu')
    episode_num = 1000

    # Set global seed
    set_global_seed(1)

    # Set up agents
    agent_0 = RandomAgent(action_num=env.action_num)
    agent_1 = RandomAgent(action_num=env.action_num)
    agent_2 = RandomAgent(action_num=env.action_num)
    env.set_agents([agent_0, agent_1, agent_2])

    trajectories_set = []
    for episode in range(episode_num):

        # Generate data from the environment
        result = pool.apply_async(env.run, args=(False, random.random()))
        trajectories_set.append(result)
    for result in trajectories_set:
        trajectories, player_wins = result.get()
        # print(trajectories, player_wins)
    end = time.time()
    pool.close()
    pool.join()
    print('run time:', end-start)
