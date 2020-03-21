'''
    File name: gin_rummy/scorers.py
    Author: William Hale
    Date created: 2/15/2020
'''

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..game import GinRummyGame

from typing import Callable

from .action_event import *
from ..player import GinRummyPlayer

import rlcard.games.gin_rummy.utils.melding as melding
import rlcard.games.gin_rummy.utils.utils as utils


class GinRummyScorer:

    def __init__(self, name: str = None, get_payoff: Callable[[GinRummyPlayer, 'GinRummyGame'], int or float] = None):
        self.name = name if name is not None else "GinRummyScorer"
        self.get_payoff = get_payoff if get_payoff else get_payoff_gin_rummy_v1

    def get_payoffs(self, game: 'GinRummyGame'):
        payoffs = [0, 0]
        for i in range(2):
            player = game.round.players[i]
            payoff = self.get_payoff(player=player, game=game)
            payoffs[i] = payoff
        return payoffs


def get_payoff_gin_rummy_v1(player: GinRummyPlayer, game: 'GinRummyGame') -> int or float:
    ''' Get the payoff of player:
            a) 1.0 if player gins
            b) 0.2 if player knocks
            c) -deadwood_count / 100 otherwise

    Returns:
        payoff (int or float): payoff for player
    '''
    # payoff is 1.0 if player gins
    # payoff is 0.2 if player knocks
    # payoff is -deadwood_count / 100 if otherwise
    # The goal is to have the agent learn how to knock and gin.
    # The negative payoff when the agent fails to knock or gin should encourage the agent to form melds.
    # The payoff is scaled to lie between -1 and 1.
    going_out_action = game.round.going_out_action
    going_out_player_id = game.round.going_out_player_id
    if going_out_player_id == player.player_id and type(going_out_action) is KnockAction:
        payoff = 0.2
    elif going_out_player_id == player.player_id and type(going_out_action) is GinAction:
        payoff = 1
    else:
        hand = player.hand
        best_meld_clusters = melding.get_best_meld_clusters(hand=hand)
        best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
        deadwood_count = utils.get_deadwood_count(hand, best_meld_cluster)
        payoff = -deadwood_count / 100
    return payoff
