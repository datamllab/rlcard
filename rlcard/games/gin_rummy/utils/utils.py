'''
    File name: gin_rummy/utils.py
    Author: William Hale
    Date created: 2/12/2020
'''

from typing import List, Iterable

import numpy as np

from rlcard.games.gin_rummy.card import Card


def get_deadwood_value(card: Card) -> int:
    rank_id = card.rank_id
    return rank_id + 1 if rank_id < 9 else 10


def get_deadwood(hand: Iterable[Card], meld_cluster: List[Iterable[Card]], has_extra_card: bool) -> List[Card]:
    meld_cards = [card for meld_pile in meld_cluster for card in meld_pile]
    deadwood = [card for card in hand if card not in meld_cards]
    if deadwood and has_extra_card:
        # drop card with highest deadwood value
        worst_card = max(deadwood, key=lambda card: get_deadwood_value(card))
        deadwood.remove(worst_card)
    return deadwood


def get_deadwood_count(hand: List[Card], meld_cluster: List[Iterable[Card]], has_extra_card: bool) -> int:
    deadwood = get_deadwood(hand=hand, meld_cluster=meld_cluster, has_extra_card=has_extra_card)
    deadwood_values = [get_deadwood_value(card) for card in deadwood]
    return sum(deadwood_values)


def encode_cards(cards: List[Card]):
    plane = np.zeros(52, dtype=int)
    for card in cards:
        plane[card.card_id] = 1
    return plane
