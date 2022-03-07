
from random import choice

from matplotlib.cbook import print_cycles
import judger
import player
import dealer
import numpy as np

from rlcard.games.base import Card
from utils import print_card


class BeloteRound:
    def __init__(self, np_random, round_cards):
        self.np_random = np_random
        self.round_cards = round_cards



    def proceed_round(self, player,round_cards):
        ''' Call other Classes's functions to keep one round running

        Args:
            player (object): object of DoudizhuPlayer
            action (str): string of legal specific action

        Returns:
            object of BelotePlayer: player who played current biggest cards.
        '''
        print("Etat du pli :\n")
        print_card(round_cards)
    
        print("Tour du joueur "+player.player_id.__str__() + ":")
        cards = judger.BeloteJudger.get_playable_cards(player,self)

        print("Tu as : "+len(player.hand).__str__()+" cartes en main \n")
        print_card(player.hand)
        print("Tu as : "+len(player.table).__str__()+" cartes face visible \n")
        print_card(player.table)
        print("Tu as : "+len(player.secret).__str__()+" cartes face cachée \n")

        print("Tu peux jouer\n")
        print_card(cards)
            

        print("Choisis ta carte en entrant son numero en commençant par 0\n")
        choix = int(input())
        print("Tu as joué :\n")
        print_card([cards[choix]])
        round_cards.append(cards[choix])
        judger.BeloteJudger.discover_secret(player,cards[choix])
        #remove la carte du jeu du joueur apres l'avoir jouer
        player.remove_card(cards[choix])
        #Pour le test faut decommenter en dessous
        #return(round_cards)


  # For test
if __name__ == '__main__':
     np_random = np.random.RandomState()
     deal = dealer.BeloteDealer(np_random)
     players = []
     players.append(player.BelotePlayer(0, np_random))
     players.append(player.BelotePlayer(1, np_random))
     for i in range(2):
            deal.deal_cards(players[i], 0)
     round = BeloteRound(np_random, [])
     trace =round.proceed_round(players[0],[])
     round.proceed_round(players[1],trace)
