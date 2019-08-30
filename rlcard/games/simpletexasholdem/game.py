# -*- coding: utf-8 -*-
"""Implement Texasholdem Game classes"""
from rlcard.core import Game
from rlcard.games.simpletexasholdem.dealer import SimpleTexasDealer as Dealer
from itertools import product
import random
from rlcard.games.simpletexasholdem.player import SimpleTexasPlayer as Player
from rlcard.games.simpletexasholdem.round import SimpleTexasRound as Round
from rlcard.games.simpletexasholdem.judger import SimpleTexasJudger as Judger

RANKS = '23456789TJQKA'


class SimpleTexasGame(Game):

    players_num = 4

    def __init__(self, player_id = None, chips = 1000, big_blind = 10):
        self._deck = Dealer()
        self._player = Player(player_id, chips, True)
        self._house = Player("House", chips, False)
        self._board = Player("Board", 0 , True)
        self._round_count = 0
        self._small = big_blind / 2
        self._big = big_blind
    
    def get_player_num(self):
        """Return the number of players in the game
        """
        return SimpleTexasGame.players_num

    def get_player_id(self):
        """Return current player's id
        """
        return self._player 

    def get_state(self, player_id):
        """Return player's state

        with errors till now
        """
        player = self.players[player_id]
        if self.current_player is not None:  # when get first state
            return self.state
        else:  # when get final states of all players
            self.state['self'] = player_id
            self.state['hand'] = Judger.cards2str(player.hand)
            self.state['remained'] = Judger.cards2str(player.remained_cards)
            self.state['actions'] = None
            return self.state

    def transfer_chips(self, player1, player2, amount = "all"):
        if amount == "all":
            player2.add_chips(player1.get_chips())
            player1.set_chips(0)
        else:
            player2.add_chips(amount)
            amount = 0 - amount
            player1.add_chips(amount)

    def start(self):
        while self._player.get_chips() > 0 and self._house.get_chips() > 0:


            print (self._player.ID , "has", self._player.get_chips(), "chips")
            print (self._house.ID , "has", self._house.get_chips(), "chips")
            print ("After", self._round_count , "rounds")
            if self._player.get_chips() > 0 :
                print ("The winner is the", self._player.ID)
            elif self._player.get_chips() <= 0 :
                print ("The winner is the", self._house.ID)

    



if __name__ == '__main__':
    GAME = SimpleTexasGame()
    GAME.start()
