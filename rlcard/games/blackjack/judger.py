from rlcard.core import Judger

class BlackjackJudger(Judger):
    def __init__(self):
        self.rank2score = {"A":10, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":10, "Q":10, "K":10}
    
    def judge_round(self, player):
        score = self.judge_score(player.hand)
        if score <= 21:
            return "alive", score
        else:
            return "bust", score

    def judge_game(self, game):
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
        score = 0
        has_A = 0
        c = [card.get_index() for card in cards]
        for card in cards:
            card_score = self.rank2score[card.rank]
            score += card_score
            if card.rank == 'A':
                has_A += 1
        if score > 21 and has_A > 0:
            for i in range(has_A):
                score -= 9
                if score < 21:
                    break
        #print(c, score)
        return score


        
