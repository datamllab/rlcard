''' An example of learning a Deep-Q Agent on GinRummy
'''

import tensorflow as tf

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed
from rlcard.utils.logger import Logger

from rlcard.games.gin_rummy.agents import HighLowAgent

from rlcard.games.gin_rummy.scorers import HighLowScorer
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
save_plot_every = 1000
evaluate_num = 100  # 5000  # 5000 is default
episode_num = 1000000

# Set the the number of steps for collecting normalization statistics
# and initial memory size
memory_init_size = 1000
norm_step = 1000

# The paths for saving the logs and learning curves
root_path = './experiments/gin_rummy_dqn_result/'
log_path = root_path + 'log.txt'
csv_path = root_path + 'performance.csv'
figure_path = root_path + 'figures/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:
    # Set agents
    global_step = tf.Variable(0, name='global_step', trainable=False)
    agent = DQNAgent(sess,
                     scope='dqn',
                     action_num=env.action_num,
                     replay_memory_size=20000,
                     replay_memory_init_size=memory_init_size,
                     norm_step=norm_step,
                     state_shape=env.state_shape,
                     mlp_layers=[512, 512])

    random_agent = RandomAgent(action_num=eval_env.action_num)
    if env.game.settings.scorer_name == "HighLowScorer":  # 200218 Note this
        random_agent = HighLowAgent(action_num=eval_env.action_num)

    sess.run(tf.global_variables_initializer())

    env.set_agents([agent, random_agent])
    eval_env.set_agents([agent, random_agent])

    # Count the number of steps
    step_counter = 0

    # Init a Logger to plot the learning curve
    logger = Logger(xlabel='timestep', ylabel='reward', legend='DQN on GinRummy', log_path=log_path, csv_path=csv_path)

    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent
        for ts in trajectories[0]:
            agent.feed(ts)
            step_counter += 1

            # Train the agent
            train_count = step_counter - (memory_init_size + norm_step)
            if train_count > 0:
                loss = agent.train()
                print('\rINFO - Step {}, loss: {}'.format(step_counter, loss), end='')

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            reward = 0
            reward2 = 0
            for eval_episode in range(evaluate_num):
                _, payoffs = eval_env.run(is_training=False)
                reward += payoffs[0]
                reward2 += payoffs[1]

            logger.log(f'\n########## Evaluation {episode} ##########')
            reward_text = f"{float(reward)/evaluate_num}"
            reward2_text = f"{float(reward2)/evaluate_num}"
            logger.log(f"Timestep: {env.timestep} Average reward is {reward_text}, reward2 is {reward2_text}")

            # Add point to logger
            logger.add_point(x=env.timestep, y=float(reward)/evaluate_num)

        # Make plot
        if episode % save_plot_every == 0 and episode > 0:
            logger.make_plot(save_path=figure_path+str(episode)+'.png')

    # Make the final plot
    logger.make_plot(save_path=figure_path+'final_'+str(episode)+'.png')
