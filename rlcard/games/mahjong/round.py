import random


class MahjongRound(object):

    def __init__(self, dealer, num_players):
        self.dealer = dealer
        self.target = None
        self.current_player = 0
        self.num_players = num_players
        self.direction = 1
        self.played_cards = []
        self.is_over = False

