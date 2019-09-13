from rlcard.core import Judger
from rlcard.games.limitholdem.utils import *

class LimitholdemJudger(Judger):
    def __init__(self):
        ''' Initialize a judger class
        '''
        
        super().__init__()
    
    def judge_game(self, players, hands):
        ''' Judge the winner of the game TTTTODO: the payoffs are not corect, we need to calculate the chips

        Args:
            game (class): target game class

        Note: Current it only judges two players. Need to be modified to adapt to more players
        '''

        # Transfer them to index
        for i in range(len(hands)):
            if hands[i] != None:
                h = [card.get_index() for card in hands[i]]
                hands[i] = h

        #print('Hands: ', hands)
        winners = compare_hands(hands[0], hands[1])
        total = 0
        for p in players:
            total += p.in_chips

        each_win = float(total) / sum(winners)

        payoffs = []
        for i in range(len(players)):
            if winners[i] == 1:
                payoffs.append(each_win-players[i].in_chips)
            else:
                payoffs.append(float(-players[i].in_chips))

        return payoffs





        
