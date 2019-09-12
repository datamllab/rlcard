from rlcard.core import Judger

class LimitholdemJudger(Judger):
    def __init__(self):
        ''' Initialize a judger class
        '''
        pass
    


    def judge_game(self, game):
        ''' Judge the winner of the game

        Args:
            game (class): target game class
        '''

        if game.player0.status == 'bust':
            game.winner['player1'] = 1
        elif game.player1.status == 'bust':
            game.winner['player0'] = 1
        else:
            if game.player0.score > game.player1.score:
                game.winner['player0'] = 1
            elif game.player0.score < game.player1.score:
                game.winner['player1'] = 1
            else:
                game.winner['player0'] = 1
                game.winner['player1'] = 1




        
