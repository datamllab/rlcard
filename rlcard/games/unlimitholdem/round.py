# -*- coding: utf-8 -*-
''' Implement Limit Texas Hold'em Round class
'''

import random
from rlcard.games.limitholdem.round import LimitholdemRound

from rlcard.games.unlimitholdem.player import UnlimitholdemPlayer as Player

class UnlimitholdemRound(LimitholdemRound):
    ''' Round can call other Classes' functions to keep the game running
    '''

    def __init__(self, num_players):
        ''' Initilize the round class

        Args:
            raise_amount (int): the raise amount for each raise
            allowed_raise_num (int): The number of allowed raise num
            num_players (int): The number of players
        '''

        self.button = None
        self.num_players = num_players

        # Count the number without raise
        # If every player agree to not raise, the round is overr
        self.not_raise_num = 0

        # Raised amount for each player
        self.raised = [0 for _ in range(self.num_players)]

    def start_new_round(self, button, raised=None):
        ''' Start a new bidding round

        Args:
            raised (list): Initialize the chips for each player

        Note: For the first round of the game, we need to setup the big/small blind
        '''

        self.button = button
        self.not_raise_num = 0
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
            (int): The button that indicates the next player
        '''

        # if action not in self.get_legal_actions():
        #     raise Exception('{} is not legal action. Legal actions: {}', action, self.get_legal_actions())

        if action == 'call':
            diff = max(self.raised) - self.raised[self.button]
            self.raised[self.button] = max(self.raised)
            players[self.button].in_chips += diff
            self.not_raise_num += 1

        elif isinstance(action, int):
            # diff = max(self.raised) - self.raised[self.button] + action
            self.raised[self.button] = max(self.raised) + action
            players[self.button].in_chips += action
            self.not_raise_num = 1

        elif action == 'fold':
            players[self.button].status = 'folded'
            self.player_folded = True

        elif action == 'check':
            self.not_raise_num += 1

        self.button = (self.button + 1) % self.num_players

        # Skip the folded players
        while players[self.button].status == 'folded':
             self.button = (self.button + 1) % self.num_players

        return self.button

    def get_legal_actions(self, players):
        ''' Obtain the legal actions for the curent player

        Args:
            players (list): The players in the game

        Returns:
           (list):  A list of legal actions
        '''

        full_actions = ['call', 'fold', 'check']

        # If the current chips are less than that of the highest one in the round, we can not check
        if self.raised[self.button] < max(self.raised):
            full_actions.remove('check')

        # If the current player has put in the chips that are more than others, we can not call
        if self.raised[self.button] == max(self.raised):
            full_actions.remove('call')

        # Append available raise amount to the action list
        last_raised_amount = max(self.raised) - self.raised[self.button]
        min_raise_amount = 2 * last_raised_amount

        # If the player cannot provide min raise amount, he has to all-in.
        if players[self.button].in_chips + min_raise_amount >= players[self.button].remained_chips:
            full_actions.append(players[self.button].remained_chips - players[self.button].in_chips)
        else:
            for available_raise_amount in range(min_raise_amount, players[self.button].remained_chips - players[self.button].in_chips + 1):
                full_actions.append(available_raise_amount)

        return full_actions