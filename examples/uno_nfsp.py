''' An example of learning a NFSP Agent on Dou Dizhu
'''

import tensorflow as tf

import rlcard
from rlcard.agents.nfsp_agent import NFSPAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed
from rlcard.utils.logger import Logger

# Make environment
env = rlcard.make('uno')
eval_env = rlcard.make('uno')

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
save_plot_every = 1000
evaluate_num = 10000
episode_num = 10000000

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 1000
norm_step = 1000

# The paths for saving the logs and learning curves
root_path = './experiments/uno_nfsp_result/'
log_path = root_path + 'log.txt'
csv_path = root_path + 'performance.csv'
figure_path = root_path + 'figures/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:
    # Set agents
    global_step = tf.Variable(0, name='global_step', trainable=False)
    agents = []
    for i in range(env.player_num):
        agent = NFSPAgent(sess,
                          scope='nfsp' + str(i),
                          action_num=env.action_num,
                          state_shape=env.state_shape,
                          hidden_layers_sizes=[512,1024,2048,1024,512],
                          anticipatory_param=0.5,
                          batch_size=256,
                          rl_learning_rate=0.00005,
                          sl_learning_rate=0.00001,
                          min_buffer_size_to_learn=memory_init_size,
                          q_replay_memory_size=int(1e5),
                          q_replay_memory_init_size=memory_init_size,
                          q_norm_step=norm_step,
                          q_batch_size=256,
                          q_mlp_layers=[512,1024,2048,1024,512])
        agents.append(agent)

    sess.run(tf.global_variables_initializer())

    random_agent = RandomAgent(action_num=eval_env.action_num)

    env.set_agents(agents)
    eval_env.set_agents([agents[0], random_agent, random_agent])

    # Count the number of steps
    step_counters = [0 for _ in range(env.player_num)]

    # Init a Logger to plot the learning curve
    logger = Logger(xlabel='timestep', ylabel='reward', legend='NFSP on UNO', log_path=log_path, csv_path=csv_path)

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
                if train_count > 0 and train_count % 128 == 0:
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
            logger.log('Timestep: {} Average reward is {}'.format(env.timestep, float(reward)/evaluate_num))

            # Add point to logger
            logger.add_point(x=env.timestep, y=float(reward)/evaluate_num)

        # Make plot
        if episode % save_plot_every == 0 and episode > 0:
            logger.make_plot(save_path=figure_path+str(episode)+'.png')

    # Make the final plot
    logger.make_plot(save_path=figure_path+'final_'+str(episode)+'.png')
