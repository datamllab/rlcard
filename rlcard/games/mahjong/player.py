from rlcard.games.uno.utils import cards2list

class MahjongPlayer(object):

    def __init__(self, player_id):
        ''' Initilize a player.

        Args:
            player_id (int): The id of the player
        '''
        self.player_id = player_id
        self.hand = []
        self.pile = []

    def get_player_id(self):
        ''' Return the id of the player
        '''

        return self.player_id

    def print_hand(self):
        for card in self.hand:
            print(card.get_str(), end=' ')

    def play_card(self, dealer, card):
        card = self.hand.pop(self.hand.index(card))
        dealer.table.append(card)

    def chow(self, dealer, cards):
        for card in cards:
            if card in self.hand:
                self.hand.pop(cards[i])
        self.pile.append(cards)

    def gong(self, dealer, cards):
        for card in cards:
            if card in self.hand:
                self.hand.pop(cards[i])
        self.pile.append(cards)

    def pong(self, dealer, cards):
        for card in cards:
            if card in self.hand:
                self.hand.pop(cards[i])
        self.pile.append(cards)
