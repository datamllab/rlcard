'''
    File name: gin_rummy/round.py
    Author: William Hale
    Date created: 2/12/2020
'''

from rlcard.games.gin_rummy.utils.action_event import *
from rlcard.games.gin_rummy.player import GinRummyPlayer
from rlcard.games.gin_rummy.dealer import GinRummyDealer
from rlcard.games.gin_rummy.utils.move import *

import rlcard.games.gin_rummy.utils.melding as melding
import rlcard.games.gin_rummy.utils.utils as utils

from typing import List


class GinRummyRound(object):

    def __init__(self, dealer_id: int):
        ''' Initialize the round class

        Args:
            dealer_id: int
        '''
        self.dealer_id = dealer_id
        self.dealer = GinRummyDealer()
        self.players = [GinRummyPlayer(player_id=0), GinRummyPlayer(player_id=1)]
        self.current_player_id = (dealer_id + 1) % 2
        self.is_over = False
        self.going_out_action = None
        self.going_out_player_id = None
        self.move_sheet = []
        player_dealing = GinRummyPlayer(player_id=dealer_id)
        shuffled_deck = self.dealer.shuffled_deck
        self.move_sheet.append(DealHandMove(player_dealing=player_dealing, shuffled_deck=shuffled_deck))

    def get_current_player(self) -> GinRummyPlayer or None:
        current_player_id = self.current_player_id
        return None if current_player_id is None else self.players[current_player_id]

    def score_player_0(self, action: ScoreNorthPlayerAction):
        assert self.current_player_id == 0
        current_player = self.get_current_player()
        best_meld_clusters = melding.get_best_meld_clusters(hand=current_player.hand)
        best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
        deadwood_count = utils.get_deadwood_count(hand=current_player.hand, meld_cluster=best_meld_cluster)
        self.move_sheet.append(ScoreNorthMove(player=current_player,
                                              action=action,
                                              best_meld_cluster=best_meld_cluster,
                                              deadwood_count=deadwood_count))
        self.current_player_id = 1

    def score_player_1(self, action: ScoreSouthPlayerAction):
        assert self.current_player_id == 1
        current_player = self.get_current_player()
        best_meld_clusters = melding.get_best_meld_clusters(hand=current_player.hand)
        best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
        deadwood_count = utils.get_deadwood_count(hand=current_player.hand, meld_cluster=best_meld_cluster)
        self.move_sheet.append(ScoreSouthMove(player=current_player,
                                              action=action,
                                              best_meld_cluster=best_meld_cluster,
                                              deadwood_count=deadwood_count))
        self.is_over = True

    def draw_card(self, action: DrawCardAction):
        current_player = self.players[self.current_player_id]
        assert len(current_player.hand) == 10
        card = self.dealer.stock_pile.pop()
        self.move_sheet.append(DrawCardMove(current_player, action=action, card=card))
        current_player.hand.append(card)

    def pick_up_discard(self, action: PickUpDiscardAction):
        current_player = self.players[self.current_player_id]
        assert len(current_player.hand) == 10
        card = self.dealer.discard_pile.pop()
        self.move_sheet.append(PickupDiscardMove(current_player, action, card=card))
        current_player.hand.append(card)
        current_player.known_cards.append(card)

    def declare_dead_hand(self, action: DeclareDeadHandAction):
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(DeclareDeadHandMove(current_player, action))
        self.going_out_action = action
        self.going_out_player_id = self.current_player_id
        assert len(current_player.hand) == 10
        self.current_player_id = 0

    def gin(self, action: GinAction):
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(GinMove(current_player, action))
        # print(f"\nDid gin: {current_player} {action}.")
        self.going_out_action = action
        self.going_out_player_id = self.current_player_id
        assert len(current_player.hand) == 11
        self.current_player_id = 0

    def discard(self, action: DiscardAction):
        current_player = self.players[self.current_player_id]
        assert len(current_player.hand) == 11
        self.move_sheet.append(DiscardMove(current_player, action))
        card = action.card
        current_player.hand.remove(card)
        if card in current_player.known_cards:
            current_player.known_cards.remove(card)
        self.dealer.discard_pile.append(card)
        self.current_player_id = (self.current_player_id + 1) % 2

    def knock(self, action: KnockAction):
        current_player = self.players[self.current_player_id]
        #  print(f"\nDid knock: {current_player} {action}.")
        self.move_sheet.append(KnockMove(current_player, action))
        self.going_out_action = action
        self.going_out_player_id = self.current_player_id
        assert len(current_player.hand) == 11
        card = action.card
        current_player.hand.remove(card)
        if card in current_player.known_cards:
            current_player.known_cards.remove(card)
        self.current_player_id = 0
