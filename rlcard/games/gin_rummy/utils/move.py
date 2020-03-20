'''
    File name: gin_rummy/move.py
    Author: William Hale
    Date created: 2/16/2020
'''

from typing import List

from rlcard.games.gin_rummy.utils.action_event import *
from rlcard.games.gin_rummy.card import Card
from rlcard.games.gin_rummy.player import GinRummyPlayer


#
#   These classes are used to keep a move_sheet history of the moves in a round.
#

class GinRummyMove(object):
    pass


class PlayerMove(GinRummyMove):

    def __init__(self, player: GinRummyPlayer, action: ActionEvent):
        super().__init__()
        self.player = player
        self.action = action


class DealHandMove(GinRummyMove):

    def __init__(self, player_dealing: GinRummyPlayer, shuffled_deck: List[Card]):
        super().__init__()
        self.player_dealing = player_dealing
        self.shuffled_deck = shuffled_deck

    def __str__(self):
        shuffled_deck_text = " ".join([str(card) for card in self.shuffled_deck])
        return "{} deal shuffled_deck=[{}]".format(self.player_dealing, shuffled_deck_text)


class DrawCardMove(PlayerMove):

    def __init__(self, player: GinRummyPlayer, action: DrawCardAction, card: Card):
        super().__init__(player, action)
        assert type(action) is DrawCardAction
        self.card = card

    def __str__(self):
        return "{} {} {}".format(self.player, self.action, self.card)


class PickupDiscardMove(PlayerMove):

    def __init__(self, player: GinRummyPlayer, action: PickUpDiscardAction, card: Card):
        super().__init__(player, action)
        assert type(action) is PickUpDiscardAction
        self.card = card

    def __str__(self):
        return "{} {} {}".format(self.player, self.action, self.card)


class DeclareDeadHandMove(PlayerMove):

    def __init__(self, player: GinRummyPlayer, action: DeclareDeadHandAction):
        super().__init__(player, action)
        assert type(action) is DeclareDeadHandAction

    def __str__(self):
        return "{} {}".format(self.player, self.action)


class DiscardMove(PlayerMove):

    def __init__(self, player: GinRummyPlayer, action: DiscardAction):
        super().__init__(player, action)
        assert type(action) is DiscardAction

    def __str__(self):
        return "{} {}".format(self.player, self.action)


class KnockMove(PlayerMove):

    def __init__(self, player: GinRummyPlayer, action: KnockAction):
        super().__init__(player, action)
        assert type(action) is KnockAction

    def __str__(self):
        return "{} {}".format(self.player, self.action)


class GinMove(PlayerMove):

    def __init__(self, player: GinRummyPlayer, action: GinAction):
        super().__init__(player, action)
        assert type(action) is GinAction

    def __str__(self):
        return "{} {}".format(self.player, self.action)


class ScoreNorthMove(PlayerMove):

    def __init__(self, player: GinRummyPlayer,
                 action: ScoreNorthPlayerAction,
                 best_meld_cluster: List[List[Card]],
                 deadwood_count: int):
        super().__init__(player, action)
        assert type(action) is ScoreNorthPlayerAction
        self.best_meld_cluster = best_meld_cluster  # for information use only
        self.deadwood_count = deadwood_count  # for information use only

    def __str__(self):
        best_meld_cluster_text = "{}".format([[str(card) for card in meld_pile] for meld_pile in self.best_meld_cluster])
        return "{} {} {} {}".format(self.player, self.action, self.deadwood_count, best_meld_cluster_text)


class ScoreSouthMove(PlayerMove):

    def __init__(self, player: GinRummyPlayer,
                 action: ScoreSouthPlayerAction,
                 best_meld_cluster: List[List[Card]],
                 deadwood_count: int):
        super().__init__(player, action)
        assert type(action) is ScoreSouthPlayerAction
        self.best_meld_cluster = best_meld_cluster  # for information use only
        self.deadwood_count = deadwood_count  # for information use only

    def __str__(self):
        best_meld_cluster_text = "{}".format([[str(card) for card in meld_pile] for meld_pile in self.best_meld_cluster])
        return "{} {} {} {}".format(self.player, self.action, self.deadwood_count, best_meld_cluster_text)
