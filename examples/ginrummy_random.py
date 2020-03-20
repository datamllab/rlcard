'''
    File name: rlcard.examples.ginrummy_random.py
    Author: William Hale
    Date created: 2/12/2020

    A toy example of playing GinRummy with random agents
'''

import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed

from rlcard.games.gin_rummy.utils.move import *
from rlcard.games.gin_rummy.player import GinRummyPlayer

# Make environment
env = rlcard.make('gin-rummy')
episode_num = 1
env.game.settings.print_settings()

# Set a global seed
set_global_seed(0)

# Set up agents
agents = [RandomAgent(action_num=env.action_num), RandomAgent(action_num=env.action_num)]
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
            player_dealing = move.player_dealing
            leading_player = GinRummyPlayer.opponent_of(player_dealing)
            shuffle_deck = move.shuffled_deck
            leading_player_hand_text = [str(card) for card in shuffle_deck[-11:]]
            dealing_player_hand_text = [str(card) for card in shuffle_deck[-21:-11]]
            stock_pile_text = [str(card) for card in shuffle_deck[:31]]
            print("player_dealing is {}; leading_player is {}.".format(player_dealing, leading_player))
            print("leading player hand: {}".format(leading_player_hand_text))
            print("dealing player hand: {}".format(dealing_player_hand_text))
            print("stock_pile: {}".format(stock_pile_text))
