from rlcard.utils import init_standard_deck


class BlackjackDealer(object):

    def __init__(self, np_random):
        ''' Initialize a Blackjack dealer class
        '''
        self.np_random = np_random
        self.deck = init_standard_deck()
        self.shuffle()
        self.hand = []
        self.status = 'alive'
        self.score = 0

    def shuffle(self):
        ''' Shuffle the deck
        '''
        self.np_random.shuffle(self.deck)

    def deal_card(self, player):
        ''' Distribute one card to the player

        Args:
            player_id (int): the target player's id
        '''
        card = self.deck.pop()
        player.hand.append(card)
