

from rlcard.games.base import Card
import utils as utils


class BeloteJudger:
    

    @staticmethod
    def judge_winner(players, np_random):
        ''' Judge the winner of the game

        Args:
            players (list): The list of players who play the game

        Returns:
            The player id of the winner
        '''
        #self.np_random = np_random

        if(players[0].score > players[1]):
            return 0
        else:
            return 1

    @staticmethod
    def get_playable_cards(player,round):
        ''' Get playable cards from a player

        Returns:
            set: set of string of playable cards
        '''
        same_color_card = set()
        same_color_and_higher_card = set()

        # si c'est le premier a jouer, il fait ce qu'il veut
        if round.trace == [] :
            return player.hand+player.table

        # boucle qui définit quelle carte peut etre jouer mais aussi si il possede des cartes de la meme couleur
        for card in player.hand:
            if card.suit == round.trace[0].suit :
                same_color_card.add(card)
                if utils.RANK_ORDER[card.rank] > utils.RANK_ORDER[round.trace[0].rank]:
                    same_color_and_higher_card.add(card)
        

        # Si il n'as ni pas de cartes plus hautes de la meme couleur
        if len(same_color_and_higher_card) ==0 :
            if len(same_color_card) ==0:
                return player.hand+player.table
                
            return same_color_card

    
