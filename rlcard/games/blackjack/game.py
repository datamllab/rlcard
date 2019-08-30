import random
from os import path
import sys
FILE = path.abspath(__file__)
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(FILE)))))
from rlcard.core import Game
from rlcard.games.blackjack.dealer import BlackjackDealer as Dealer
from rlcard.games.blackjack.player import BlackjackPlayer as Player
from rlcard.games.blackjack.round import BlackjackRound as Round
from rlcard.games.blackjack.judger import BlackjackJudger as Judger

class BlackjackGame(Game):
    def __init__(self, seed=None):
        super().__init__()
        self.set_seed(seed)
        self.dealer = Dealer()
        self.player = Player(0)
        self.judger = Judger()
        self.winner = {'dealer':0, 'player':0}


    def set_seed(self, seed):
        random.seed(seed)

    def start_game(self):
        player = self.player.get_player_id()
        #state = self.get_state(player)
        action = ['hit', 'stand']
        self.init()
        while not self.end():
            act = random.choice(action)
            print(self.player.status, self.dealer.status)
            print(self.player.score, self.dealer.score)
            print(act)
            next_state, next_player = self.step(act)

        print(self.player.status, self.dealer.status)
        print(self.player.score, self.dealer.score)
        print(self.winner)

    def init(self):
        self.dealer.deal_card(self.player)
        self.dealer.deal_card(self.dealer)
        self.dealer.deal_card(self.player)
        self.dealer.deal_card(self.dealer)
        self.player.status, self.player.score = self.judger.judge_round(self.player)
        self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)
            
    def step(self, action):
        if action != "stand":
            self.dealer.deal_card(self.player)
            self.player.status, self.player.score = self.judger.judge_round(self.player)
            if self.player.status == 'bust':
                self.judger.judge_game(self)
            next_state = (self.player, self.dealer.hand[1:])
        elif action == "stand":
            while self.judger.judge_score(self.dealer.hand) <= 17:
                self.dealer.deal_card(self.dealer)
                self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)
            self.judger.judge_game(self)
            next_state = (self.player, self.dealer.hand[1:])
        return next_state, self.player

    def end(self):
        if self.player.status == 'bust'or self.dealer.status == 'bust' or (self.winner['dealer'] != 0 or self.winner['player'] != 0):
            return True
        else:
            return False
        
    def reset(self):
        self.winner = {'dealer':0, 'player':0}
        self.dealer = Dealer()
        self.player = Player(0)
        self.judger = Judger()
        self.dealer.deal_card(self.player)
        self.dealer.deal_card(self.dealer)
        self.dealer.deal_card(self.player)
        self.dealer.deal_card(self.dealer)
        self.player.status, self.player.score = self.judger.judge_round(self.player)
        self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)

    def get_reward(self):
        pass

if __name__ == "__main__":
    game = BlackjackGame()
    game.start_game()
