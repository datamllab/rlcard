'''
    File name: gin_rummy/thinker.py
    Author: William Hale
    Date created: 3/28/2020
'''

from typing import List

from rlcard.games.base import Card

from . import melding
from . import utils


class Thinker(object):

    def __init__(self, hand: List[Card]):
        self.hand = hand

    # simple thinking
    def get_meld_piles_with_discard_card(self, discard_card: Card) -> List[List[Card]]:
        next_hand = self.hand + [discard_card]
        meld_clusters = melding.get_meld_clusters(hand=next_hand)
        best_deadwood_count = 999
        best_deadwoods = []  # type: List[List[Card]]
        best_meld_clusters = []  # type: List[List[List[Card]]]
        for meld_cluster in meld_clusters:
            meld_cards = [card for meld_pile in meld_cluster for card in meld_pile]
            deadwood = [card for card in next_hand if card not in meld_cards]
            deadwood_count = self._get_deadwood_count(deadwood=deadwood)
            if deadwood_count < best_deadwood_count:
                best_deadwood_count = deadwood_count
                best_deadwoods = [deadwood]
                best_meld_clusters = [meld_cluster]
            elif deadwood_count == best_deadwood_count:
                best_deadwoods.append(deadwood)
                best_meld_clusters.append(meld_cluster)
        want_discard_card = False
        for deadwood in best_deadwoods:
            if discard_card in deadwood:
                want_discard_card = False
                break
            else:
                want_discard_card = True
        result = []  # type: List[List[Card]]
        if want_discard_card:
            for meld_cluster in best_meld_clusters:
                for meld_pile in meld_cluster:
                    if discard_card in meld_pile:
                        result.append(meld_pile)
        return result

    @staticmethod
    def _get_deadwood_count(deadwood: List[Card]) -> int:
        deadwood_values = [utils.get_deadwood_value(card) for card in deadwood]
        return sum(deadwood_values)
