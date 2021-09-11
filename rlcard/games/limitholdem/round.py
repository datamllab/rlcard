# -*- coding: utf-8 -*-
"""Limit texas holdem round class implementation"""


class LimitHoldemRound:
    """Round can call other Classes' functions to keep the game running"""

    def __init__(self, raise_amount, allowed_raise_num, num_players, np_random):
        """
        Initialize the round class

        Args:
            raise_amount (int): the raise amount for each raise
            allowed_raise_num (int): The number of allowed raise num
            num_players (int): The number of players
        """
        self.np_random = np_random
        self.game_pointer = None
        self.raise_amount = raise_amount
        self.allowed_raise_num = allowed_raise_num

        self.num_players = num_players

        # Count the number of raise
        self.have_raised = 0

        # Count the number without raise
        # If every player agree to not raise, the round is over
        self.not_raise_num = 0

        # Raised amount for each player
        self.raised = [0 for _ in range(self.num_players)]
        self.player_folded = None

    def start_new_round(self, game_pointer, raised=None):
        """
        Start a new bidding round

        Args:
            game_pointer (int): The game_pointer that indicates the next player
            raised (list): Initialize the chips for each player

        Note: For the first round of the game, we need to setup the big/small blind
        """
        self.game_pointer = game_pointer
        self.have_raised = 0
        self.not_raise_num = 0
        if raised:
            self.raised = raised
        else:
            self.raised = [0 for _ in range(self.num_players)]

    def proceed_round(self, players, action):
        """
        Call other classes functions to keep one round running

        Args:
            players (list): The list of players that play the game
            action (str): An legal action taken by the player

        Returns:
            (int): The game_pointer that indicates the next player
        """
        if action not in self.get_legal_actions():
            raise Exception('{} is not legal action. Legal actions: {}'.format(action, self.get_legal_actions()))

        if action == 'call':
            diff = max(self.raised) - self.raised[self.game_pointer]
            self.raised[self.game_pointer] = max(self.raised)
            players[self.game_pointer].in_chips += diff
            self.not_raise_num += 1

        elif action == 'raise':
            diff = max(self.raised) - self.raised[self.game_pointer] + self.raise_amount
            self.raised[self.game_pointer] = max(self.raised) + self.raise_amount
            players[self.game_pointer].in_chips += diff
            self.have_raised += 1
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

    def get_legal_actions(self):
        """
        Obtain the legal actions for the current player

        Returns:
           (list):  A list of legal actions
        """
        full_actions = ['call', 'raise', 'fold', 'check']

        # If the the number of raises already reaches the maximum number raises, we can not raise any more
        if self.have_raised >= self.allowed_raise_num:
            full_actions.remove('raise')

        # If the current chips are less than that of the highest one in the round, we can not check
        if self.raised[self.game_pointer] < max(self.raised):
            full_actions.remove('check')

        # If the current player has put in the chips that are more than others, we can not call
        if self.raised[self.game_pointer] == max(self.raised):
            full_actions.remove('call')

        return full_actions

    def is_over(self):
        """
        Check whether the round is over

        Returns:
            (boolean): True if the current round is over
        """
        if self.not_raise_num >= self.num_players:
            return True
        return False
