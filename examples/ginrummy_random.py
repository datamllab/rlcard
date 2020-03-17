''' A toy example of playing GinRummy with random agents
'''

import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed

from rlcard.games.gin_rummy.utils.move import *
from rlcard.games.gin_rummy.player import GinRummyPlayer
from rlcard.games.gin_rummy.agents import HighLowAgent

# Make environment
env = rlcard.make('gin-rummy')
episode_num = 1

# adjust game settings
choice = 0  # Please select a choice
if choice == 0:
    env.game.settings.set_gin_rummy()  # default choice
elif choice == 1:
    env.game.settings.set_high_low()  # first choice
    env.game.settings.max_drawn_card_count = 10  # 200218 Note: this
elif choice == 2:
    env.game.settings.set_simple_gin_rummy()  # second choice
env.game.settings.print_settings()

# Set a global seed
set_global_seed(0)

# Set up agents
agents = [RandomAgent(action_num=env.action_num), RandomAgent(action_num=env.action_num)]
if env.game.settings.scorer_name == "HighLowScorer":  # 200218 Note this
    agents[1] = HighLowAgent(action_num=env.action_num)
env.set_agents(agents)

# set scorer
env.set_scorer(printing_configuration=True)

for episode in range(episode_num):

    # Generate data from the environment
    trajectories, _ = env.run(is_training=False)

    # Print out the trajectories
    print('\nEpisode {}'.format(episode))
    for ts in trajectories[0]:
        print('State: {}, Action: {}, Reward: {}, Next State: {}, Done: {}'.format(ts[0], ts[1], ts[2], ts[3], ts[4]))

    # print move sheet
    print("\n========== Move Sheet ==========")
    move_sheet = env.game.round.move_sheet
    move_sheet_count = len(move_sheet)
    for i in range(move_sheet_count):
        move = move_sheet[i]
        print(move)
        if i == 0 and type(move) is DealHandMove:
            player_dealing = move.player_dealing
            leading_player = GinRummyPlayer.opponent_of(player_dealing)
            shuffle_deck = move.shuffled_deck
            leading_player_hand_text = [str(card) for card in shuffle_deck[-11:]]
            dealing_player_hand_text = [str(card) for card in shuffle_deck[-21:-11]]
            stock_pile_text = [str(card) for card in shuffle_deck[:31]]
            print("player_dealing is", player_dealing, "; leading_player is ", leading_player)
            print("leading player hand:", leading_player_hand_text)
            print("dealing player hand:", dealing_player_hand_text)
            print("stock_pile:", stock_pile_text)
