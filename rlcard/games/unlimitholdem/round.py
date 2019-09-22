# -*- coding: utf-8 -*-
''' Implement Limit Texas Hold'em Round class
'''

import random
from rlcard.games.limitholdem.round import LimitholdemRound

from rlcard.games.unlimitholdem.player import UnlimitholdemPlayer as Player

class UnlimitholdemRound(LimitholdemRound):
    ''' Round can call other Classes' functions to keep the game running
    '''

    def __init__(self, num_players, init_raise_amount):
        ''' Initilize the round class

        Args:
            allowed_raise_num (int): The number of allowed raise num
            num_players (int): The number of players
            init_raise_amount (int): The min raise amount when every round starts
        '''

        self.game_pointer = None
        self.num_players = num_players
        self.init_raise_amount = init_raise_amount
        self.current_raise_amount = self.init_raise_amount

        # Count the number without raise
        # If every player agree to not raise, the round is overr
        self.not_raise_num = 0

        # Raised amount for each player
        self.raised = [0 for _ in range(self.num_players)]

    def start_new_round(self, game_pointer, raised=None):
        ''' Start a new bidding round

        Args:
            raised (list): Initialize the chips for each player

        Note: For the first round of the game, we need to setup the big/small blind
        '''

        self.game_pointer = game_pointer
        self.not_raise_num = 0
        self.current_raise_amount = self.init_raise_amount
        if raised:
            self.raised = raised
        else:
            self.raised = [0 for _ in range(self.num_players)]

    def proceed_round(self, players, action):
        ''' Call other Classes's functions to keep one round running

        Args:
            players (list): The list of players that play the game
            action (str/int): An legal action taken by the player

        Returns:
            (int): The game_pointer that indicates the next player
        '''

        # if action not in self.get_legal_actions():
        #     raise Exception('{} is not legal action. Legal actions: {}', action, self.get_legal_actions())

        if action == 'call':
            diff = max(self.raised) - self.raised[self.game_pointer]
            self.raised[self.game_pointer] = max(self.raised)
            players[self.game_pointer].in_chips += diff
            self.not_raise_num += 1

        elif isinstance(action, int):
            # diff = max(self.raised) - self.raised[self.game_pointer] + action
            self.current_raise_amount = action - (max(self.raised) - self.raised[self.game_pointer])
            self.raised[self.game_pointer] += action
            players[self.game_pointer].in_chips += action
            
            # self.raised[self.game_pointer] = players[self.game_pointer].
            self.not_raise_num = 1

        elif action == 'fold':
            players[self.game_pointer].status = 'folded'
            self.player_folded = True

        elif action == 'check':
            self.not_raise_num += 1

        self.game_pointer = (self.game_pointer + 1) % self.num_players

        # Skip the folded players
        while players[self.game_pointer].status == 'folded':
             self.game_pointer = (self.game_pointer + 1) % self.num_players

        return self.game_pointer

    def get_legal_actions(self, players):
        ''' Obtain the legal actions for the curent player

        Args:
            players (list): The players in the game

        Returns:
           (list):  A list of legal actions
        '''

        full_actions = ['call', 'fold', 'check']

        # If the current chips are less than that of the highest one in the round, we can not check
        if self.raised[self.game_pointer] < max(self.raised):
            full_actions.remove('check')

        # If the current player has put in the chips that are more than others, we can not call
        if self.raised[self.game_pointer] == max(self.raised):
            full_actions.remove('call')

        # If the current player has no more chips after call, we cannot raise
        diff = max(self.raised) - self.raised[self.game_pointer]
        if players[self.game_pointer].in_chips + diff >= players[self.game_pointer].remained_chips:
            return full_actions

        # Append available raise amount to the action list
        min_raise_amount = max(self.raised) - self.raised[self.game_pointer] + self.current_raise_amount
        print('min_raise_amount:', max(self.raised), '-', self.raised[self.game_pointer], '+', self.current_raise_amount)
        # If the player cannot provide min raise amount, he has to all-in.
        if players[self.game_pointer].in_chips + min_raise_amount >= players[self.game_pointer].remained_chips:
            full_actions.append(players[self.game_pointer].remained_chips - players[self.game_pointer].in_chips)
        else:
            for available_raise_amount in range(min_raise_amount, players[self.game_pointer].remained_chips - players[self.game_pointer].in_chips + 1):
                # test
                if available_raise_amount <= 0:
                    raise ValueError("error raise amount")
                full_actions.append(available_raise_amount)

        return full_actions