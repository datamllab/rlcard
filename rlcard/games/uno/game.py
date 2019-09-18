import random

from rlcard.games.uno.dealer import UnoDealer as Dealer
from rlcard.games.uno.player import UnoPlayer as Player
from rlcard.games.uno.round import UnoRound as Round


class UnoGame(object):

    def __init__(self):
        self.num_players = 4

    def init_game(self):
        # Initialize a dealer that can deal cards
        self.dealer = Dealer()

        # Initialize four players to play the game
        self.players = [Player(i) for i in range(self.num_players)]

        # Deal 7 cards to each player to prepare for the game
        for player in self.players:
            # print(player.get_player_id(), end=':')
            self.dealer.deal_cards(player, 7)
            # for card in player.hand:
            # print(card.get_str(), end=',')

        # Initialize a Round
        self.round = Round(self.dealer, self.num_players)

        # flip and perfrom top card
        top_card = self.round.flip_top_card()

        # print test
        print('top: ', top_card.get_str())
        self.round.perform_top_card(self.players, top_card)
        for player in self.players:
            player.print_hand()
        print(len(self.dealer.deck))
        # ##
        self.played_cards = []

    def step(self, action):
        self.round.proceed_round(self.players, action)
        print(self.round.current_player, end=': ')

    def get_legal_actions(self):

        return self.round.get_legal_actions(self.players, self.round.current_player)

    def get_player_num(self):
        return self.num_players

    @staticmethod
    def get_action_num():
        return 54

    def get_player_id(self):
        return self.round.current_player

    def is_over(self):
        if not self.players[self.round.current_player].hand:
            return True
        else:
            return False


if __name__ == '__main__':
    random.seed(0)
    game = UnoGame()
    game.init_game()
    print('*****init game*****')
    while not game.is_over():
        legal_actions = game.get_legal_actions()
        print(legal_actions)
        if not legal_actions:
            action = 'draw'
        else:
            action = random.choice(legal_actions)
        print(action)
        print()
        game.step(action)
