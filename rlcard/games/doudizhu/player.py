# -*- coding: utf-8 -*-
''' Implement Doudizhu Player class
'''
from copy import deepcopy

from rlcard.games.doudizhu.utils import get_gt_cards
from rlcard.games.doudizhu.utils import cards2str


class DoudizhuPlayer(object):
    ''' Player can store cards in the player's hand and the role,
    determine the actions can be made according to the rules,
    and can perfrom corresponding action
    '''

    def __init__(self, player_id):
        ''' Give the player an id in one game

        Args:
            player_id (int): the player_id of a player

        Notes:
            1. role: A player's temporary role in one game(landlord or peasant)
            2. played_cards: The cards played in one round
            3. hand: Initial cards
            4. current_hand: The rest of the cards after playing some of them
        '''

        self.player_id = player_id
        self.initial_hand = None
        self.current_hand = []
        self.role = ''
        self.played_cards = None
        self.singles = '3456789TJQKA2BR'

    def get_state(self, public, others_hands, actions):
        state = deepcopy(public)
        state['self'] = self.player_id
        state['initial_hand'] = self.initial_hand
        state['current_hand'] = cards2str(self.current_hand)
        state['others_hand'] = others_hands
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
        if greater_player is None or greater_player is self:
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
            return greater_player
        else:
            self.played_cards = action
            for play_card in action:
                if play_card in trans:
                    play_card = trans[play_card]
                for _, remain_card in enumerate(self.current_hand):
                    if remain_card.rank != '':
                        remain_card = remain_card.rank
                    else:
                        remain_card = remain_card.suit
                    if play_card == remain_card:
                        self.current_hand.remove(self.current_hand[_])
                        break
            return self
