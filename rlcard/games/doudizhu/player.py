# -*- coding: utf-8 -*-
''' Implement Doudizhu Player class
'''
import functools

from rlcard.games.doudizhu.utils import get_gt_cards
from rlcard.games.doudizhu.utils import cards2str, doudizhu_sort_card


class DoudizhuPlayer:
    ''' Player can store cards in the player's hand and the role,
    determine the actions can be made according to the rules,
    and can perfrom corresponding action
    '''
    def __init__(self, player_id, np_random):
        ''' Give the player an id in one game

        Args:
            player_id (int): the player_id of a player

        Notes:
            1. role: A player's temporary role in one game(landlord or peasant)
            2. played_cards: The cards played in one round
            3. hand: Initial cards
            4. _current_hand: The rest of the cards after playing some of them
        '''
        self.np_random = np_random
        self.player_id = player_id
        self.initial_hand = None
        self._current_hand = []
        self.role = ''
        self.played_cards = None
        self.singles = '3456789TJQKA2BR'

        #record cards removed from self._current_hand for each play()
        # and restore cards back to self._current_hand when play_back()
        self._recorded_played_cards = []

    @property
    def current_hand(self):
        return self._current_hand

    def set_current_hand(self, value):
        self._current_hand = value

    def get_state(self, public, others_hands, num_cards_left, actions):
        state = {}
        state['seen_cards'] = public['seen_cards']
        state['landlord'] = public['landlord']
        state['trace'] = public['trace'].copy()
        state['played_cards'] = public['played_cards']
        state['self'] = self.player_id
        state['current_hand'] = cards2str(self._current_hand)
        state['others_hand'] = others_hands
        state['num_cards_left'] = num_cards_left
        state['actions'] = actions

        return state

    def available_actions(self, greater_player=None, judger=None):
        ''' Get the actions can be made based on the rules

        Args:
            greater_player (DoudizhuPlayer object): player who played
        current biggest cards.
            judger (DoudizhuJudger object): object of DoudizhuJudger

        Returns:
            list: list of string of actions. Eg: ['pass', '8', '9', 'T', 'J']
        '''
        actions = []
        if greater_player is None or greater_player.player_id == self.player_id:
            actions = judger.get_playable_cards(self)
        else:
            actions = get_gt_cards(self, greater_player)
        return actions

    def play(self, action, greater_player=None):
        ''' Perfrom action

        Args:
            action (string): specific action
            greater_player (DoudizhuPlayer object): The player who played current biggest cards.

        Returns:
            object of DoudizhuPlayer: If there is a new greater_player, return it, if not, return None
        '''
        trans = {'B': 'BJ', 'R': 'RJ'}
        if action == 'pass':
            self._recorded_played_cards.append([])
            return greater_player
        else:
            removed_cards = []
            self.played_cards = action
            for play_card in action:
                if play_card in trans:
                    play_card = trans[play_card]
                for _, remain_card in enumerate(self._current_hand):
                    if remain_card.rank != '':
                        remain_card = remain_card.rank
                    else:
                        remain_card = remain_card.suit
                    if play_card == remain_card:
                        removed_cards.append(self.current_hand[_])
                        self._current_hand.remove(self._current_hand[_])
                        break
            self._recorded_played_cards.append(removed_cards)
            return self

    def play_back(self):
        ''' Restore recorded cards back to self._current_hand
        '''
        removed_cards = self._recorded_played_cards.pop()
        self._current_hand.extend(removed_cards)
        self._current_hand.sort(key=functools.cmp_to_key(doudizhu_sort_card))
