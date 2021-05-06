# -*- coding: utf-8 -*-
''' Implement Doudizhu Dealer class
'''
import functools

from rlcard.utils import init_54_deck
from rlcard.games.doudizhu.utils import cards2str, doudizhu_sort_card

class DoudizhuDealer:
    ''' Dealer will shuffle, deal cards, and determine players' roles
    '''
    def __init__(self, np_random):
        '''Give dealer the deck

        Notes:
            1. deck with 54 cards including black joker and red joker
        '''
        self.np_random = np_random
        self.deck = init_54_deck()
        self.deck.sort(key=functools.cmp_to_key(doudizhu_sort_card))
        self.landlord = None

    def shuffle(self):
        ''' Randomly shuffle the deck
        '''
        self.np_random.shuffle(self.deck)

    def deal_cards(self, players):
        ''' Deal cards to players

        Args:
            players (list): list of DoudizhuPlayer objects
        '''
        hand_num = (len(self.deck) - 3) // len(players)
        for index, player in enumerate(players):
            current_hand = self.deck[index*hand_num:(index+1)*hand_num]
            current_hand.sort(key=functools.cmp_to_key(doudizhu_sort_card))
            player.set_current_hand(current_hand)
            player.initial_hand = cards2str(player.current_hand)

    def determine_role(self, players):
        ''' Determine landlord and peasants according to players' hand

        Args:
            players (list): list of DoudizhuPlayer objects

        Returns:
            int: landlord's player_id
        '''
        # deal cards
        self.shuffle()
        self.deal_cards(players)
        players[0].role = 'landlord'
        self.landlord = players[0]
        players[1].role = 'peasant'
        players[2].role = 'peasant'
        #players[0].role = 'peasant'
        #self.landlord = players[0]

        ## determine 'landlord'
        #max_score = get_landlord_score(
        #    cards2str(self.landlord.current_hand))
        #for player in players[1:]:
        #    player.role = 'peasant'
        #    score = get_landlord_score(
        #        cards2str(player.current_hand))
        #    if score > max_score:
        #        max_score = score
        #        self.landlord = player
        #self.landlord.role = 'landlord'

        # give the 'landlord' the  three cards
        self.landlord.current_hand.extend(self.deck[-3:])
        self.landlord.current_hand.sort(key=functools.cmp_to_key(doudizhu_sort_card))
        self.landlord.initial_hand = cards2str(self.landlord.current_hand)
        return self.landlord.player_id
