''' Doudizhu utils
'''

import os
import json
from collections import OrderedDict
import threading
import collections

import rlcard

# Read required docs
ROOT_PATH = rlcard.__path__[0]

# a map of action to abstract action
with open(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/specific_map.json'), 'r') as file:
    SPECIFIC_MAP = json.load(file, object_pairs_hook=OrderedDict)

# a map of abstract action to its index and a list of abstract action
with open(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/action_space.json'), 'r') as file:
    ACTION_SPACE = json.load(file, object_pairs_hook=OrderedDict)
    ACTION_LIST = list(ACTION_SPACE.keys())

# a map of card to its type. Also return both dict and list to accelerate
with open(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/card_type.json'), 'r') as file:
    data = json.load(file, object_pairs_hook=OrderedDict)
    CARD_TYPE = (data, list(data), set(data))

# a map of type to its cards
with open(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/type_card.json'), 'r') as file:
    TYPE_CARD = json.load(file, object_pairs_hook=OrderedDict)

# rank list of solo character of cards
CARD_RANK_STR = ['3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K',
                 'A', '2', 'B', 'R']
CARD_RANK_STR_INDEX = {'3': 0, '4': 1, '5': 2, '6': 3, '7': 4,
            '8': 5, '9': 6, 'T': 7, 'J': 8, 'Q': 9,
            'K': 10, 'A': 11, '2': 12, 'B': 13, 'R': 14}
# rank list
CARD_RANK = ['3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K',
             'A', '2', 'BJ', 'RJ']

INDEX = {'3': 0, '4': 1, '5': 2, '6': 3, '7': 4,
         '8': 5, '9': 6, 'T': 7, 'J': 8, 'Q': 9,
         'K': 10, 'A': 11, '2': 12, 'B': 13, 'R': 14}
INDEX = OrderedDict(sorted(INDEX.items(), key=lambda t: t[1]))


def doudizhu_sort_str(card_1, card_2):
    ''' Compare the rank of two cards of str representation

    Args:
        card_1 (str): str representation of solo card
        card_2 (str): str representation of solo card

    Returns:
        int: 1(card_1 > card_2) / 0(card_1 = card2) / -1(card_1 < card_2)
    '''
    key_1 = CARD_RANK_STR.index(card_1)
    key_2 = CARD_RANK_STR.index(card_2)
    if key_1 > key_2:
        return 1
    if key_1 < key_2:
        return -1
    return 0


def doudizhu_sort_card(card_1, card_2):
    ''' Compare the rank of two cards of Card object

    Args:
        card_1 (object): object of Card
        card_2 (object): object of card
    '''
    key = []
    for card in [card_1, card_2]:
        if card.rank == '':
            key.append(CARD_RANK.index(card.suit))
        else:
            key.append(CARD_RANK.index(card.rank))
    if key[0] > key[1]:
        return 1
    if key[0] < key[1]:
        return -1
    return 0


def get_landlord_score(current_hand):
    ''' Roughly judge the quality of the hand, and provide a score as basis to
    bid landlord.

    Args:
        current_hand (str): string of cards. Eg: '56888TTQKKKAA222R'

    Returns:
        int: score
    '''
    score_map = {'A': 1, '2': 2, 'B': 3, 'R': 4}
    score = 0
    # rocket
    if current_hand[-2:] == 'BR':
        score += 8
        current_hand = current_hand[:-2]
    length = len(current_hand)
    i = 0
    while i < length:
        # bomb
        if i <= (length - 4) and current_hand[i] == current_hand[i+3]:
            score += 6
            i += 4
            continue
        # 2, Black Joker, Red Joker
        if current_hand[i] in score_map:
            score += score_map[current_hand[i]]
        i += 1
    return score


def get_optimal_action(probs, legal_actions, np_random):
    ''' Determine the optimal action from legal actions
    according to the probabilities of abstract actions.

    Args:
        probs (list): list of probabilities of abstract actions
        legal_actions (list): list of legal actions

    Returns:
        str: optimal legal action
    '''
    abstract_actions = [SPECIFIC_MAP[action] for action in legal_actions]
    action_probs = []
    for actions in abstract_actions:
        max_prob = -1
        for action in actions:
            prob = probs[ACTION_SPACE[action]]
            if prob > max_prob:
                max_prob = prob
        action_probs.append(max_prob)
    optimal_prob = max(action_probs)
    optimal_actions = [legal_actions[index] for index,
                       prob in enumerate(action_probs) if prob == optimal_prob]
    if len(optimal_actions) > 1:
        return np_random.choice(optimal_actions)
    return optimal_actions[0]


def cards2str_with_suit(cards):
    ''' Get the corresponding string representation of cards with suit

    Args:
        cards (list): list of Card objects

    Returns:
        string: string representation of cards
    '''
    return ' '.join([card.suit+card.rank for card in cards])

def cards2str(cards):
    ''' Get the corresponding string representation of cards

    Args:
        cards (list): list of Card objects

    Returns:
        string: string representation of cards
    '''
    response = ''
    for card in cards:
        if card.rank == '':
            response += card.suit[0]
        else:
            response += card.rank
    return response

class LocalObjs(threading.local):
    def __init__(self):
        self.cached_candidate_cards = None
_local_objs = LocalObjs()

def contains_cards(candidate, target):
    ''' Check if cards of candidate contains cards of target.

    Args:
        candidate (string): A string representing the cards of candidate
        target (string): A string representing the number of cards of target

    Returns:
        boolean
    '''
    # In normal cases, most continuous calls of this function
    #   will test different targets against the same candidate.
    # So the cached counts of each card in candidate can speed up
    #   the comparison for following tests if candidate keeps the same.
    if not _local_objs.cached_candidate_cards or _local_objs.cached_candidate_cards != candidate:
        _local_objs.cached_candidate_cards = candidate
        cards_dict = collections.defaultdict(int)
        for card in candidate:
            cards_dict[card] += 1
        _local_objs.cached_candidate_cards_dict = cards_dict
    cards_dict = _local_objs.cached_candidate_cards_dict
    if (target == ''):
        return True
    curr_card = target[0]
    curr_count = 1
    for card in target[1:]:
        if (card != curr_card):
            if (cards_dict[curr_card] < curr_count):
                return False
            curr_card = card
            curr_count = 1
        else:
            curr_count += 1
    if (cards_dict[curr_card] < curr_count):
        return False
    return True

def encode_cards(plane, cards):
    ''' Encode cards and represerve it into plane.

    Args:
        cards (list or str): list or str of cards, every entry is a
    character of solo representation of card
    '''
    if not cards:
        return None
    layer = 1
    if len(cards) == 1:
        rank = CARD_RANK_STR.index(cards[0])
        plane[layer][rank] = 1
        plane[0][rank] = 0
    else:
        for index, card in enumerate(cards):
            if index == 0:
                continue
            if card == cards[index-1]:
                layer += 1
            else:
                rank = CARD_RANK_STR.index(cards[index-1])
                plane[layer][rank] = 1
                layer = 1
                plane[0][rank] = 0
        rank = CARD_RANK_STR.index(cards[-1])
        plane[layer][rank] = 1
        plane[0][rank] = 0


def get_gt_cards(player, greater_player):
    ''' Provide player's cards which are greater than the ones played by
    previous player in one round

    Args:
        player (DoudizhuPlayer object): the player waiting to play cards
        greater_player (DoudizhuPlayer object): the player who played current biggest cards.

    Returns:
        list: list of string of greater cards

    Note:
        1. return value contains 'pass'
    '''
    # add 'pass' to legal actions
    gt_cards = ['pass']
    current_hand = cards2str(player.current_hand)
    target_cards = greater_player.played_cards
    target_types = CARD_TYPE[0][target_cards]
    type_dict = {}
    for card_type, weight in target_types:
        if card_type not in type_dict:
            type_dict[card_type] = weight
    if 'rocket' in type_dict:
        return gt_cards
    type_dict['rocket'] = -1
    if 'bomb' not in type_dict:
        type_dict['bomb'] = -1
    for card_type, weight in type_dict.items():
        candidate = TYPE_CARD[card_type]
        for can_weight, cards_list in candidate.items():
            if int(can_weight) > int(weight):
                for cards in cards_list:
                    # TODO: improve efficiency
                    if cards not in gt_cards and contains_cards(current_hand, cards):
                        # if self.contains_cards(current_hand, cards):
                        gt_cards.append(cards)
    return gt_cards


# Test json order
#if __name__ == '__main__':
#    for action, index in ACTION_SPACE.items():
#        if action != ACTION_LIST[index]:
#            print('order error')
