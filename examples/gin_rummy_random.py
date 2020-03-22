'''
    File name: rlcard.examples.gin_rummy_random.py
    Author: William Hale
    Date created: 2/12/2020

    A toy example of playing GinRummy with random agents / novice agents
'''

import rlcard
from rlcard import models

from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed

from rlcard.games.gin_rummy.player import GinRummyPlayer
from rlcard.games.gin_rummy.utils.move import DealHandMove

# Make environment
env = rlcard.make('gin-rummy')
episode_num = 1
env.game.settings.print_settings()

# Set a global seed
set_global_seed(0)

# Set up agents
agents = [RandomAgent(action_num=env.action_num), RandomAgent(action_num=env.action_num)]
agents = models.load("gin-rummy-novice-rule").agents  # use novice agents rather than random agents
env.set_agents(agents)

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
        print("{}".format(move))
        if i == 0 and type(move) is DealHandMove:
            player_dealing_id = move.player_dealing.player_id
            leading_player_id = GinRummyPlayer.opponent_id_of(player_dealing_id)
            shuffle_deck = move.shuffled_deck
            leading_player_hand_text = [str(card) for card in shuffle_deck[-11:]]
            dealing_player_hand_text = [str(card) for card in shuffle_deck[-21:-11]]
            stock_pile_text = [str(card) for card in shuffle_deck[:31]]
            short_name_of_player_dealing = GinRummyPlayer.short_name_of(player_id=player_dealing_id)
            short_name_of_player_leading = GinRummyPlayer.short_name_of(player_id=leading_player_id)
            print("player_dealing is {}; leading_player is {}.".format(short_name_of_player_dealing,
                                                                       short_name_of_player_leading))
            print("leading player hand: {}".format(leading_player_hand_text))
            print("dealing player hand: {}".format(dealing_player_hand_text))
            print("stock_pile: {}".format(stock_pile_text))
