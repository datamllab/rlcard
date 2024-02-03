import os
import json
import numpy as np
from collections import OrderedDict

import rlcard

from rlcard.games.skull_king.card import SkullKingCard as Card

# Read required docs
ROOT_PATH = rlcard.__path__[0]

# a map of abstract action to its index and a list of abstract action
with open(os.path.join(ROOT_PATH, 'games/skull_king/jsondata/action_space.json'), 'r') as file:
    ACTION_SPACE = json.load(file, object_pairs_hook=OrderedDict)
    ACTION_LIST = list(ACTION_SPACE.keys())

# a map of color to its index
COLOR_MAP = {'green': 0, 'yellow': 1, 'purple': 2, 'black': 3,'pirate': 4, 'escape': 5, 'special_pirate': 6}

# a map of trait to its index
TRAIT_MAP = {'1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
             '8': 8, '9': 9, '10': 10, '11': 11, '12': 12, '13': 13, 'pirate': 14, 'tigress': 15, 'skull king': 16,
             'escape': 17}


def init_deck():
    ''' Generate A SkullKing deck of 66 Cards
    '''
    deck = []
    card_info = SkullKingCard.info

    # init suit cards
    for color in ['green','yellow','purple']:


        for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9','10','11','12','13']:
            deck.append(SkullKingCard('suit', color, num))


    # init black trump cards
    for trump in ['black']:

        for num in ['1', '2', '3', '4', '5', '6', '7', '8', '9','10','11','12','13']:


          deck.append(SkullKingCard('black', trump, num))

    # init pirate cards

    for pirate in ['pirate1','pirate2','pirate3','pirate4','pirate5']:

      deck.append(SkullKingCard('pirate','pirate',pirate))

    # init escape cards

    for escape in ['escape1','escape2','escape3','escape4','escape5']:

      deck.append(SkullKingCard('escape','escape',escape))

    # init skull king

    deck.append(SkullKingCard('pirate','special_pirate','skull_king'))


    # init tigress

    deck.append(SkullKingCard('pirate','special_pirate','tigress'))




    return deck


def cards2list(cards):
    ''' Get the corresponding string representation of cards

    Args:
        cards (list): list of UnoCards objects

    Returns:
        (string): string representation of cards
    '''
    cards_list = []
    for card in cards:
        cards_list.append(card.get_str())
    return cards_list

def hand2dict(hand):
    ''' Get the corresponding dict representation of hand

    Args:
        hand (list): list of string of hand's card

    Returns:
        (dict): dict of hand
    '''
    hand_dict = {}
    for card in hand:
        if card not in hand_dict:
            hand_dict[card] = 1
        else:
            hand_dict[card] += 1
    return hand_dict



def encode_hand(plane, hand):
    ''' Encode hand and represerve it into plane

    Args:
        plane (array): 3*4*15 numpy array
        hand (list): list of string of hand's card

    Returns:
        (array): 3*4*15 numpy array
    '''
    # plane = np.zeros((3, 4, 15), dtype=int)
    plane[0] = np.ones((4, 15), dtype=int)
    hand = hand2dict(hand)
    for card, count in hand.items():
        card_info = card.split('-')
        color = COLOR_MAP[card_info[0]]
        trait = TRAIT_MAP[card_info[1]]
        if trait >= 13:
            if plane[1][0][trait] == 0:
                for index in range(4):
                    plane[0][index][trait] = 0
                    plane[1][index][trait] = 1
        else:
            plane[0][color][trait] = 0
            plane[count][color][trait] = 1
    return plane

def encode_target(plane, target):
    ''' Encode target and represerve it into plane

    Args:
        plane (array): 1*4*15 numpy array
        target(str): string of target card

    Returns:
        (array): 1*4*15 numpy array
    '''
    target_info = target.split('-')
    color = COLOR_MAP[target_info[0]]
    trait = TRAIT_MAP[target_info[1]]
    plane[color][trait] = 1
    return plane
