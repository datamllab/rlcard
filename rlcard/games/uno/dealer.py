import random

from rlcard.games.uno.utils import init_deck


class UnoDealer(object):
    ''' Initialize a uno dealer class
    '''
    def __init__(self):
        self.deck = init_deck()
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.deck)

    def deal_cards(self, player, num):
        for _ in range(num):
            player.hand.append(self.deck.pop())

    def flip_top_card(self):
        top_card = self.deck.pop()
        while top_card.trait == 'wild_draw_4':
            self.deck.append(top_card)
            self.shuffle()
            top_card = self.deck.pop()
        return top_card

# For test
if __name__ == '__main__':
    dealer = UnoDealer()
    for card in dealer.deck:
        print(card.get_str())
    print(len(dealer.deck))
