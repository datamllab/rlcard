'''
    File name: gin_rummy/utils.py
    Author: William Hale
    Date created: 2/12/2020
'''

from rlcard.games.gin_rummy.card import Card

import numpy as np

from typing import List
from typing import Iterable


def get_deadwood_value(card: Card) -> int:
    rank_id = card.rank_id
    return rank_id + 1 if rank_id < 9 else 10


def get_deadwood(hand: Iterable[Card], meld_cluster: List[Iterable[Card]]) -> List[Card]:
    meld_cards = [card for meld_pile in meld_cluster for card in meld_pile]
    deadwood = [card for card in hand if card not in meld_cards]
    return deadwood


def get_deadwood_count(hand: List[Card], meld_cluster: List[Iterable[Card]]) -> int:
    deadwood = get_deadwood(hand=hand, meld_cluster=meld_cluster)
    return sum([get_deadwood_value(card) for card in deadwood])


def encode_cards(cards: List[Card]):
    plane = np.zeros(52, dtype=int)
    for card in cards:
        plane[card.card_id] = 1
    return plane
