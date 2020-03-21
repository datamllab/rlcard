'''
    File name: gin_rummy/settings.py
    Author: William Hale
    Date created: 2/16/2020
'''

from typing import Dict, Any

from enum import Enum


class DealerForRound(Enum):
    North = 0
    South = 1
    Random = 2


class Setting(Enum):
    dealer_for_round = "dealer_for_round"
    stockpile_dead_card_count = "stockpile_dead_card_count"
    going_out_deadwood_count = "going_out_deadwood_count"
    max_drawn_card_count = "max_drawn_card_count"
    is_allowed_knock = "is_allowed_knock"
    is_allowed_gin = "is_allowed_gin"
    is_allowed_pick_up_discard = "is_allowed_pick_up_discard"
    is_allowed_to_discard_picked_up_card = "is_allowed_to_discard_picked_up_card"
    is_always_knock = "is_always_knock"
    is_south_never_knocks = "is_south_never_knocks"

    @staticmethod
    def default_setting() -> Dict['Setting', Any]:
        return {Setting.dealer_for_round: DealerForRound.Random,
                Setting.stockpile_dead_card_count: 2,
                Setting.going_out_deadwood_count: 10,  # Can specify going_out_deadwood_count before running game.
                Setting.max_drawn_card_count: 52,
                Setting.is_allowed_knock: True,
                Setting.is_allowed_gin: True,
                Setting.is_allowed_pick_up_discard: True,
                Setting.is_allowed_to_discard_picked_up_card: False,
                Setting.is_always_knock: False,
                Setting.is_south_never_knocks: False
                }

    @staticmethod
    def simple_gin_rummy_setting():
        # North should be agent being trained.
        # North always deals.
        # South never knocks.
        # North always knocks when can.
        return {Setting.dealer_for_round: DealerForRound.North,
                Setting.stockpile_dead_card_count: 2,
                Setting.going_out_deadwood_count: 10,  # Can specify going_out_deadwood_count before running game.
                Setting.max_drawn_card_count: 52,
                Setting.is_allowed_knock: True,
                Setting.is_allowed_gin: True,
                Setting.is_allowed_pick_up_discard: True,
                Setting.is_allowed_to_discard_picked_up_card: False,
                Setting.is_always_knock: True,
                Setting.is_south_never_knocks: True
                }

    @staticmethod
    def gin_rummy_setting():
        # North always deals.
        return {Setting.dealer_for_round: DealerForRound.North,
                Setting.stockpile_dead_card_count: 2,
                Setting.going_out_deadwood_count: 10,  # Can specify going_out_deadwood_count before running game.
                Setting.max_drawn_card_count: 52,
                Setting.is_allowed_knock: True,
                Setting.is_allowed_gin: True,
                Setting.is_allowed_pick_up_discard: True,
                Setting.is_allowed_to_discard_picked_up_card: False,
                Setting.is_always_knock: False,
                Setting.is_south_never_knocks: False
                }


class Settings(object):

    def __init__(self):
        self.scorer_name = "GinRummyScorer"
        self.dealer_for_round = DealerForRound.Random
        self.stockpile_dead_card_count = 2
        self.going_out_deadwood_count = 10  # Can specify going_out_deadwood_count before running game
        self.max_drawn_card_count = 52

        self.is_allowed_knock = True
        self.is_allowed_gin = True
        self.is_allowed_pick_up_discard = True

        self.is_allowed_to_discard_picked_up_card = False

        self.is_always_knock = False
        self.is_south_never_knocks = False

    def print_settings(self):
        print("========== Settings ==========")
        print("scorer_name={}".format(self.scorer_name))
        print("dealer_for_round={}".format(self.dealer_for_round))
        print("stockpile_dead_card_count={}".format(self.stockpile_dead_card_count))
        print("going_out_deadwood_count={}".format(self.going_out_deadwood_count))
        print("max_drawn_card_count={}".format(self.max_drawn_card_count))

        print("is_allowed_knock={}".format(self.is_allowed_knock))
        print("is_allowed_gin={}".format(self.is_allowed_gin))
        print("is_allowed_pick_up_discard={}".format(self.is_allowed_pick_up_discard))

        print("is_allowed_to_discard_picked_up_card={}".format(self.is_allowed_to_discard_picked_up_card))

        print("is_always_knock={}".format(self.is_always_knock))
        print("is_south_never_knocks={}".format(self.is_south_never_knocks))
        print("==============================")

    def set_simple_gin_rummy(self):  # speeding up training 200213
        self.scorer_name = "GinRummyScorer"
        self.dealer_for_round = DealerForRound.North
        self.stockpile_dead_card_count = 2
        self.going_out_deadwood_count = 10
        self.max_drawn_card_count = 52
        self.is_allowed_knock = True
        self.is_allowed_gin = True
        self.is_allowed_pick_up_discard = True
        self.is_allowed_to_discard_picked_up_card = False
        self.is_always_knock = True
        self.is_south_never_knocks = True

    def set_gin_rummy(self):  # default
        self.scorer_name = "GinRummyScorer"
        self.dealer_for_round = DealerForRound.North
        self.stockpile_dead_card_count = 2
        self.going_out_deadwood_count = 10
        self.max_drawn_card_count = 52
        self.is_allowed_knock = True
        self.is_allowed_gin = True
        self.is_allowed_pick_up_discard = True
        self.is_allowed_to_discard_picked_up_card = False
        self.is_always_knock = False
        self.is_south_never_knocks = False
