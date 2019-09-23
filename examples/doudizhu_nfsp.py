''' A toy example of learning a NFSP Agent on Limit Texas Holdem
'''

import tensorflow as tf

import rlcard
from rlcard.agents.nfsp_agent import NFSPAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed

from rlcard.utils.logger import Logger

# Make environment
env = rlcard.make('doudizhu')
eval_env = rlcard.make('doudizhu')

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 1000
save_plot_every = 10000
evaluate_num = 200
episode_num = 10000000

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 1000
norm_step = 1000

# Set a global seed
set_global_seed(100)

with tf.Session() as sess:
    # Set agents
    global_step = tf.Variable(0, name='global_step', trainable=False)
    agents = []
    for i in range(env.player_num):
        agent = NFSPAgent(sess,
                          scope='nfsp' + str(i),
                          action_num=env.action_num,
                          state_shape=[6, 5, 15],
                          hidden_layers_sizes=[512,512],
                          min_buffer_size_to_learn=memory_init_size,
                          q_replay_memory_init_size=memory_init_size,
                          q_norm_step=norm_step,
                          q_mlp_layers=[512,512])
        agents.append(agent)

    sess.run(tf.global_variables_initializer())

    random_agent = RandomAgent(action_num=eval_env.action_num)

    env.set_agents(agents)
    eval_env.set_agents([agents[0], random_agent, random_agent])

    # Count the number of steps
    step_counters = [0 for _ in range(env.player_num)]

    # Init a Logger to plot the learning curve
    logger = Logger(xlabel='eposide', ylabel='reward', legend='NFSP on Dou Dizhu', log_path='./experiments/limit_holdem_nfsp_result/log.txt', csv_path='./experiments/limit_holdem_nfsp_result/performance.csv')

    for episode in range(episode_num):

        # First sample a policy for the episode
        for agent in agents:
            agent.sample_episode_policy()

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent
        for i in range(env.player_num):
            for ts in trajectories[i]:
                agents[i].feed(ts)
                step_counters[i] += 1

                # Train the agent
                train_count = step_counters[i] - (memory_init_size + norm_step)
                if train_count > 0 and train_count % 64 == 0:
                    rl_loss = agents[i].train_rl()
                    sl_loss = agents[i].train_sl()
                    print('\rINFO - Agent {}, step {}, rl-loss: {}, sl-loss: {}'.format(i, step_counters[i], rl_loss, sl_loss), end='')

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            reward = 0
            eval_episode = 0
            for eval_episode in range(evaluate_num):
                _, payoffs = eval_env.run(is_training=False)
                reward += payoffs[0]

            logger.log('\n########## Evaluation ##########')
            logger.log('Average reward is {}'.format(float(reward)/evaluate_num))

            # Add point to logger
            logger.add_point(x=episode, y=float(reward)/evaluate_num)

        # Make plot
        if episode % save_plot_every == 0 and episode > 0:
            logger.make_plot(save_path='./experiments/limit_holdem_nfsp_result/'+str(episode)+'.png')

    # Make the final plot
    logger.make_plot(save_path='./experiments/limit_holdem_nfsp_result/'+'final_'+str(episode)+'.png')
