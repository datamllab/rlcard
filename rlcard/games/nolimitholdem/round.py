# -*- coding: utf-8 -*-
''' Implement NoLimit Texas Hold'em Round class
'''
from enum import Enum

from rlcard.games.limitholdem import PlayerStatus


class Action(Enum):

    FOLD = 0
    CHECK = 1
    CALL = 2
    # RAISE_3BB = 3
    RAISE_HALF_POT = 3
    RAISE_POT = 4
    # RAISE_2POT = 5
    ALL_IN = 5
    # SMALL_BLIND = 7
    # BIG_BLIND = 8


class NolimitholdemRound:
    ''' Round can call other Classes' functions to keep the game running
    '''

    def __init__(self, num_players, init_raise_amount, dealer, np_random):
        ''' Initilize the round class

        Args:
            num_players (int): The number of players
            init_raise_amount (int): The min raise amount when every round starts
        '''
        self.np_random = np_random
        self.game_pointer = None
        self.num_players = num_players
        self.init_raise_amount = init_raise_amount

        self.dealer = dealer

        # Count the number without raise
        # If every player agree to not raise, the round is overr
        self.not_raise_num = 0

        # Count players that are not playing anymore (folded or all-in)
        self.not_playing_num = 0

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
        player = players[self.game_pointer]

        if action == Action.CALL:
            diff = max(self.raised) - self.raised[self.game_pointer]
            self.raised[self.game_pointer] = max(self.raised)
            player.bet(chips=diff)
            self.not_raise_num += 1

        elif action == Action.ALL_IN:
            all_in_quantity = player.remained_chips
            self.raised[self.game_pointer] = all_in_quantity + self.raised[self.game_pointer]
            player.bet(chips=all_in_quantity)

            self.not_raise_num = 1

        elif action == Action.RAISE_POT:
            self.raised[self.game_pointer] += self.dealer.pot
            player.bet(chips=self.dealer.pot)
            self.not_raise_num = 1

        elif action == Action.RAISE_HALF_POT:
            quantity = int(self.dealer.pot / 2)
            self.raised[self.game_pointer] += quantity
            player.bet(chips=quantity)
            self.not_raise_num = 1

        elif action == Action.FOLD:
            player.status = PlayerStatus.FOLDED

        elif action == Action.CHECK:
            self.not_raise_num += 1

        if player.remained_chips < 0:
            raise Exception("Player in negative stake")

        if player.remained_chips == 0 and player.status != PlayerStatus.FOLDED:
            player.status = PlayerStatus.ALLIN

        self.game_pointer = (self.game_pointer + 1) % self.num_players

        if player.status == PlayerStatus.ALLIN:
            self.not_playing_num += 1
            self.not_raise_num -= 1  # Because already counted in not_playing_num
        if player.status == PlayerStatus.FOLDED:
            self.not_playing_num += 1

        # Skip the folded players
        while players[self.game_pointer].status == PlayerStatus.FOLDED:
            self.game_pointer = (self.game_pointer + 1) % self.num_players

        return self.game_pointer

    def get_nolimit_legal_actions(self, players):
        ''' Obtain the legal actions for the curent player

        Args:
            players (list): The players in the game

        Returns:
           (list):  A list of legal actions
        '''

        full_actions = list(Action)
        # If the current chips are less than that of the highest one in the round, we can not check
        if self.raised[self.game_pointer] < max(self.raised):
            full_actions.remove(Action.CHECK)

        # If the current player has put in the chips that are more than others, we can not call
        if self.raised[self.game_pointer] == max(self.raised):
            full_actions.remove(Action.CALL)

        player = players[self.game_pointer]

        if self.dealer.pot > player.remained_chips:
            full_actions.remove(Action.RAISE_POT)

        if int(self.dealer.pot / 2) > player.remained_chips:
            full_actions.remove(Action.RAISE_HALF_POT)

        # Can't raise if the raise is smaller than pot
        if Action.RAISE_HALF_POT in full_actions and \
                int(self.dealer.pot / 2) + player.in_chips <= max(self.raised):
            full_actions.remove(Action.RAISE_HALF_POT)

        # If the current player has no more chips after call, we cannot raise
        diff = max(self.raised) - self.raised[self.game_pointer]
        if diff > 0 and player.in_chips + diff >= player.remained_chips:
            return [Action.FOLD, Action.CALL]

        return full_actions

    def is_over(self):
        ''' Check whether the round is over

        Returns:
            (boolean): True if the current round is over
        '''
        if self.not_raise_num + self.not_playing_num >= self.num_players:
            return True
        return False
