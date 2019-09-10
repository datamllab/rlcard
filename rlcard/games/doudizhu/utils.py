'''doudizhu utils'''
import os
import json
import random
import rlcard

# Read required docs
ROOT_PATH = rlcard.__path__[0]

# a map of action to abstract action
with open(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/specific_map.json'), 'r') as file:
    SPECIFIC_MAP = json.load(file)

# a map of abstract action to its index and a list of abstract action
with open(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/action_space.json'), 'r') as file:
    ACTION_SPACE = json.load(file)
    ACTION_LIST = list(ACTION_SPACE.keys())

# a map of card to its type
with open(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/card_type.json'), 'r') as file:
    CARD_TYPE = json.load(file)

# a map of type to its cards
with open(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/type_card.json'), 'r') as file:
    TYPE_CARD = json.load(file)

# rank list of solo character of cards
CARD_RANK_STR = ['3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K',
                 'A', '2', 'B', 'R']
# rank list
CARD_RANK = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K',
             'A', '2', 'BJ', 'RJ']


def doudizhu_sort_str(card_1, card_2):
    '''Compare the rank of two cards of str representation

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
    '''Compare the rank of two cards of Card object

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


def get_landlord_score(remaining):
    '''Roughly judge the quality of the hand, and provide a score as basis to
    bid landlord.

    Args:
        remaining (str): string of cards. Eg: '56888TTQKKKAA222R'

    Returns:
        int: score
    '''
    score_map = {'A': 1, '2': 2, 'B': 3, 'R': 4}
    score = 0
    # rocket
    if remaining[-2:] == 'BR':
        score += 8
        remaining = remaining[:-2]
    length = len(remaining)
    i = 0
    while i < length:
        # bomb
        if i <= (length - 4) and remaining[i] == remaining[i+3]:
            score += 6
            i += 4
            continue
        # 2, Black Joker, Red Joker
        if remaining[i] in score_map:
            score += score_map[remaining[i]]
        i += 1
    return score


def get_optimal_action(probs, legal_actions):
    '''Determine the optimal action from legal actions
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
        return random.choice(optimal_actions)
    return optimal_actions[0]


def cards2str(cards: list):
    '''Get the corresponding string representation of cards

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
            if card.rank == '10':
                response += 'T'
            else:
                response += card.rank
    return response


def contains_cards(candidate, target):
    '''Check if cards of candidate contains cards of target.

    Args:
        candidate (string): string represent of cards of candidate
        target (string): string represent of cards of target

    Returns:
        boolean
    '''
    len_can = len(candidate)
    len_tar = len(target)
    if len_can < len_tar:
        return False
    if len_can == len_tar:
        if candidate == target:
            return True
        return False
    beg = 0
    for tar_card in target:
        beg = candidate.find(tar_card, beg) + 1
        if beg == 0:
            return False
    return True
