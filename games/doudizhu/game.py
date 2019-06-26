# -*- coding: utf-8 -*-
"""Implement Doudizhu Game class"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from core import Game
from player import DoudizhuPlayer
from round import DoudizhuRound


class DoudizhuGame(Game):
    """Start Doudizhu"""
    players_num = 3

    def start_game(self):
        players = [DoudizhuPlayer(num) for num in range(DoudizhuGame.players_num)]
        # for player in players:
        #     print(player.number)
        new_round = DoudizhuRound(players)


if __name__ == '__main__':
    game = DoudizhuGame()
    game.start_game()