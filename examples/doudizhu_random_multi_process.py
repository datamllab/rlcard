import time
import multiprocessing

import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed, assign_task

if __name__ == '__main__':
    # Timer start
    start = time.time()

    # Avoid RuntimeError
    multiprocessing.freeze_support()

    # Set the number of process
    process_num = 8

    # Set episode_num
    episode_num = 10000

    # Assign tasks
    per_tasks = assign_task(episode_num, process_num)

    # Set game and make environment
    game = 'doudizhu'
    env = rlcard.make(game)

    # Set global seed
    set_global_seed(1)

    # Set up agents
    agent_num = env.player_num
    env.set_agents([RandomAgent(action_num=env.action_num)
                    for _ in range(agent_num)])

    # Set a global list to reserve trajectories
    manager = multiprocessing.Manager()
    trajectories_set = manager.list()

    # Generate Processes
    processes = []
    for p in range(process_num):
        process = multiprocessing.Process(target=env.run_multi, args=(per_tasks[p], trajectories_set))
        processes.append(process)

    # Run process
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    end = time.time()
    print('run time:', end-start)
