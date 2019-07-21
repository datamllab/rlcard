# -*- coding: utf-8 -*-
"""Implement Texasholdem Dealer class"""
import random
from core import Dealer
from utils.utils import init_standard_deck
from itertools import product
import random

DECK = init_standard_deck()

class TexasDealer(Dealer):
    def __init__(self):
        self._cards = []
        self._random_card =[]
    def reset_deck(self):
        self._cards = list(DECK)
        random.shuffle(self._cards)
        self._random_card = []

    def deal_cards(self,player):
        self._random_card = self._cards.pop()
        player.add_card(self._random_card)