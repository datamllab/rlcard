

from rlcard.games.base import Card
import utils as utils


class BeloteJudger:
    
    @staticmethod
    def get_round_winner(round_cards):
        #initialise la couleur du round , la max carte et le winner avec le premier joueur
        round_color = round_cards[0][1].suit
        round_max_card_rank = round_cards[0][1]
        round_winner = round_cards[0][0]
        for (id,card) in round_cards:
            if(card.suit == round_color and utils.RANK_ORDER[round_max_card_rank.rank]<utils.RANK_ORDER[card.rank]):
                round_max_card_rank = card
                round_winner = id

        return(round_winner)


    @staticmethod
    def get_round_point(round_cards):
        score = 0
        for (id,card) in round_cards:
            score += utils.RANK_ORDER[card.rank]
        return score

    @staticmethod
    def judge_winner(players, np_random):
        ''' Judge the winner of the game

        Args:
            players (list): The list of players who play the game

        Returns:
            The player id of the winner
        '''
        #self.np_random = np_random

        if(players[0].score > players[1].score):
            return 0
        else:
            return 1

    @staticmethod
    def discover_secret(player,played_card):
        for i in range(len(player.table)):
            if(played_card.__eq__(player.table[i]) and len(player.secret[i])>0):
                player.table[i] = player.secret.pop()
                

    @staticmethod
    def get_playable_cards(player,round):
        ''' Get playable cards from a player

        Returns:
            set: set of string of playable cards
        '''
        same_color_card = set()
        same_color_and_higher_card = set()

        # si c'est le premier a jouer, il fait ce qu'il veut
        if round.round_cards == [] :
            return player.hand+player.table

        # boucle qui définit quelle carte peut etre jouer mais aussi si il possede des cartes de la meme couleur
        for card in player.hand:
            if card.suit == round.round_cards[0].suit :
                same_color_card.add(card)
                if utils.RANK_ORDER[card.rank] > utils.RANK_ORDER[round.round_cards[0].rank]:
                    same_color_and_higher_card.add(card)
        

        # Si il n'as ni pas de cartes plus hautes de la meme couleur
        if len(same_color_and_higher_card) ==0 :
            if len(same_color_card) ==0:
                return player.hand+player.table
                
            return same_color_card

    
  #For test
# if __name__ == '__main__':
    
#     round_card = [(0,Card('H','K')),(1,Card('S','A'))]
#     print("gagnant = "+BeloteJudger.get_round_winner(round_card).__str__())
#     print("score = "+BeloteJudger.get_round_point(round_card).__str__())