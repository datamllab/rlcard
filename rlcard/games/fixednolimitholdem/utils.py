# -*- coding: utf-8 -*-
"""Implement utils for no limit texas holdem"""

def get_card_id(suit, rank):
    """
    Get the card ID based on suit and rank
    
    Args:
        suit (str): The suit of the card ('S', 'H', 'D', 'C')
        rank (str): The rank of the card ('A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K')
        
    Returns:
        (int): The ID of the card
    """
    suit_list = ['S', 'H', 'D', 'C']
    rank_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    
    suit_index = suit_list.index(suit)
    rank_index = rank_list.index(rank)
    
    return rank_index + 13 * suit_index

# get_card_from_id
def get_card_from_id(card_id):
    """
    Get a Card object from a card ID
    
    Args:
        card_id (int): The ID of the card
        
    Returns:
        (Card): A Card object
    """
    suit_list = ['S', 'H', 'D', 'C']
    rank_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    
    suit_index = card_id // 13
    rank_index = card_id % 13
    
    return Card(suit_list[suit_index], rank_list[rank_index])

