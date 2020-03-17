'''
    File name: gin_rummy/scorers.py
    Author: William Hale
    Date created: 2/15/2020
'''

from rlcard.games.gin_rummy.utils.action_event import *
from rlcard.games.gin_rummy.game import GinRummyGame
from rlcard.games.gin_rummy.player import GinRummyPlayer
from rlcard.games.gin_rummy.round import GinRummyRound

import rlcard.games.gin_rummy.utils.melding as melding
import rlcard.games.gin_rummy.utils.utils as utils

from typing import Callable


class Scorer:

    def __init__(self, name: str):
        self.name = name

    def get_payoffs(self, game: GinRummyGame):
        raise NotImplementedError


class GinRummyScorer(Scorer):

    def __init__(self, get_payoff: Callable[[GinRummyPlayer, GinRummyGame], int or float] = None):
        super().__init__(name="GinRummyScorer")
        self.get_payoff = get_payoff

    def get_payoffs(self, game: GinRummyGame):
        ''' Get the payoffs of players:
                a) 1 if gin
                b) 0.2 if knock
                c) -deadwood_count / 100 otherwise

        Returns:
            payoffs (list): a list of payoffs for each player
        '''
        payoffs = [0, 0]
        game_round = game.round
        last_action = game.actions[-1]
        assert game_round.is_over
        assert type(last_action) is ScoreSouthPlayerAction
        going_out_action = game_round.going_out_action
        going_out_player_id = game_round.going_out_player_id
        for i in range(2):  # FIXME: 200213 simplified calculation
            player = game.round.players[i]
            hand = player.hand
            if self.get_payoff:
                payoff = self.get_payoff(player, game)
            else:
                best_meld_clusters = melding.get_best_meld_clusters(hand=hand)
                best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
                deadwood_count = utils.get_deadwood_count(hand, best_meld_cluster)
                payoff = -deadwood_count / 100
                if going_out_player_id == player.player_id and type(going_out_action) is KnockAction:
                    payoff = 0.2  # FIXME: 200213 simplified calculation
                elif going_out_player_id == player.player_id and type(going_out_action) is GinAction:
                    payoff = 1  # FIXME: 200213 simplified calculation
                elif type(going_out_action) is DeclareDeadHandAction:
                    pass  # FIXME: 200213 payoffs should be zeros
                else:
                    raise Exception("get_payoffs: ???")
            payoffs[i] = payoff
        return payoffs


class HighLowScorer(Scorer):

    def __init__(self, get_payoff: Callable[[GinRummyPlayer, GinRummyGame], int or float] = None):
        super().__init__(name="HighLowScorer")
        self.get_payoff = get_payoff

    def get_payoffs(self, game: GinRummyGame):
        ''' Get the payoffs of players: (100 - deadwood count) / 100 with no melds allowed

        Returns:
            payoffs (list): a list of payoffs for each player
        '''
        payoffs = [0, 0]
        game_round = game.round
        last_action = game.actions[-1]
        assert game_round.is_over
        assert type(last_action) is ScoreSouthPlayerAction
        going_out_action = game_round.going_out_action
        for i in range(2):
            hand = game.round.players[i].hand
            if self.get_payoff:
                player = game.round.players[i]
                payoff = self.get_payoff(player, game)
            else:
                deadwood_count = sum([utils.get_deadwood_value(card) for card in hand])
                payoff = (100 - deadwood_count) / 100
            payoffs[i] = payoff
        if type(going_out_action) is DeclareDeadHandAction:
            pass
        else:
            raise Exception("get_payoffs: ???")
        return payoffs
