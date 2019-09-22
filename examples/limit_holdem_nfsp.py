''' A toy example of learning a NFSP Agent on Limit Texas Holdem
'''

import tensorflow as tf

import rlcard
from rlcard.agents.nfsp_agent import NFSPAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed
from rlcard.utils.logger import Logger

# Make environment
env = rlcard.make('limit-holdem')
eval_env = rlcard.make('limit-holdem')

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 1000
save_plot_every = 10000
evaluate_num = 10000
episode_num = 10000000

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 1000
norm_step = 100

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:
    # Set agents
    agent = NFSPAgent(sess,
                      action_num=env.action_num,
                      state_shape=[52],
                      min_buffer_size_to_learn=memory_init_size,
                      q_replay_memory_init_size=memory_init_size,
                      q_norm_step=norm_step)

    random_agent = RandomAgent(action_num=eval_env.action_num)

    env.set_agents([agent, agent])
    eval_env.set_agents([agent, random_agent])

    # Count the number of steps
    step_counter = 0

    # Init a Logger to plot the learning curve
    logger = Logger(xlabel='eposide', ylabel='reward', legend='NFSP on Limit Texas Holdem', log_path='./experiments/limit_holdem_nfsp_result/log.txt', csv_path='./experiments/limit_holdem_nfsp_result/performance.csv')

    for episode in range(episode_num):
        
        # First sample a policy for the episode
        agent.sample_episode_policy()
        
        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent
        for ts in trajectories[0]:
            agent.feed(ts)
            step_counter += 1

            # Train the agent
            train_count = step_counter - (memory_init_size + norm_step) 
            if train_count > 0 and train_count % 128 == 0:
                for _ in range(2):
                    rl_loss = agent.train_rl()
                    sl_loss = agent.train_sl()
                    print('\rINFO - Step {}, rl-loss: {}, sl-loss: {}'.format(step_counter, rl_loss, sl_loss), end='')

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            reward = 0
            eval_episode = 0
            for eval_episode in range(evaluate_num):
                _, payoffs = eval_env.run(is_training=False)
                reward += payoffs[0]

            logger.log('\n########## Evaluation ##########')
            #logger.log('Average reward is {}'.format(float(reward)/evaluate_num))
            logger.log('Average reward is {}'.format(float(reward)/evaluate_num))

            # Add point to logger
            logger.add_point(x=episode, y=float(reward)/evaluate_num)

        # Make plot
        if episode % save_plot_every == 0 and episode > 0:
            logger.make_plot(save_path='./experiments/limit_holdem_nfsp_result/'+str(episode)+'.png')

    # Make the final plot
    logger.make_plot(save_path='./experiments/limit_holdem_nfsp_result/'+'final_'+str(episode)+'.png')
