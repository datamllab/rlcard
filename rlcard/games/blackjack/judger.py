
class BlackjackJudger(object):
    def __init__(self):
        ''' Initialize a BlackJack judger class
        '''
        self.rank2score = {"A":11, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "T":10, "J":10, "Q":10, "K":10}

    def judge_round(self, player):
        ''' Judge the target player's status

        Args:
            player (int): target player's id

        Returns:
            status (str): the status of the target player
            score (int): the current score of the player
        '''
        score = self.judge_score(player.hand)
        if score <= 21:
            return "alive", score
        else:
            return "bust", score

    @staticmethod
    def judge_game(game):
        ''' Judge the winner of the game

        Args:
            game (class): target game class
        '''
        if game.player.status == 'bust':
            game.winner['dealer'] = 1
        elif game.dealer.status == 'bust':
            game.winner['player'] = 1
        else:
            if game.player.score > game.dealer.score:
                game.winner['player'] = 1
            elif game.player.score < game.dealer.score:
                game.winner['dealer'] = 1
            else:
                game.winner['dealer'] = 1
                game.winner['player'] = 1

    def judge_score(self, cards):
        ''' Judge the score of a given cards set

        Args:
            cards (list): a list of cards

        Returns:
            score (int): the score of the given cards set
        '''
        score = 0
        has_A = 0
        for card in cards:
            card_score = self.rank2score[card.rank]
            score += card_score
            if card.rank == 'A':
                has_A += 1
        if score > 21 and has_A > 0:
            for _ in range(has_A):
                score -= 10
                if score < 21:
                    break
        return score
