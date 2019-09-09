import random
from copy import deepcopy
from rlcard.core import Game
from rlcard.games.blackjack.dealer import BlackjackDealer as Dealer
from rlcard.games.blackjack.player import BlackjackPlayer as Player
from rlcard.games.blackjack.round import BlackjackRound as Round
from rlcard.games.blackjack.judger import BlackjackJudger as Judger

class BlackjackGame(Game):

    def __init__(self, seed=None):
        super().__init__()
        self.set_seed(seed)


    def init_game(self):
        self.dealer = Dealer()
        self.player = Player(0)
        self.judger = Judger()
        self.dealer.deal_card(self.player)
        self.dealer.deal_card(self.dealer)
        self.dealer.deal_card(self.player)
        self.dealer.deal_card(self.dealer)
        self.player.status, self.player.score = self.judger.judge_round(self.player)
        self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)
        self.winner = {'dealer':0, 'player':0}
        self.history = []
        return self.get_state(self.get_player_id()), self.get_player_id()
        
    def step(self, action):
        next_state = {}
        p = deepcopy(self.player)
        d = deepcopy(self.dealer)
        w = deepcopy(self.winner)
        self.history.append((d,p,w))
        if action != "stand":
            self.dealer.deal_card(self.player)
            self.player.status, self.player.score = self.judger.judge_round(self.player)
            if self.player.status == 'bust':
                self.judger.judge_game(self)
            hand = [card.get_index() for card in self.player.hand]
            dealer_hand = [card.get_index() for card in self.dealer.hand[1:]]
            next_state['state'] = (hand, dealer_hand)
            next_state['actions'] = ('hit', 'stand')

        elif action == "stand":
            while self.judger.judge_score(self.dealer.hand) < 17:
                self.dealer.deal_card(self.dealer)
                self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)
            self.judger.judge_game(self)
            hand = [card.get_index() for card in self.player.hand]
            dealer_hand = [c.get_index() for c in self.dealer.hand]
            next_state['state'] = (hand, dealer_hand) # show all hand of dealer
            next_state['actions'] = ('hit', 'stand')
        return next_state, self.player.get_player_id()

    def step_back(self):
        if len(self.history) > 0:
            self.dealer, self.player, self.winner = self.history.pop()
            return True
        return False

    def set_seed(self, seed):
        random.seed(seed)

    def get_player_num(self):
        return 1

    def get_action_num(self):
        return 2

    def get_player_id(self):
        return self.player.get_player_id()

    def get_state(self, player):
        state = {}
        state['actions'] = ('hit', 'stand')
        hand = [card.get_index() for card in self.player.hand]
        if self.winner['player'] == 0 and self.winner['dealer'] == 0:
            dealer_hand = [card.get_index() for card in self.dealer.hand[1:]]
        else:
            dealer_hand = [card.get_index() for card in self.dealer.hand]
        state['state'] = (hand, dealer_hand)
        return state

    def is_over(self):
        if self.player.status == 'bust'or self.dealer.status == 'bust' or (self.winner['dealer'] != 0 or self.winner['player'] != 0):
            return True
        else:
            return False
    

######################################################### 
    # For testing
    def _start_game(self):
        while True:
            self.init_game()
            player = self.player.get_player_id()
            #state = self.get_state(player)
            action = ['hit', 'stand']
            while not self.is_over():
                act = random.choice(action)
                print("Status(Player, Dealer): ",(self.player.status, self.dealer.status))
                print("Score(Player, Dealer): ",(self.player.score, self.dealer.score))
                print("Player_action:",act)
                next_state, next_player = self.step(act)

            print("Status(Player, Dealer): ",(self.player.status, self.dealer.status))
            print("Score(Player, Dealer): ",(self.player.score, self.dealer.score))
            print(self.winner)
            if self.dealer.score < 17 and self.winner['dealer'] == 1 and self.winner['player'] == 0:
                print(next_state)
                break

if __name__ == "__main__":
    game = BlackjackGame()
    game._start_game()


