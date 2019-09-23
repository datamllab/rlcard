import random
from rlcard.games.mahjong.card import MahjongCard as Card


class MahjongDealer(object):
    ''' Initialize a mahjong dealer class
    '''
    def __init__(self):
        self.deck = self.init_wall()
        self.shuffle()
        self.table = []

    def init_wall(self):
        deck = []
        info = Card.info 
        for _type in info['type']:
            if _type != 'dragons' and _type != 'winds':
                for _trait in info['trait'][:9]:
                    card = Card(_type, _trait)
                    deck.append(card)
            elif _type == 'dragons':
                for _trait in info['trait'][9:12]:
                    card = Card(_type, _trait)
                    deck.append(card)
            else:
                for _trait in info['trait'][12:]:
                    card = Card(_type, _trait)
                    deck.append(card)
        deck = deck * 4
        return deck
        
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
