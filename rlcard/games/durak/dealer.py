from rlcard.utils import init_standard_deck
import numpy as np

class DurakDealer:

    def __init__(self, np_random):
        ''' Initialize a Durak dealer class
        '''
        self.np_random = np_random
        self.deck = init_standard_deck()
        self.shuffle()
        self.determine_trump_suit()

    def shuffle(self):
        self.np_random.shuffle(self.deck)

    def deal_card(self):
        """
        Deal one card from the deck
        Returns:
            (Card): The drawn card from the deck
        """
        return self.deck.pop(0)

    def determine_trump_suit(self):
        self.trump_suit = self.deck[-1].suit

    def empty(self):
        return len(self.deck) == 0