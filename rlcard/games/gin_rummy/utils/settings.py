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
    def simple_gin_rummy_setting():  # speeding up training 200213
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


dealer_for_round = Setting.dealer_for_round
stockpile_dead_card_count = Setting.stockpile_dead_card_count
going_out_deadwood_count = Setting.going_out_deadwood_count
max_drawn_card_count = Setting.max_drawn_card_count
is_allowed_knock = Setting.is_allowed_knock
is_allowed_gin = Setting.is_allowed_gin
is_allowed_pick_up_discard = Setting.is_allowed_pick_up_discard
is_allowed_to_discard_picked_up_card = Setting.is_allowed_to_discard_picked_up_card
is_always_knock = Setting.is_always_knock
is_south_never_knocks = Setting.is_south_never_knocks


class Settings(object):

    def __init__(self):
        self.scorer_name = "GinRummyScorer"
        default_setting = Setting.default_setting()
        self.dealer_for_round = default_setting[Setting.dealer_for_round]
        self.stockpile_dead_card_count = default_setting[Setting.stockpile_dead_card_count]
        self.going_out_deadwood_count = default_setting[Setting.going_out_deadwood_count]
        self.max_drawn_card_count = default_setting[Setting.max_drawn_card_count]
        self.is_allowed_knock = default_setting[Setting.is_allowed_knock]
        self.is_allowed_gin = default_setting[Setting.is_allowed_gin]
        self.is_allowed_pick_up_discard = default_setting[Setting.is_allowed_pick_up_discard]
        self.is_allowed_to_discard_picked_up_card = default_setting[Setting.is_allowed_to_discard_picked_up_card]
        self.is_always_knock = default_setting[Setting.is_always_knock]
        self.is_south_never_knocks = default_setting[Setting.is_south_never_knocks]

    def change_settings(self, config: Dict[Setting, Any]):
        corrected_config = Settings.get_config_with_invalid_settings_set_to_default_value(config=config)
        for key, value in corrected_config.items():
            if key == Setting.dealer_for_round:
                self.dealer_for_round = value
            elif key == Setting.stockpile_dead_card_count:
                self.stockpile_dead_card_count = value
            elif key == Setting.going_out_deadwood_count:
                self.going_out_deadwood_count = value
            elif key == Setting.max_drawn_card_count:
                self.max_drawn_card_count = value
            elif key == Setting.is_allowed_knock:
                self.is_allowed_knock = value
            elif key == Setting.is_allowed_gin:
                self.is_allowed_gin = value
            elif key == Setting.is_allowed_pick_up_discard:
                self.is_allowed_pick_up_discard = value
            elif key == Setting.is_allowed_to_discard_picked_up_card:
                self.is_allowed_to_discard_picked_up_card = value
            elif key == Setting.is_always_knock:
                self.is_always_knock = value
            elif key == Setting.is_south_never_knocks:
                self.is_south_never_knocks = value

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

    @staticmethod
    def get_config_with_invalid_settings_set_to_default_value(config: Dict[Setting, Any]) -> Dict[Setting, Any]:
        # Set each invalid setting to its default_value.
        result = config.copy()
        default_setting = Setting.default_setting()
        for key, value in config.items():
            if key == dealer_for_round and not isinstance(value, DealerForRound):
                result[dealer_for_round] = default_setting[dealer_for_round]
            elif key == stockpile_dead_card_count and not isinstance(value, int):
                result[stockpile_dead_card_count] = default_setting[stockpile_dead_card_count]
            elif key == going_out_deadwood_count and not isinstance(value, int):
                result[going_out_deadwood_count] = default_setting[going_out_deadwood_count]
            elif key == max_drawn_card_count and not isinstance(value, int):
                result[max_drawn_card_count] = default_setting[max_drawn_card_count]
            elif key == is_allowed_knock and not isinstance(value, bool):
                result[is_allowed_knock] = default_setting[is_allowed_knock]
            elif key == is_allowed_gin and not isinstance(value, bool):
                result[is_allowed_gin] = default_setting[is_allowed_gin]
            elif key == is_allowed_pick_up_discard and not isinstance(value, bool):
                result[is_allowed_pick_up_discard] = default_setting[is_allowed_pick_up_discard]
            elif key == is_allowed_to_discard_picked_up_card and not isinstance(value, bool):
                result[is_allowed_to_discard_picked_up_card] = default_setting[is_allowed_to_discard_picked_up_card]
            elif key == is_always_knock and not isinstance(value, bool):
                result[is_always_knock] = default_setting[is_always_knock]
            elif key == is_south_never_knocks and not isinstance(value, bool):
                result[is_south_never_knocks] = default_setting[is_south_never_knocks]
        return result

