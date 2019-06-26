# -*- coding: utf-8 -*-
"""Implement Doudizhu Card class"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from core import Card


def get_doudizhu_index(card: Card):
    """Get valid index of a card in order to check type

    Return:
        string: Eg: As, 2h, Kc, BJ, CJ
    """
    index = card.rank+card.suit.lower()
    if index == 'rj':
        index = 'CJ'
    if index == 'bj':
        index = 'BJ'
    return index


def get_play_string(hand, nums):
    """Get valid string of the cards played by a player in order to check type

    Return:
        String: Eg: 2c-2d-2h-2s-BJ-CJ

    """
    play_cards = ''
    for num in nums:
        play_cards += (get_doudizhu_index(hand[num]) + '-')
    play_cards[-1] = ''
    return play_cards

    