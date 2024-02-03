
class UnoJudger:

    @staticmethod
    def judge_winner(players, np_random):
        ''' Judge the winner of the game

        Args:
            players (list): The list of players who play the game

        Returns:
            (list): The player id of the winner
        '''
        self.np_random = np_random
        count_1 = len(players[0].hand)
        count_2 = len(players[1].hand)
        if count_1 == count_2:
            return [0, 1]
        if count_1 < count_2:
            return [0]
        return [1]
