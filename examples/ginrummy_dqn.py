''' An example of learning a Deep-Q Agent on GinRummy
'''

import tensorflow as tf

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed, tournament
from rlcard.utils.logger import Logger

from rlcard.games.gin_rummy.agents import HighLowAgent

from rlcard.games.gin_rummy.utils.scorers import HighLowScorer
from rlcard.games.gin_rummy.game import GinRummyGame
from rlcard.games.gin_rummy.player import GinRummyPlayer

# Make environment
env = rlcard.make('gin-rummy')
eval_env = rlcard.make('gin-rummy')

# adjust game settings and scorer
choice = 1  # Please select a choice or 0 for default
for e in [env, eval_env]:
    if choice == 0:
        e.game.settings.set_gin_rummy()  # default choice
    elif choice == 1:
        e.game.settings.set_high_low()  # first choice
        e.game.settings.max_drawn_card_count = 20  # 200218 Note: this
    elif choice == 2:
        e.game.settings.set_simple_gin_rummy()  # second choice
    if e == env:
        e.game.settings.print_settings()
    # set scorer
    e.set_scorer(printing_configuration=(e == env))
    choice_get_payoff = 2  # Please select a choice or 0 for default
    if choice_get_payoff == 1 and type(e.scorer) is HighLowScorer:
        def get_payoff_choice1(player: GinRummyPlayer, game: GinRummyGame) -> float:
            hand = player.hand
            deadwood_count = sum([10 if card.rank_id > 5 else 0 for card in hand])
            deadwood_count = min(100, deadwood_count)
            payoff = (100 - deadwood_count) / 100
            return payoff
        e.scorer.get_payoff = get_payoff_choice1
    elif choice_get_payoff == 2 and type(e.scorer) is HighLowScorer:
        def get_payoff_choice2(player: GinRummyPlayer, game: GinRummyGame) -> int:
            hand = player.hand
            max_rank_id = max([card.rank_id for card in hand])
            payoff = 1 if max_rank_id < 11 else 0
            return payoff
        e.scorer.get_payoff = get_payoff_choice2

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
evaluate_num = 10000
episode_num = 100000

# The intial memory size
memory_init_size = 1000

# Train the agent every X steps
train_every = 1

# The paths for saving the logs and learning curves
log_dir = './experiments/leduc_gin_rummy_dqn_result/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:
    # Initialize a global step
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # Set agents
    agent = DQNAgent(sess,
                     scope='dqn',
                     action_num=env.action_num,
                     replay_memory_init_size=memory_init_size,
                     train_every=train_every,
                     state_shape=env.state_shape,
                     mlp_layers=[128,128])
    random_agent = RandomAgent(action_num=eval_env.action_num)
    #if env.game.settings.scorer_name == "HighLowScorer":  # 200218 Note this
    #    random_agent = HighLowAgent(action_num=eval_env.action_num)

    env.set_agents([agent, random_agent])
    eval_env.set_agents([agent, random_agent])

    # Initialize global variables
    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)

    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent
        for ts in trajectories[0]:
            agent.feed(ts)

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('DQN')
    
    # Save model
    save_dir = 'models/gin_rummy_dqn'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(save_dir, 'model'))
    

