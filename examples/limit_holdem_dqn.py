''' A toy example of learning a Deep-Q Agent on Dou Dizhu
'''

import tensorflow as tf

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed
from rlcard.utils.logger import Logger

# Make environment
env = rlcard.make('limit-holdem')
eval_env = rlcard.make('limit-holdem')

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 200
save_plot_every = 5000
evaluate_num = 200
episode_num = 1000000

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 1000
norm_step = 100

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:
    # Set agents
    agent = DQNAgent(sess,
                       action_num=env.action_num,
                       replay_memory_size=20000,
                       replay_memory_init_size=memory_init_size,
                       norm_step=norm_step,
                       state_shape=[52],
                       mlp_layers=[512, 512])

    random_agent = RandomAgent(action_num=eval_env.action_num)

    env.set_agents([agent, random_agent])
    eval_env.set_agents([agent, random_agent])

    # Count the number of steps
    step_counter = 0

    # Init a Logger to plot the learning curve
    logger = Logger(xlabel='eposide', ylabel='reward', legend='DQN on Dou Dizhu', log_path='./experiments/limitholdem_dqn_result/log.txt', csv_path='./experiments/limitholdem_dqn_result/performance.csv')

    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent
        for ts in trajectories[0]:
            agent.feed(ts)
            step_counter += 1

            # Train the agent
            if step_counter > memory_init_size + norm_step:
                loss = agent.train()
                print('\rINFO - Step {}, loss: {}'.format(step_counter, loss), end='')

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            reward = 0
            for eval_episode in range(evaluate_num):
                _, payoffs = eval_env.run(is_training=False)
                reward += payoffs[0]

            logger.log('\n########## Evaluation ##########')
            logger.log('Average reward is {}'.format(float(reward)/evaluate_num))

            # Add point to logger
            logger.add_point(x=episode, y=float(reward)/evaluate_num)

        # Make plot
        if episode % save_plot_every == 0 and episode > 0:
            logger.make_plot(save_path='./experiments/limitholdem_dqn_result/'+str(episode)+'.png')

    # Make the final plot
    logger.make_plot(save_path='./experiments/limitholdem_dqn_result/'+'final_'+str(episode)+'.png')
