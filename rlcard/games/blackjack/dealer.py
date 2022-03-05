from rlcard.utils import init_standard_deck
import numpy as np

class BlackjackDealer:

    def __init__(self, np_random, num_decks=1):
        ''' Initialize a Blackjack dealer class
        '''
        self.np_random = np_random
        self.num_decks = num_decks
        self.deck = init_standard_deck()
        if self.num_decks not in [0, 1]:  # 0 indicates infinite decks of cards
            self.deck = self.deck * self.num_decks  # copy m standard decks of cards
        self.shuffle()
        self.hand = []
        self.status = 'alive'
        self.score = 0

    def shuffle(self):
        ''' Shuffle the deck
        '''
        shuffle_deck = np.array(self.deck)
        self.np_random.shuffle(shuffle_deck)
        self.deck = list(shuffle_deck)

    def deal_card(self, player):
        ''' Distribute one card to the player

        Args:
            player_id (int): the target player's id
        '''
        idx = self.np_random.choice(len(self.deck))
        card = self.deck[idx]
        if self.num_decks != 0:  # If infinite decks, do not pop card from deck
            self.deck.pop(idx)
        # card = self.deck.pop()
        player.hand.append(card)
