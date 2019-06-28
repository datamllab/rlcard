# -*- coding: utf-8 -*-
"""Implement Doudizhu Player class"""
from core import Player
from methods import get_doudizhu_index
from methods import check_play_cards
from methods import get_play_string
from doudizhu import Card as DoudizhuCard
from doudizhu import check_card_type, list_greater_cards, cards_greater


class DoudizhuPlayer(Player):
    """Player can store cards in the player's hand and the role,
    determine the actions can be made according to the rules,
    and can perfrom responding action
    """

    def __init__(self, num):
        """Give the player a number(not id) in one game

        Member Vars:
            number: a player's temporaty number in one game
            role: a player's temporary role in one game(landlord or farmer)
            played_cards: the cards played in one round
        """
        self.number = num
        self.role = None
        self.played_cards = None

    def available_order(self, greater_player=None):
        """Get the actions can be made based on the rules

        Args:
            greater_player: the current winner in this round

        Return:
            list: a list of available orders
                  (some of ['draw'(叫/抢地主), 'not draw', 'play(出牌)', 'pass'])
        """
        orders = []
        if self.role is not None:
            if greater_player is None:
                orders.append('play')
            else:
                orders.append('pass')
                rocket = DoudizhuCard.card_ints_from_string('BJ-CJ')
                not_rocket, card_type = cards_greater(
                    rocket, greater_player.played_cards)
                if not not_rocket:
                    return orders
                candidate = get_play_string(self.hand, range(len(self.hand)))
                candidate = DoudizhuCard.card_ints_from_string(candidate)
                if len(list_greater_cards(greater_player.played_cards, candidate)) > 0:
                    orders.append('play')
        else:
            orders.extend(['draw', 'not draw'])
        return orders

    def play(self, action, greater_player=None):
        """Perfrom action

        Args:
            action: one of ['draw'(叫/抢地主), 'not draw', 'play(出牌)', 'pass']
            greater_player: the same to the upper

        Return:
            if current winner changed, return current winner
            else return None
        """
        if action == 'not draw':
            self.role = 'farmer'
            return None
        if action == 'draw':
            self.role = 'landlord'
            return None
        if action == 'play':
            total = len(self.hand)
            nums = input('Please enter the numbers of your hand'
                         ' and connect them with space(Eg: 0 1 2 10):')
            nums = nums.split()
            while True:
                if check_play_cards(nums, total):
                    cards = get_play_string(self.hand, nums)
                    cards = DoudizhuCard.card_ints_from_string(cards)
                    is_valid, type = check_card_type(cards)
                    if is_valid:
                        if greater_player is None:
                            self.played_cards = cards
                            break
                        else:
                            if cards_greater(cards, greater_player.played_cards)[0]:
                                self.played_cards = cards
                                break
                            else:
                                nums = input('Please enter greater cards:')
                    else:
                        nums = input('Please enter valid type:')
                else:
                    nums = input('Please enter valid numbers(Eg: 0 1 2 10):')
                nums = nums.split()
            nums.sort(reverse=True)
            for num in nums:
                self.hand.remove(self.hand[num])
            return self
        if action == 'pass':
            return greater_player

    def print_hand_and_orders(self, greater_player=None):
        """Print_hand_and_orders

        Args:
            greater_player: the same to the upper

        Return:
            The action choosed by player according to optional operations
        """
        print()
        print("the hand of player "+str(self.number)+": [", end='')
        for index, card in enumerate(self.hand[:-1]):
            print(str(index)+':'+get_doudizhu_index(card), end=', ')
        print(str(len(self.hand)-1)+':'+get_doudizhu_index(self.hand[-1])+']')
        orders = self.available_order(greater_player)
        print("optional operations of player " +
              str(self.number) + ": [", end='')
        for order in orders[:-1]:
            print(order, end=', ')
        print(orders[-1]+']')
        action = input("Your Choice: ")
        while action not in orders:
            action = input("Please input valid choice: ")
        return action
