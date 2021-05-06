from rlcard.games.mahjong.utils import init_deck


class MahjongDealer:
    ''' Initialize a mahjong dealer class
    '''
    def __init__(self, np_random):
        self.np_random = np_random
        self.deck = init_deck()
        self.shuffle()
        self.table = []

    def shuffle(self):
        ''' Shuffle the deck
        '''
        self.np_random.shuffle(self.deck)

    def deal_cards(self, player, num):
        ''' Deal some cards from deck to one player

        Args:
            player (object): The object of DoudizhuPlayer
            num (int): The number of cards to be dealed
        '''
        for _ in range(num):
            player.hand.append(self.deck.pop())


## For test
#if __name__ == '__main__':
#    dealer = MahjongDealer()
#    for card in dealer.deck:
#        print(card.get_str())
#    print(len(dealer.deck))
