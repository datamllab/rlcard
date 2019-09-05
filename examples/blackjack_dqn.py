# Example of using doudizhu environment
import rlcard
from rlcard.agents.dqn_agent import DQNAgent
import tensorflow as tf

# make environment
env = rlcard.make('blackjack')

evaluate_every = 100
evaluate_num = 1000
episode_num = 1000000

with tf.Session() as sess:
    # set agents
    agent_0 = DQNAgent(sess)
    env.set_agents([agent_0])

    # seed everything
    #env.set_seed(0)
    #agent_0.set_seed(0)

    for episode in range(episode_num):

        # generate data from the environment
        trajectories, _ = env.run(is_testing=False)

        # Feed transitions into agent and update the agent
        for ts in trajectories[0]:
            is_training = agent_0.feed(ts)

        if is_training and (episode+1) % evaluate_every == 0:
            reward = 0
            print('\n')
            for eval_episode in range(evaluate_num):
                _, payoffs = env.run(is_testing=True)
                reward += payoffs[0]

            print('INFO - Average rewards is {}'.format(float(reward)/evaluate_num))

            










