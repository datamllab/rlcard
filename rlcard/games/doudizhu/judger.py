# -*- coding: utf-8 -*-
''' Implement Doudizhu Judger class
'''
import numpy as np
import collections
from itertools import combinations
from bisect import bisect_left

from rlcard.games.doudizhu.utils import CARD_RANK_STR, CARD_RANK_STR_INDEX
from rlcard.games.doudizhu.utils import cards2str, contains_cards



class DoudizhuJudger:
    ''' Determine what cards a player can play
    '''
    @staticmethod
    def chain_indexes(indexes_list):
        ''' Find chains for solos, pairs and trios by using indexes_list

        Args:
            indexes_list: the indexes of cards those have the same count, the count could be 1, 2, or 3.

        Returns:
            list of tuples: [(start_index1, length1), (start_index1, length1), ...]

        '''
        chains = []
        prev_index = -100
        count = 0
        start = None
        for i in indexes_list:
            if (i[0] >= 12): #no chains for '2BR'
                break
            if (i[0] == prev_index + 1):
                count += 1
            else:
                if (count > 1):
                    chains.append((start, count))
                count = 1
                start = i[0]
            prev_index = i[0]
        if (count > 1):
            chains.append((start, count))
        return chains

    @classmethod
    def solo_attachments(cls, hands, chain_start, chain_length, size):
        ''' Find solo attachments for trio_chain_solo_x and four_two_solo

        Args:
            hands:
            chain_start: the index of start card of the trio_chain or trio or four
            chain_length: the size of the sequence of the chain, 1 for trio_solo or four_two_solo
            size: count of solos for the attachments

        Returns:
            list of tuples: [attachment1, attachment2, ...]
                            Each attachment has two elemnts,
                            the first one contains indexes of attached cards smaller than the index of chain_start,
                            the first one contains indexes of attached cards larger than the index of chain_start
        '''
        attachments = set()
        candidates = []
        prev_card = None
        same_card_count = 0
        for card in hands:
            #dont count those cards in the chain
            if (CARD_RANK_STR_INDEX[card] >= chain_start and CARD_RANK_STR_INDEX[card] < chain_start + chain_length):
                continue
            if (card == prev_card):
                #attachments can not have bomb
                if (same_card_count == 3):
                    continue
                #attachments can not have 3 same cards consecutive with the trio (except 3 cards of '222')
                elif (same_card_count == 2 and (CARD_RANK_STR_INDEX[card] == chain_start - 1 or CARD_RANK_STR_INDEX[card] == chain_start + chain_length) and card != '2'):
                    continue
                else:
                    same_card_count += 1
            else:
                prev_card = card
                same_card_count = 1
            candidates.append(CARD_RANK_STR_INDEX[card])
        for attachment in combinations(candidates, size):
            if (attachment[-1] == 14 and attachment[-2] == 13):
                continue
            i = bisect_left(attachment, chain_start)
            attachments.add((attachment[:i], attachment[i:]))
        return list(attachments)

    @classmethod
    def pair_attachments(cls, cards_count, chain_start, chain_length, size):
        ''' Find pair attachments for trio_chain_pair_x and four_two_pair

        Args:
            cards_count:
            chain_start: the index of start card of the trio_chain or trio or four
            chain_length: the size of the sequence of the chain, 1 for trio_pair or four_two_pair
            size: count of pairs for the attachments

        Returns:
            list of tuples: [attachment1, attachment2, ...]
                            Each attachment has two elemnts,
                            the first one contains indexes of attached cards smaller than the index of chain_start,
                            the first one contains indexes of attached cards larger than the index of chain_start
        '''
        attachments = set()
        candidates = []
        for i, _ in enumerate(cards_count):
            if (i >= chain_start and i < chain_start + chain_length):
                continue
            if (cards_count[i] == 2 or cards_count[i] == 3):
                candidates.append(i)
            elif (cards_count[i] == 4):
                candidates.append(i)
        for attachment in combinations(candidates, size):
            if (attachment[-1] == 14 and attachment[-2] == 13):
                continue
            i = bisect_left(attachment, chain_start)
            attachments.add((attachment[:i], attachment[i:]))
        return list(attachments)
        
    @staticmethod
    def playable_cards_from_hand(current_hand):
        ''' Get playable cards from hand

        Returns:
            set: set of string of playable cards
        '''
        cards_dict = collections.defaultdict(int)
        for card in current_hand:
            cards_dict[card] += 1
        cards_count = np.array([cards_dict[k] for k in CARD_RANK_STR])
        playable_cards = set()

        non_zero_indexes = np.argwhere(cards_count > 0)
        more_than_1_indexes = np.argwhere(cards_count > 1)
        more_than_2_indexes = np.argwhere(cards_count > 2)
        more_than_3_indexes = np.argwhere(cards_count > 3)
        #solo
        for i in non_zero_indexes:
            playable_cards.add(CARD_RANK_STR[i[0]])
        #pair
        for i in more_than_1_indexes:
            playable_cards.add(CARD_RANK_STR[i[0]] * 2)
        #bomb, four_two_solo, four_two_pair
        for i in more_than_3_indexes:
            cards = CARD_RANK_STR[i[0]] * 4
            playable_cards.add(cards)
            for left, right in DoudizhuJudger.solo_attachments(current_hand, i[0], 1, 2):
                pre_attached = ''
                for j in left:
                    pre_attached += CARD_RANK_STR[j]
                post_attached = ''
                for j in right:
                    post_attached += CARD_RANK_STR[j]
                playable_cards.add(pre_attached + cards + post_attached)
            for left, right in DoudizhuJudger.pair_attachments(cards_count, i[0], 1, 2):
                pre_attached = ''
                for j in left:
                    pre_attached += CARD_RANK_STR[j] * 2
                post_attached = ''
                for j in right:
                    post_attached += CARD_RANK_STR[j] * 2
                playable_cards.add(pre_attached + cards + post_attached)

        #solo_chain_5 -- #solo_chain_12
        solo_chain_indexes = DoudizhuJudger.chain_indexes(non_zero_indexes)
        for (start_index, length) in solo_chain_indexes:
            s, l = start_index, length
            while(l >= 5):
                cards = ''
                curr_index = s - 1
                curr_length = 0
                while (curr_length < l and curr_length < 12):
                    curr_index += 1
                    curr_length += 1
                    cards += CARD_RANK_STR[curr_index]
                    if (curr_length >= 5):
                        playable_cards.add(cards)
                l -= 1
                s += 1

        #pair_chain_3 -- #pair_chain_10
        pair_chain_indexes = DoudizhuJudger.chain_indexes(more_than_1_indexes)
        for (start_index, length) in pair_chain_indexes:
            s, l = start_index, length
            while(l >= 3):
                cards = ''
                curr_index = s - 1
                curr_length = 0
                while (curr_length < l and curr_length < 10):
                    curr_index += 1
                    curr_length += 1
                    cards += CARD_RANK_STR[curr_index] * 2
                    if (curr_length >= 3):
                        playable_cards.add(cards)
                l -= 1
                s += 1

        #trio, trio_solo and trio_pair
        for i in more_than_2_indexes:
            playable_cards.add(CARD_RANK_STR[i[0]] * 3)
            for j in non_zero_indexes:
                if (j < i):
                    playable_cards.add(CARD_RANK_STR[j[0]] + CARD_RANK_STR[i[0]] * 3)
                elif (j > i):
                    playable_cards.add(CARD_RANK_STR[i[0]] * 3 + CARD_RANK_STR[j[0]])
            for j in more_than_1_indexes:
                if (j < i):
                    playable_cards.add(CARD_RANK_STR[j[0]] * 2 + CARD_RANK_STR[i[0]] * 3)
                elif (j > i):
                    playable_cards.add(CARD_RANK_STR[i[0]] * 3 + CARD_RANK_STR[j[0]] * 2)

        #trio_solo, trio_pair, #trio -- trio_chain_2 -- trio_chain_6; trio_solo_chain_2 -- trio_solo_chain_5; trio_pair_chain_2 -- trio_pair_chain_4
        trio_chain_indexes = DoudizhuJudger.chain_indexes(more_than_2_indexes)
        for (start_index, length) in trio_chain_indexes:
            s, l = start_index, length
            while(l >= 2):
                cards = ''
                curr_index = s - 1
                curr_length = 0
                while (curr_length < l and curr_length < 6):
                    curr_index += 1
                    curr_length += 1
                    cards += CARD_RANK_STR[curr_index] * 3

                    #trio_chain_2 to trio_chain_6
                    if (curr_length >= 2 and curr_length <= 6):
                        playable_cards.add(cards)

                    #trio_solo_chain_2 to trio_solo_chain_5
                    if (curr_length >= 2 and curr_length <= 5):
                        for left, right in DoudizhuJudger.solo_attachments(current_hand, s, curr_length, curr_length):
                            pre_attached = ''
                            for j in left:
                                pre_attached += CARD_RANK_STR[j]
                            post_attached = ''
                            for j in right:
                                post_attached += CARD_RANK_STR[j]
                            playable_cards.add(pre_attached + cards + post_attached)

                    #trio_pair_chain2 -- trio_pair_chain_4
                    if (curr_length >= 2 and curr_length <= 4):
                        for left, right in DoudizhuJudger.pair_attachments(cards_count, s, curr_length, curr_length):
                            pre_attached = ''
                            for j in left:
                                pre_attached += CARD_RANK_STR[j] * 2
                            post_attached = ''
                            for j in right:
                                post_attached += CARD_RANK_STR[j] * 2
                            playable_cards.add(pre_attached + cards + post_attached)
                l -= 1
                s += 1
        #rocket
        if (cards_count[13] and cards_count[14]):
            playable_cards.add(CARD_RANK_STR[13] + CARD_RANK_STR[14])
        return playable_cards

    def __init__(self, players, np_random):
        ''' Initilize the Judger class for Dou Dizhu
        '''
        self.playable_cards = [set() for _ in range(3)]
        self._recorded_removed_playable_cards = [[] for _ in range(3)]
        for player in players:
            player_id = player.player_id
            current_hand = cards2str(player.current_hand)
            self.playable_cards[player_id] = self.playable_cards_from_hand(current_hand)

    def calc_playable_cards(self, player):
        ''' Recalculate all legal cards the player can play according to his
        current hand.

        Args:
            player (DoudizhuPlayer object): object of DoudizhuPlayer
            init_flag (boolean): For the first time, set it True to accelerate
              the preocess.

        Returns:
            list: list of string of playable cards
        '''
        removed_playable_cards = []

        player_id = player.player_id
        current_hand = cards2str(player.current_hand)
        missed = None
        for single in player.singles:
            if single not in current_hand:
                missed = single
                break

        playable_cards = self.playable_cards[player_id].copy()

        if missed is not None:
            position = player.singles.find(missed)
            player.singles = player.singles[position+1:]
            for cards in playable_cards:
                if missed in cards or (not contains_cards(current_hand, cards)):
                    removed_playable_cards.append(cards)
                    self.playable_cards[player_id].remove(cards)
        else:
            for cards in playable_cards:
                if not contains_cards(current_hand, cards):
                    #del self.playable_cards[player_id][cards]
                    removed_playable_cards.append(cards)
                    self.playable_cards[player_id].remove(cards)
        self._recorded_removed_playable_cards[player_id].append(removed_playable_cards)
        return self.playable_cards[player_id]

    def restore_playable_cards(self, player_id):
        ''' restore playable_cards for judger for game.step_back().

        Args:
            player_id: The id of the player whose playable_cards need to be restored
        '''
        removed_playable_cards = self._recorded_removed_playable_cards[player_id].pop()
        self.playable_cards[player_id].update(removed_playable_cards)

    def get_playable_cards(self, player):
        ''' Provide all legal cards the player can play according to his
        current hand.

        Args:
            player (DoudizhuPlayer object): object of DoudizhuPlayer
            init_flag (boolean): For the first time, set it True to accelerate
              the preocess.

        Returns:
            list: list of string of playable cards
        '''
        return self.playable_cards[player.player_id]


    @staticmethod
    def judge_game(players, player_id):
        ''' Judge whether the game is over

        Args:
            players (list): list of DoudizhuPlayer objects
            player_id (int): integer of player's id

        Returns:
            (bool): True if the game is over
        '''
        player = players[player_id]
        if not player.current_hand:
            return True
        return False

    @staticmethod
    def judge_payoffs(landlord_id, winner_id):
        payoffs = np.array([0, 0, 0])
        if winner_id == landlord_id:
            payoffs[landlord_id] = 1
        else:
            for index, _ in enumerate(payoffs):
                if index != landlord_id:
                    payoffs[index] = 1
        return payoffs
