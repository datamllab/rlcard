
class BlackjackJudger:
    def __init__(self, np_random):
        ''' Initialize a BlackJack judger class
        '''
        self.np_random = np_random
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

    def judge_game(self, game, game_pointer):
        ''' Judge the winner of the game

        Args:
            game (class): target game class
        '''
        '''
                game.winner['dealer'] doesn't need anymore if we change code like this

                player bust (whether dealer bust or not) => game.winner[playerX] = -1
                player and dealer tie => game.winner[playerX] = 1
                dealer bust and player not bust => game.winner[playerX] = 2
                player get higher score than dealer => game.winner[playerX] = 2
                dealer get higher score than player => game.winner[playerX] = -1
                game.winner[playerX] = 0 => the game is still ongoing
                '''

        if game.players[game_pointer].status == 'bust':
            game.winner['player' + str(game_pointer)] = -1
        elif game.dealer.status == 'bust':
            game.winner['player' + str(game_pointer)] = 2
        else:
            if game.players[game_pointer].score > game.dealer.score:
                game.winner['player' + str(game_pointer)] = 2
            elif game.players[game_pointer].score < game.dealer.score:
                game.winner['player' + str(game_pointer)] = -1
            else:
                game.winner['player' + str(game_pointer)] = 1

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
