'''
    File name: gin_rummy/melding.py
    Author: William Hale
    Date created: 2/12/2020
'''

from rlcard.games.gin_rummy.card import Card

import rlcard.games.gin_rummy.utils.utils as utils

from typing import List
from typing import Set

import copy

"""
    Terminology:
        run_meld - three or more cards of same suit in sequence
        set_meld - three or more cards of same rank
        meld_pile - a run_meld or a set_meld
        meld_piles - a list of meld_pile
        meld_cluster - same as meld_piles, but usually with the piles being mutually disjoint
        meld_clusters - a list of meld_cluster
"""


def get_meld_clusters(hand: List[Card], opponent_meld_piles: List[List[Card]] = None) -> List[List[Set[Card]]]:
    # opponent_meld_piles are those of the going_out_player to be used for laying off cards
    result = []  # type: List[List[Set[Card]]]
    all_run_melds = [set(x) for x in _get_all_run_melds(hand)]
    all_set_melds = [set(x) for x in _get_all_set_melds(hand)]
    all_melds = all_run_melds + all_set_melds
    all_melds_count = len(all_melds)
    for i in range(0, all_melds_count):
        first_meld = all_melds[i]
        meld_cluster_1 = [first_meld]
        result.append(meld_cluster_1)
        for j in range(i + 1, all_melds_count):
            second_meld = all_melds[j]
            if not second_meld.isdisjoint(first_meld):
                continue
            meld_cluster_2 = [first_meld, second_meld]
            result.append(meld_cluster_2)
            for k in range(j + 1, all_melds_count):
                third_meld = all_melds[k]
                if not third_meld.isdisjoint(first_meld) or not third_meld.isdisjoint(second_meld):
                    continue
                meld_cluster_3 = [first_meld, second_meld, third_meld]
                result.append(meld_cluster_3)
    return result


def get_going_out_meld_clusters(meld_clusters: List[List[Set[Card]]],
                                hand: List[Card],
                                going_out_deadwood_count: int) -> List[List[Set[Card]]]:
    # Return only meld_clusters with deadwood count <= going_out_deadwood_count
    result = []  # type: List[List[Set[Card]]]
    for meld_cluster in meld_clusters:
        deadwood_count = utils.get_deadwood_count(hand=hand, meld_cluster=meld_cluster, has_extra_card=True)
        if deadwood_count <= going_out_deadwood_count:
            result.append(meld_cluster)
    return result


def get_best_meld_clusters(hand: List[Card], has_extra_card: bool) -> List[List[Set[Card]]]:
    result = []  # type: List[List[Set[Card]]]
    meld_clusters = get_meld_clusters(hand=hand)
    meld_clusters_count = len(meld_clusters)
    if meld_clusters_count > 0:
        deadwood_counts = [utils.get_deadwood_count(hand=hand,
                                                    meld_cluster=meld_cluster,
                                                    has_extra_card=has_extra_card)
                           for meld_cluster in meld_clusters]
        best_deadwood_count = min(deadwood_counts)
        for i in range(meld_clusters_count):
            if deadwood_counts[i] == best_deadwood_count:
                result.append(meld_clusters[i])
    return result

# private methods


def _get_all_run_melds(hand: List[Card]) -> List[List[Card]]:
    card_count = len(hand)
    hand_by_suit = sorted(hand, key=lambda x: x.card_id)
    max_run_melds_from_left = [[] for _ in hand_by_suit]
    for i in range(card_count):
        card = hand_by_suit[i]
        max_run_melds_from_left[i].append(card)
        for j in range(i + 1, card_count):
            next_card = hand_by_suit[j]
            if next_card.suit != card.suit or next_card.rank_id != card.rank_id + (j - i):
                break
            else:
                max_run_melds_from_left[i].append(next_card)
    max_run_melds_from_left = [run_meld for run_meld in max_run_melds_from_left if len(run_meld) >= 3]
    result = copy.deepcopy(max_run_melds_from_left)
    for max_run_meld in max_run_melds_from_left:
        max_run_meld_count = len(max_run_meld)
        if max_run_meld_count > 3:
            for i in range(max_run_meld_count - 3):
                result.append(max_run_meld[:-(i + 1)])
    return result


def _get_all_set_melds(hand: List[Card]) -> List[List[Card]]:
    max_set_melds = []
    hand_by_rank = sorted(hand, key=lambda x: x.rank)
    set_meld = []
    current_rank = None
    for card in hand_by_rank:
        if current_rank is None or current_rank == card.rank:
            set_meld.append(card)
        else:
            if len(set_meld) >= 3:
                max_set_melds.append(set_meld)
            set_meld = [card]
        current_rank = card.rank
    if len(set_meld) >= 3:
        max_set_melds.append(set_meld)
    result = copy.deepcopy(max_set_melds)
    for max_set_meld in max_set_melds:
        if len(max_set_meld) == 4:
            for meld_card in max_set_meld:
                result.append([card for card in max_set_meld if card != meld_card])
    return result
