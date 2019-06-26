import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from functools import reduce
import random
from core import Card, Player

def init_standard_deck():
    ''' Return a list of Card objects which form a standard 52 cards deck
    '''
    suit_list = ['S', 'H', 'D', 'C']
    rank_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    res = [Card(suit, rank) for suit in suit_list for rank in rank_list]
    return res

def init_54_deck():
    ''' Return a list of Card objects which include a standard 52 cards deck, BJ and RJ
    '''
    suit_list = ['S', 'H', 'D', 'C']
    rank_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    res = [Card(suit, rank) for suit in suit_list for rank in rank_list]
    res.append(Card('BJ', ''))
    res.append(Card('RJ', ''))
    return res

def get_random_cards(cards, num, seed = None):
    ''' Randomly get a number of chosen cards out of a list of cards

    Args:
        cards: list of Card object
        num: int, number of cards to be chosen
        seed: int, optional, random seed

    Return:
        list: list of chosen cards
        list: list of remained cards
    '''
    assert num > 0, "Invalid input number"
    assert num <= len(cards), "Input number larger than length of cards"
    remained_cards = []
    chosen_cards = []
    remained_cards = cards.copy()
    random.Random(seed).shuffle(remained_cards)
    chosen_cards = remained_cards[:num]
    remained_cards = remained_cards[num:]
    return chosen_cards, remained_cards

def is_pair(cards):
    '''
    Arg:
        cards: list of Card object

    Return:
        boolean: whether the input list is a pair or not
    '''
    if len(cards) == 2 and cards[0].rank == cards[1].rank:
        return True
    else:
        return False

def is_single(cards):
    '''
    Arg:
        cards: list of Card object
    
    Return:
        boolean: whether the input list is a single card or not
    '''
    if len(cards) == 1:
        return True
    else:
        return False

def rank2int(rank):
    ''' Get the coresponding number of a rank.
    Arg:
        rank: rank stored in Card object
    
    Return:
        int: the number corresponding to the rank

    Note:
        If the input rank is an empty string, the function will return -1.
        If the input rank is not valid, the function will return None.
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
    ''' get chosen cards and remained cards from a player's hand according to input rank list
    Args:
        player: Player object
        ranks: list of rank(string)

    Return:
        list of Card objects: chosen cards
        list of Card objects: remained cards

    Note:
        This function will not affect the player's original hand.
    '''
    chosen_cards = []
    remained_cards = player.hand.copy()
    for rank in ranks:
        for card in remained_cards:
            if card.rank == rank:
                chosen_cards.append(card)
                remained_cards.pop(remained_cards.index(card))
    return chosen_cards, remained_cards

def init_players(n):
    ''' Return a list of Player objects with n players
    Arg:
        n: int, number of players to be initialized
    
    Return:
        list of Player objects
    '''
    players = []
    for idx in range(n):
        players.append(Player(idx))
    return players

def get_upstream_player_id(player, players):
    return (player.player_id-1)%len(players)

def get_downstream_player_id(player, players):
    return (player.player_id+1)%len(players)