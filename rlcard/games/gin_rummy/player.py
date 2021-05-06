'''
    File name: gin_rummy/player.py
    Author: William Hale
    Date created: 2/12/2020
'''

from typing import List

from rlcard.games.base import Card

from .utils import utils

from .utils import melding


class GinRummyPlayer:

    def __init__(self, player_id: int, np_random):
        ''' Initialize a GinRummy player class

        Args:
            player_id (int): id for the player
        '''
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []  # type: List[Card]
        self.known_cards = []  # type: List[Card]  # opponent knows cards picked up by player and not yet discarded
        # memoization for speed
        self.meld_kinds_by_rank_id = [[] for _ in range(13)]  # type: List[List[List[Card]]]
        self.meld_run_by_suit_id = [[] for _ in range(4)]  # type: List[List[List[Card]]]

    def get_player_id(self) -> int:
        ''' Return player's id
        '''
        return self.player_id

    def get_meld_clusters(self) -> List[List[List[Card]]]:
        result = []  # type: List[List[List[Card]]]
        all_run_melds = [frozenset(meld_kind) for meld_kinds in self.meld_kinds_by_rank_id for meld_kind in meld_kinds]
        all_set_melds = [frozenset(meld_run) for meld_runs in self.meld_run_by_suit_id for meld_run in meld_runs]
        all_melds = all_run_melds + all_set_melds
        all_melds_count = len(all_melds)
        for i in range(0, all_melds_count):
            first_meld = all_melds[i]
            first_meld_list = list(first_meld)
            meld_cluster_1 = [first_meld_list]
            result.append(meld_cluster_1)
            for j in range(i + 1, all_melds_count):
                second_meld = all_melds[j]
                second_meld_list = list(second_meld)
                if not second_meld.isdisjoint(first_meld):
                    continue
                meld_cluster_2 = [first_meld_list, second_meld_list]
                result.append(meld_cluster_2)
                for k in range(j + 1, all_melds_count):
                    third_meld = all_melds[k]
                    third_meld_list = list(third_meld)
                    if not third_meld.isdisjoint(first_meld) or not third_meld.isdisjoint(second_meld):
                        continue
                    meld_cluster_3 = [first_meld_list, second_meld_list, third_meld_list]
                    result.append(meld_cluster_3)
        return result

    def did_populate_hand(self):
        self.meld_kinds_by_rank_id = [[] for _ in range(13)]
        self.meld_run_by_suit_id = [[] for _ in range(4)]
        all_set_melds = melding.get_all_set_melds(hand=self.hand)
        for set_meld in all_set_melds:
            rank_id = utils.get_rank_id(set_meld[0])
            self.meld_kinds_by_rank_id[rank_id].append(set_meld)
        all_run_melds = melding.get_all_run_melds(hand=self.hand)
        for run_meld in all_run_melds:
            suit_id = utils.get_suit_id(run_meld[0])
            self.meld_run_by_suit_id[suit_id].append(run_meld)

    def add_card_to_hand(self, card: Card):
        self.hand.append(card)
        self._increase_meld_kinds_by_rank_id(card=card)
        self._increase_run_kinds_by_suit_id(card=card)

    def remove_card_from_hand(self, card: Card):
        self.hand.remove(card)
        self._reduce_meld_kinds_by_rank_id(card=card)
        self._reduce_run_kinds_by_suit_id(card=card)

    def __str__(self):
        return "N" if self.player_id == 0 else "S"

    @staticmethod
    def short_name_of(player_id: int) -> str:
        return "N" if player_id == 0 else "S"

    @staticmethod
    def opponent_id_of(player_id: int) -> int:
        return (player_id + 1) % 2

    # private methods

    def _increase_meld_kinds_by_rank_id(self, card: Card):
        rank_id = utils.get_rank_id(card)
        meld_kinds = self.meld_kinds_by_rank_id[rank_id]
        if len(meld_kinds) == 0:
            card_rank = card.rank
            meld_kind = [card for card in self.hand if card.rank == card_rank]
            if len(meld_kind) >= 3:
                self.meld_kinds_by_rank_id[rank_id].append(meld_kind)
        else:  # must have all cards of given rank
            suits = ['S', 'H', 'D', 'C']
            max_kind_meld = [Card(suit, card.rank) for suit in suits]
            self.meld_kinds_by_rank_id[rank_id] = [max_kind_meld]
            for meld_card in max_kind_meld:
                self.meld_kinds_by_rank_id[rank_id].append([card for card in max_kind_meld if card != meld_card])

    def _reduce_meld_kinds_by_rank_id(self, card: Card):
        rank_id = utils.get_rank_id(card)
        meld_kinds = self.meld_kinds_by_rank_id[rank_id]
        if len(meld_kinds) > 1:
            suits = ['S', 'H', 'D', 'C']
            self.meld_kinds_by_rank_id[rank_id] = [[Card(suit, card.rank) for suit in suits if suit != card.suit]]
        else:
            self.meld_kinds_by_rank_id[rank_id] = []

    def _increase_run_kinds_by_suit_id(self, card: Card):
        suit_id = utils.get_suit_id(card=card)
        self.meld_run_by_suit_id[suit_id] = melding.get_all_run_melds_for_suit(cards=self.hand, suit=card.suit)

    def _reduce_run_kinds_by_suit_id(self, card: Card):
        suit_id = utils.get_suit_id(card=card)
        meld_runs = self.meld_run_by_suit_id[suit_id]
        self.meld_run_by_suit_id[suit_id] = [meld_run for meld_run in meld_runs if card not in meld_run]
