""" A toy example of learning a Deep-Q Agent on Blackjack
"""

import tensorflow as tf

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.utils.utils import *
from rlcard.plotter import Plotter

# Make environment
env = rlcard.make('blackjack')

# Set the iterations numbers and how frequently we evaluate
evaluate_every = 100
save_plot_every = 10000
evaluate_num = 1000
episode_num = 1000000

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 100
norm_step = 100

# Set a global seed
set_global_seed(1)

with tf.Session() as sess:
    # Set agents
    agent = DQNAgent(sess,
                       action_size=env.action_num,
                       replay_memory_init_size=memory_init_size,
                       norm_step=norm_step,
                       mlp_layers=[10,10])
    env.set_agents([agent])

    # Count the number of steps
    step_counter = 0

    # Init Plotter
    plotter = Plotter(xlabel='eposide', ylabel='reward', legend='DQN on Blackjack')

    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent and update the agent
        for ts in trajectories[0]:
            agent.feed(ts)
            step_counter += 1

            # Train the agent
            if step_counter > memory_init_size + norm_step:
                agent.train()

        # Evaluate the performance
        if episode % evaluate_every == 0:
            reward = 0
            for eval_episode in range(evaluate_num):
                _, payoffs = env.run(is_training=False)
                reward += payoffs[0]

            print('\n########## Evaluation ##########')
            print('Average reward is {}'.format(float(reward)/evaluate_num))

            # Add point
            plotter.add_point(x=episode, y=reward)

        # Make plot
        if episode % save_plot_every == 0 and episode > 0:
            plotter.make_plot(save_path='./blackjack_dqn_result/'+str(episode)+'.png')
    
    # Make the final plot
    plotter.make_plot(save_path='./blackjack_dqn_result/'+'final_'+str(episode)+'.png')
