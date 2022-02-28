
import dealer
import player
import numpy as np


class BeloteRound:
    def __init__(self, np_random, played_cards):
        self.np_random = np_random
        self.played_cards = played_cards
        self.trace = []

        self.dealer = dealer.BeloteDealer(np_random)
        # self.deck_str = cards2str(self.dealer.deck)

    def initiate(self, players):
        ''' Call dealer to deal cards.

        Args:
            players (list): list of BelotePlayer objects
        '''

        for i in range(2):
            self.dealer.deal_cards(players[i], 0)
            #print("Main joueur "+i.__str__())
            #for card in players[i].hand:
            #    print(card.__str__())
            #print("Table joueur "+i.__str__())
            #for card in players[i].table:
            #    print(card.__str__())

            #print("Secret joueur "+i.__str__())
            #for card in players[i].secret:
            #    print(card.__str__())

        # il reste a implémenter ici le choix de l'atout

    def proceed_round(self, player, action):
        ''' Call other Classes's functions to keep one round running

        Args:
            player (object): object of DoudizhuPlayer
            action (str): string of legal specific action

        Returns:
            object of BelotePlayer: player who played current biggest cards.
        '''

  # For test
if __name__ == '__main__':
    np_random = np.random.RandomState()
    players = []
    players.append(player.BelotePlayer(0, np_random))
    players.append(player.BelotePlayer(1, np_random))
    round = BeloteRound(np_random, [])
    round.initiate(players)
