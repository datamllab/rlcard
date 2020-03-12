'''
    File name: gin_rummy/settings.py
    Author: William Hale
    Date created: 2/16/2020
'''

from enum import Enum


class DealerForRound(Enum):
    North = 0
    South = 1
    Random = 2


class Settings(object):

    def __init__(self):
        self.scorer_name = ["GinRummyScorer", "HighLowScorer"][0]
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
        print("scorer_name=", self.scorer_name)
        print("dealer_for_round=", self.dealer_for_round)
        print("stockpile_dead_card_count=", self.stockpile_dead_card_count)
        print("going_out_deadwood_count=", self.going_out_deadwood_count)
        print("max_drawn_card_count=", self.max_drawn_card_count)

        print("is_allowed_knock=", self.is_allowed_knock)
        print("is_allowed_gin=", self.is_allowed_gin)
        print("is_allowed_pick_up_discard=", self.is_allowed_pick_up_discard)

        print("is_allowed_to_discard_picked_up_card=", self.is_allowed_to_discard_picked_up_card)

        print("is_always_knock=", self.is_always_knock)
        print("is_south_never_knocks=", self.is_south_never_knocks)
        print("==============================")

    def set_high_low(self):  # speeding up training 200213
        # A very simple version: best strategy is to just discard card with highest deadwood value
        self.scorer_name = "HighLowScorer"
        self.dealer_for_round = DealerForRound.North
        self.stockpile_dead_card_count = 2
        self.going_out_deadwood_count = 10
        # don't go through a lot of draw from stockpile (10 draws for each player)
        self.max_drawn_card_count = 20
        self.is_allowed_knock = False
        self.is_allowed_gin = False
        self.is_allowed_pick_up_discard = False
        self.is_allowed_to_discard_picked_up_card = False
        self.is_always_knock = False
        self.is_south_never_knocks = True

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
