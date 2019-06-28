# -*- coding: utf-8 -*-
"""Implement Doudizhu Game class"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(
    path.dirname(path.abspath(__file__)))))
from core import Game
from player import DoudizhuPlayer
from round import DoudizhuRound


class DoudizhuGame(Game):
    """Start Doudizhu Game"""
    players_num = 3

    def start_game(self):
        """Initialize players and round operator, and let round operator
        to proceed round
        """
        players = [DoudizhuPlayer(num)
                   for num in range(DoudizhuGame.players_num)]
        round_operator = DoudizhuRound(players)
        game_over, start = round_operator.proceed_round(
            players, round_operator.landlord_num)
        while not game_over:
            round_operator.greater_player = None
            game_over, start = round_operator.proceed_round(players, start)
        print('The game is over. The winner is '+str(start))

if __name__ == '__main__':
    GAME = DoudizhuGame()
    GAME.start_game()
