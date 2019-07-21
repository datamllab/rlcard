# -*- coding: utf-8 -*-
"""Implement Texasholdem Game classes"""
from core import Game
from dealer import TexasDealer
from itertools import product
import random
from player import Player
from round import TexasRound

RANKS = '23456789TJQKA'

class TexasGame(Game):
    def __init__(self, player_id = None, chips = 1000, big_blind = 10):
        self._deck = TexasDealer()
        self._player = Player(player_id, chips, True)
        self._house = Player("House", chips, False)
        self._board = Player("Board", 0 , True)
        self._round_count = 0
        self._small = big_blind / 2
        self._big = big_blind
        self._deck.reset_deck()

    def transfer_chips(self, player1, player2, amount = "all"):
        if amount == "all":
            player2.add_chips(player1.get_chips())
            player1.set_chips(0)
        else:
            player2.add_chips(amount)
            amount = -amount
            player1.add_chips(amount)

    def start(self):
        while self._player.get_chips() > 0 and self._house.get_chips() > 0:
            self.start_new_round()


        print (self._player.name , "has", self._player.get_chips(), "chips")
        print (self._house.name , "has", self._house.get_chips(), "chips")
        print ("After", self._round_count , "rounds")
        if self._player.get_chips() > 0 :
            print ("The winner is the", self._player.name)
        elif self._player.get_chips() <= 0 :
            print ("The winner is the", self._house.name)



if __name__ == '__main__':
    GAME = TexasGame()
    GAME.start()
