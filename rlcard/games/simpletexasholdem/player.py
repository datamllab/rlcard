# -*- coding: utf-8 -*-
import json
from rlcard.core import Player
from rlcard.games.simpletexasholdem.judger import SimpleTexasJudger as Judger


class SimpleTexasPlayer(Player):
    def __init__(self,player_id = None, chips = 1000 , face_up = False):
        self.ID = player_id
        self._cards = []
        self._hand = Judger(player_id)
        self._chips = chips
        self._face_up = face_up

    def add_card(self, card):
        self._cards.append(card)

    def add_card_to_hand(self,cards):
        for card in cards:
            self._hand._all_cards.append(card)

    def get_hand_name(self):
        return self._hand._hand_name

    def reset_player_cards(self):
        self._cards = []
        self._hand = Judger(self.ID)

    def display_cards(self):
        if self._face_up == True:
            print (self.ID , "has :" , self._cards)
        else:
            print (self.ID , "has : [X,X]")

    def display_all_cards(self):
        print (self.ID , "has :" , self._cards)

    def get_chips(self):
        return self._chips

    def add_chips(self, more_chips):
        self._chips += more_chips

    def set_chips(self, amount):
        self._chips = amount

    def get_cards(self):
        return self._cards

    def evaluate(self):
        if len(self._hand._all_cards) == 7:
            self._hand.evaluateHand()
       
    def get_hand_category(self):
        return self._hand._category

    def get_hand_five_cards(self):
        return self._hand._five_cards
