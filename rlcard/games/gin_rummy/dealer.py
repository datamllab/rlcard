'''
    File name: gin_rummy/dealer.py
    Author: William Hale
    Date created: 2/12/2020
'''

import random

from rlcard.games.gin_rummy.card import Card, get_deck
from rlcard.games.gin_rummy.player import GinRummyPlayer

from typing import List


class GinRummyDealer(object):
    ''' Initialize a GinRummy dealer class
    '''
    def __init__(self):
        ''' Empty discard_pile, set shuffled_deck, set stock_pile
        '''
        self.discard_pile: List[Card] = []
        self.shuffled_deck = get_deck().copy()  # keep a copy of the shuffled cards at start of new hand
        random.shuffle(self.shuffled_deck)
        self.stock_pile: List[Card] = self.shuffled_deck.copy()

    def deal_cards(self, player: GinRummyPlayer, num: int):
        ''' Deal some cards from stock_pile to one player

        Args:
            player (GinRummyPlayer): The GinRummyPlayer object
            num (int): The number of cards to be dealt
        '''
        for _ in range(num):
            player.hand.append(self.stock_pile.pop())


# For test

def test_gin_rummy_dealer():
    dealer = GinRummyDealer()
    current_deck = get_deck()
    deck_text = [card.rank + card.suit for card in current_deck]
    deck_card_ids = [card.card_id for card in current_deck]
    print(f"deck={deck_text}")
    print(deck_card_ids)
    print(f"Deal 10 cards.")
    player = GinRummyPlayer(player_id=0)
    dealer.deal_cards(player=player, num=10)
    print(f"shuffled_deck_count={len(dealer.shuffled_deck)}")
    print(f"stock_pile_count={len(dealer.stock_pile)}")
    print(f"current_deck_count={len(current_deck)}")
    print(f"new_deck_count={len(get_deck())}")

    print(f"Pop top_card from current_deck.")
    top_card = current_deck.pop(-1)
    print(f"top_card={top_card} current_deck_count={len(current_deck)} new_deck_count={len(get_deck())}")


if __name__ == '__main__':
    test_gin_rummy_dealer()
