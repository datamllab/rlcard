import os
import json
import numpy as np

import rlcard

from rlcard.games.uno.card import UnoCard as Card

ROOT_PATH = rlcard.__path__[0]

with open(os.path.join(ROOT_PATH, 'games/uno/jsondata/action_space.json'), 'r') as file:
    ACTION_SPACE = json.load(file)
    ACTION_LIST = list(ACTION_SPACE.keys())

COLOR_MAP = {'r': 0, 'g': 1, 'b': 2, 'y': 3}

TRAIT_MAP = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
             '8': 8, '9': 9, 'skip': 10, 'reverse': 11, 'draw_2': 12,
             'wild': 13, 'wild_draw_4': 14}


def init_deck():
    deck = []
    card_info = Card.info
    for color in card_info['color']:

        # init number cards
        for num in card_info['trait'][:10]:
            deck.append(Card('number', color, num))
            if num != '0':
                deck.append(Card('number', color, num))

        # init action cards
        for action in card_info['trait'][10:13]:
            deck.append(Card('action', color, action))
            deck.append(Card('action', color, action))

        # init wild cards
        for wild in card_info['trait'][-2:]:
            deck.append(Card('wild', color, wild))
    return deck


def cards2list(cards):
    cards_list = []
    for card in cards:
        cards_list.append(card.get_str())
    return cards_list

def hand2dict(hand):
    hand_dict = {}
    for card in hand:
        if card not in hand_dict:
            hand_dict[card] = 1
        else:
            hand_dict[card] += 1
    return hand_dict

def encode_hand(encoded_hand, hand):
    # encoded_hand = np.zeros((3, 4, 15), dtype=int)
    encoded_hand[0] = np.ones((4, 15), dtype=int)
    hand = hand2dict(hand)
    for card, count in hand.items():
        card_info = card.split('-')
        color = COLOR_MAP[card_info[0]]
        trait = TRAIT_MAP[card_info[1]]
        if trait >= 13 and encoded_hand[1][0][trait] == 0:
            for index in range(4):
                encoded_hand[0][index][trait] = 0
                encoded_hand[1][index][trait] = 1
        else:
            encoded_hand[0][color][trait] = 0
            encoded_hand[count][color][trait] = 1
    return encoded_hand

def encode_target(encoded_target, target):
    # encoded_target = np.zeros((4, 15), dtype=int)
    target_info = target.split('-')
    color = COLOR_MAP[target_info[0]]
    trait = TRAIT_MAP[target_info[1]]
    encoded_target[color][trait] = 1
    return encoded_target

if __name__ == '__main__':
    hand = ['g-reverse', 'y-8', 'g-wild_draw_4', 'r-3', 'g-3', 'b-6']
    for target in hand:
        print(encode_target(target))
