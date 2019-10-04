import numpy as np
from rlcard.games.mahjong.card import MahjongCard as Card


card_encoding_dict = {}
num = 0
for _type in ['bamboo', 'characters', 'dots']:
    for _trait in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
        card = _type+"-"+_trait
        card_encoding_dict[card] = num
        num += 1
for _trait in ['green', 'red', 'white']:
    card = 'dragons-'+_trait
    card_encoding_dict[card] = num
    num += 1

for _trait in ['east', 'west', 'north', 'south']:
    card = 'winds-'+_trait
    card_encoding_dict[card] = num
    num += 1

def init_deck():
    deck = []
    info = Card.info 
    for _type in info['type']:
        if _type != 'dragons' and _type != 'winds':
            for _trait in info['trait'][:9]:
                card = Card(_type, _trait)
                deck.append(card)
        elif _type == 'dragons':
            for _trait in info['trait'][9:12]:
                card = Card(_type, _trait)
                deck.append(card)
        else:
            for _trait in info['trait'][12:]:
                card = Card(_type, _trait)
                deck.append(card)
    deck = deck * 4
    return deck


def pile2list(pile):
    cards_list = []
    for each in pile:
        cards_list.extend(each)
    return cards_list

def cards2list(cards):
    cards_list = []
    for each in cards:
        cards_list.append(each.get_str())
    return cards_list


def encode_cards(cards):
    plane = np.zeros((34,4), dtype=int)
    cards = cards2list(cards)
    for card in list(set(cards)):
        index = card_encoding_dict[card]
        num = cards.count(card)
        plane[index][:num] = 1
    return plane 
