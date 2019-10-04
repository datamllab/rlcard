from rlcard.games.limitholdem.utils import *

class LimitholdemJudger(object):
    ''' The Judger class for Texas Hold'em
    '''

    def __init__(self):
        ''' Initialize a judger class
        '''
        super().__init__()

    @staticmethod
    def judge_game(players, hands):
        ''' Judge the winner of the game.

        Args:
            players (list): The list of players who play the game
            hands (list): The list of hands that from the players

        Returns:
            (list): Each entry of the list corresponds to one entry of the
        '''
        # Convert the hands into card indexes
        for i, hand in enumerate(hands):
            if hands[i] != None:
                h = [card.get_index() for card in hand]
                hands[i] = h

        #winners = compare_hands(hands)
        #winners = [1, 0, 0]
        winners = compare_hands(hands[0], hands[1])

        # Compute the total chips
        total = 0
        for p in players:
            total += p.in_chips

        each_win = float(total) / sum(winners)

        payoffs = []
        for i, _ in enumerate(players):
            if winners[i] == 1:
                payoffs.append(each_win - players[i].in_chips)
            else:
                payoffs.append(float(-players[i].in_chips))

        return payoffs
