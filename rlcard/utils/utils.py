import random
import numpy as np

from rlcard.core import Card, Player

def init_standard_deck():
    ''' Initialize a standard deck of 52 cards

    Returns:
        (list): A list of Card object
    '''

    suit_list = ['S', 'H', 'D', 'C']
    rank_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    res = [Card(suit, rank) for suit in suit_list for rank in rank_list]
    return res

def init_54_deck():
    ''' Initialize a standard deck of 52 cards, BJ and RJ

    Returns:
        (list): Alist of Card object
    '''

    suit_list = ['S', 'H', 'D', 'C']
    rank_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    res = [Card(suit, rank) for suit in suit_list for rank in rank_list]
    res.append(Card('BJ', ''))
    res.append(Card('RJ', ''))
    return res


def get_random_cards(cards, num, seed=None):
    ''' Randomly get a number of chosen cards out of a list of cards

    Args:
        cards (list): List of Card object
        num (int): The  number of cards to be chosen
        seed (int): Optional, random seed

    Returns:
        (list): A list of chosen cards
        (list): A list of remained cards
    '''

    if not num> 0:
        raise AssertionError('Invalid input number')
    if not num <= len(cards):
        raise AssertionError('Input number larger than length of cards')
    remained_cards = []
    chosen_cards = []
    remained_cards = cards.copy()
    random.Random(seed).shuffle(remained_cards)
    chosen_cards = remained_cards[:num]
    remained_cards = remained_cards[num:]
    return chosen_cards, remained_cards

def is_pair(cards):
    ''' Check whether the card is a pair

    Args:
        cards (list): A list of Card object

    Returns:
        (boolean): True if the list is a pair
    '''

    if len(cards) == 2 and cards[0].rank == cards[1].rank:
        return True
    else:
        return False

def is_single(cards):
    ''' Check whether the card is singel

    Args:
        cards (list): A list of Card object

    Returns:
        (boolean): True if the list is single
    '''
    if len(cards) == 1:
        return True
    else:
        return False

def rank2int(rank):
    ''' Get the coresponding number of a rank.

    Args:
        rank(str): rank stored in Card object

    Returns:
        (int): the number corresponding to the rank

    Note:
        1. If the input rank is an empty string, the function will return -1.
        2. If the input rank is not valid, the function will return None.
    '''

    if rank == '':
        return -1
    elif rank.isdigit():
        if int(rank) >= 2 and int(rank) <= 10:
            return int(rank)
        else:
            return None
    elif rank == 'A':
        return 14
    elif rank == 'T':
        return 10
    elif rank == 'J':
        return 11
    elif rank == 'Q':
        return 12
    elif rank == 'K':
        return 13
    return None

def get_cards_from_ranks(player, ranks):
    ''' Get chosen cards and remained cards from a player's hand according to input rank list

    Args:
        player (Player): Player object
        ranks (list): A list of rank (string)

    Returns:
        (tupel): Tuple containing:
            (list): A list of Card objects, chosen cards
            (list): A list of Card objects, remained cards

    Note: This function will not affect the player's original hand.
    '''

    chosen_cards = []
    remained_cards = player.hand.copy()
    for rank in ranks:
        for card in remained_cards:
            if card.rank == rank:
                chosen_cards.append(card)
                remained_cards.pop(remained_cards.index(card))
    return chosen_cards, remained_cards

def take_out_cards(cards, remove_cards):
    ''' Take out specific cards from a list of cards

    Args:
        cards (list): A list of Card objects from which to be taken out some cards
        remove_cards (list): A list of Card objects that need to be taken out

    Returns:
        (list): A list of Card objects. The cards in 'remove_cards' list that doesn't make cards in 'cards' list taken out

    Note:
        1. This function will affect the first input Card list,
        but will not affect the second input Card list.
        2. For each card in 'remove_cards' list, it will make only one card in 'cards' list taken out,
        which means to take out one kind of cards with the same suit and rank in 'cards' list,
        you need to have the same number of cards with the same suit and rank in 'remove_cards' list.
    '''

    remove_cards_cp = remove_cards
    for card in cards:
        for remove_card in remove_cards_cp:
            if card.rank == remove_card.rank and card.suit == remove_card.suit:
                cards.pop(cards.index(card))
                remove_cards_cp.pop(remove_cards_cp.index(remove_card))
    return remove_cards_cp

def is_in_cards(origin_cards, check_cards):
    ''' Check if a list of Card objects contains another list of Card objects

    Args:
        cards (list): A list of Card objects which to be checked if it contains another list of Card objects
        check_cards (list): A list of Card objects which to be checked if it is in a list of Card objecrts

    Returns:
        (boolean): True if the cards are in the original cards.
    '''

    check_cards_cp = check_cards.copy()
    cards = origin_cards.copy()
    i = 0
    while i < len(check_cards_cp):
        j = 0
        while j < len(cards):
            if cards[j].rank == check_cards_cp[i].rank and cards[j].suit == check_cards_cp[i].suit:
                cards.pop(j)
                check_cards_cp.pop(i)
                if(len(cards) == 0 or len(check_cards_cp) == 0):
                    break
                j -= 1
            j += 1
        if(len(cards) == 0 or len(check_cards_cp) == 0):
            break
        i += 1
    return len(check_cards_cp) == 0

def init_players(n):
    ''' Initilize a list of Player objects with n players

    Args:
        n (int): The number of players to be initialized

    Returns:
        (list): A list of Player objects with player_id(s) start from 0 and are consequent
    '''

    players = []
    for idx in range(n):
        players.append(Player(idx))
    return players

def get_upstream_player_id(player, players):
    ''' Obtain the upsteam player's player_id

    Args:
        player (Player): The current player
        players (list): A list of players

    Note: This function assumes player_id(s) in 'players' list starts from 0, and are consequent.
    '''
    return (player.player_id-1)%len(players)

def get_downstream_player_id(player, players):
    ''' Obtain the downsteam player's player_id

    Args:
        player (Player): The current player
        players (list): A list of players

    Note: This function assumes player_id(s) in 'players' list start from 0, and are consequent.
    '''

    return (player.player_id+1)%len(players)

def reorganize(trajectories, payoffs):
    ''' Reorganize the trajectory to make it RL friendly

    Args:
        trajectory (list): A list of trajectories
        payoffs (list): A list of payoffs for the players. Each entry corresponds to one player

    Returns:
        (list): A new trajectories that can be fed into RL algorithms.

    '''

    player_num = len(trajectories)
    new_trajectories = [[] for _ in range(player_num)]

    for player in range(player_num):
        for i in range(0, len(trajectories[player])-2, 2):
            if i ==len(trajectories[player])-3:
                reward = payoffs[player]
                done =True
            else:
                reward, done = 0, False
            transition = trajectories[player][i:i+3].copy()
            transition.insert(2, reward)
            transition.append(done)

            new_trajectories[player].append(transition)
    return new_trajectories

def set_global_seed(seed):
    ''' Set the global see for reproducing results

    Args:
        seed (int): The seed

    Note: If using other modules with randomness, they also need to be seeded
    '''

    if seed is not None:
        import tensorflow as tf
        tf.set_random_seed(seed)
        np.random.seed(seed)
        random.seed(seed)

def remove_illegal(action_probs, legal_actions):
    ''' Remove illegal actions and normalize the
        probability vector

    Args:
        action_probs (numpy.array): A 1 dimention numpy array.
        legal_actions (list): A list of indices of legal actions.

    Returns:
        probd (numpy.array): A normalized vector without legal actions.
    '''

    probs = np.zeros(action_probs.shape[0])
    probs[legal_actions] = action_probs[legal_actions]
    probs /= sum(probs)
    return probs

