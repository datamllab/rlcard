''' An example of learning a NFSP Agent on GinRummy
'''

import tensorflow as tf

import rlcard
from rlcard.agents.nfsp_agent import NFSPAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed, tournament
from rlcard.utils.logger import Logger

from rlcard.games.gin_rummy.agents import HighLowAgent

# Make environment
env = rlcard.make('gin-rummy')
eval_env = rlcard.make('gin-rummy')

# adjust game settings
choice = 1  # Please select a choice
for e in [env, eval_env]:
    if choice == 0:
        e.game.settings.set_gin_rummy()  # default choice
    elif choice == 1:
        e.game.settings.set_high_low()  # first choice
        e.game.settings.max_drawn_card_count = 10  # 200218 Note: this
    elif choice == 2:
        e.game.settings.set_simple_gin_rummy()  # second choice
    if e == env:
        e.game.settings.print_settings()
    # set scorer
    e.set_scorer(printing_configuration=(e == env))


# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 10000
evaluate_num = 10000
episode_num = 200000

# The intial memory size
memory_init_size = 1000

# Train the agent every X steps
train_every = 64

# The paths for saving the logs and learning curves
log_dir = './experiments/leduc_holdem_nfsp_result/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:
    # Initialize a global step
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # Set agents
    agents = []
    for i in range(env.player_num):
        agent = NFSPAgent(sess,
                          scope='nfsp' + str(i),
                          action_num=env.action_num,
                          state_shape=env.state_shape,
                          hidden_layers_sizes=[128,128],
                          min_buffer_size_to_learn=memory_init_size,
                          q_replay_memory_init_size=memory_init_size,
                          train_every = train_every,
                          q_train_every=train_every,
                          q_mlp_layers=[128,128])
        agents.append(agent)
    random_agent = RandomAgent(action_num=eval_env.action_num)
    #if env.game.settings.scorer_name == "HighLowScorer":  # 200218 Note this
    #    random_agent = HighLowAgent(action_num=eval_env.action_num)

    env.set_agents(agents)
    eval_env.set_agents([agents[0], random_agent])

    # Initialize global variables
    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)

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

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('NFSP')
    
    # Save model
    save_dir = 'models/gin_rummy_nfsp'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(save_dir, 'model'))
    
