'''
    File name: gin_rummy/z_test.py
    Author: William Hale
    Date created: 2/12/2020
'''

from rlcard.games.gin_rummy.action_event import *
from rlcard.games.gin_rummy.game import GinRummyGame
from rlcard.games.gin_rummy.judge import GinRummyJudge

import rlcard.games.gin_rummy.melding as melding
import rlcard.games.gin_rummy.utils as utils

import random

print_going_out_action = 2
print_move_sheet = 4


def play_game(print_level: int = 0, episode: int = None):
    game = GinRummyGame(allow_step_back=False)
    judge = GinRummyJudge(game=game)
    game.settings.max_drawn_card_count = 5  # NOTE: this
    game.init_game()
    if print_level & 1:
        print(
            f"dealer={game.round.players[game.round.dealer_id]} {[str(card) for card in game.round.dealer.stock_pile]}")
    while game.is_over() is False:
        current_player = game.get_current_player()
        legal_actions = judge.get_legal_actions()
        knock_actions = [action for action in legal_actions if type(action) is KnockAction]
        gin_actions = [action for action in legal_actions if type(action) is GinAction]
        if gin_actions:
            legal_action = random.choice(gin_actions)
        elif knock_actions:
            legal_action = random.choice(knock_actions)
        else:
            legal_action = random.choice(legal_actions)
        if type(legal_action) is DiscardAction or type(legal_action) is KnockAction:
            if current_player:
                hand = current_player.hand
                going_out_deadwood_count = game.settings.going_out_deadwood_count
                meld_clusters = melding.get_meld_clusters(hand=hand, going_out_deadwood_count=going_out_deadwood_count)
                for meld_cluster in meld_clusters:
                    deadwood = utils.get_deadwood(hand=hand, meld_cluster=meld_cluster)
                    meld_cluster_text = f"{[[str(card) for card in meld_pile] for meld_pile in meld_cluster]}"
                    deadwood_text = f"{[str(card) for card in deadwood]}"
                    if print_level & 1:
                        print(f"meld_cluster={meld_cluster_text} deadwood={deadwood_text}")
        if type(legal_action) is DrawCardAction:
            drawn_card = game.round.dealer.stock_pile[-1]
            if print_level & 1:
                print(f"{current_player} {legal_action} {drawn_card}")
        elif type(legal_action) is PickUpDiscardAction:
            pick_up_card = game.round.dealer.discard_pile[-1]
            if print_level & 1:
                print(f"{current_player} {legal_action} {pick_up_card}")
        else:
            if print_level & 1:
                print(f"{current_player} {legal_action}")
        game.step(legal_action)
    if print_level & print_going_out_action:
        episode_text = "" if episode is None else f"{episode} "
        last_action = game.actions[-1]
        if type(last_action) is KnockAction:
            print(f"{episode_text}{last_action}")
        elif type(last_action) is GinAction:
            print(f"{episode_text}{last_action}")
    if print_level & print_move_sheet:
        for move in game.round.move_sheet:
            print(f"{move}")


def test01():
    play_game(print_level=1)
    print("Done test01")


def test02():  # print games that end with knock or gin Note: doesn't succeed very well !!!
    episode_count = 1000
    for episode in range(episode_count):
        play_game(print_level=print_going_out_action, episode=episode)
    print("Done test02")


def test03():
    play_game(print_level=print_move_sheet)
    print("Done test01")


if __name__ == '__main__':
    test03()
