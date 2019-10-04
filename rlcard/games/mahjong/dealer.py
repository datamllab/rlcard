import random
from rlcard.games.mahjong.card import MahjongCard as Card
from rlcard.games.mahjong.utils import *


class MahjongDealer(object):
    ''' Initialize a mahjong dealer class
    '''
    def __init__(self):
        self.deck = init_deck()
        self.shuffle()
        self.table = []

    def shuffle(self):
        random.shuffle(self.deck)

    def deal_cards(self, player, num):
        for _ in range(num):
            player.hand.append(self.deck.pop())


# For test
if __name__ == '__main__':
    dealer = MahjongDealer()
    for card in dealer.deck:
        print(card.get_str())
    print(len(dealer.deck))
