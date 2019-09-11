import random
from copy import deepcopy
from rlcard.core import Game
from rlcard.games.simpletexasholdem.dealer import LimitHoldemDealer as Dealer
from rlcard.games.simpletexasholdem.player import LimitHoldemPlayer as Player
from rlcard.games.simpletexasholdem.round import LimitHoldemRound as Round
from rlcard.games.simpletexasholdem.judger import LimitHoldemJudger as Judger

class LimitHoldemGame(Game):

    def __init__(self, seed=None):
        super().__init__()
        self.set_seed(seed)


    def init_game(self):
        self.dealer = Dealer()
        self.player0 = Player(0)
        self.player1 = Player(1)
        self.judger = Judger()
        self.dealer.deal_card(self.player0)
        self.dealer.deal_card(self.player1)
        self.dealer.deal_card(self.player0)
        self.dealer.deal_card(self.player1)

        
       # self.player0.status, self.player0.score = self.judger.judge_round(self.player0)
       # self.player1.status, self.player1.score = self.judger.judge_round(self.player1)
        self.winner = {'player0':0, 'player1':0}
        self.history = []
        return self.get_state(self.get_player_id()), self.get_player_id()
        
    def step(self, action):
        next_state = {}
        p = deepcopy(self.player0)
        d = deepcopy(self.player1)
        w = deepcopy(self.winner)
        self.history.append((d,p,w))

        if action == "call":
            self.dealer.deal_card(self.player0)
            self.player1.hand.append(self.player0.hand[-1])
                
            if len(self.player1.hand) == 3:
                #self.dealer.deal_card(self.player0)
                #self.player1.hand.append(self.player0.hand[-1])
                self.dealer.deal_card(self.player0)
                self.player1.hand.append(self.player0.hand[-1])
                self.dealer.deal_card(self.player0)
                self.player1.hand.append(self.player0.hand[-1])  
                
            self.player0.status, self.player0.score = self.judger.judge_round(self.player0)
            hand = [card.get_index() for card in self.player0.hand]
            player1_hand = [card.get_index() for card in self.player1.hand[1:]]
            next_state['state'] = (hand, player1_hand)
            next_state['actions'] = ('call', 'raise', 'fold')

        if action == "raise":
            self.dealer.deal_card(self.dealer)
            while self.judger.judge_score(self.player1.hand) < 17:
                self.dealer.deal_card(self.player1)
                self.player1.status, self.player1.score = self.judger.judge_round(self.player1)
            self.judger.judge_game(self)
            hand = [card.get_index() for card in self.player0.hand]
            player1_hand = [c.get_index() for c in self.player1.hand[1:]]
            next_state['state'] = (hand, player1_hand) # show all hand of player1
            next_state['actions'] = ('call', 'raise', 'fold')

        if action == "fold":
            self.dealer.deal_card(self.player0)
            self.player1.hand.append(self.player0.hand[-1])
                
            if len(self.player1.hand) == 3:
                #self.dealer.deal_card(self.player0)
                #self.player1.hand.append(self.player0.hand[-1])
                self.dealer.deal_card(self.player0)
                self.player1.hand.append(self.player0.hand[-1])
                self.dealer.deal_card(self.player0)
                self.player1.hand.append(self.player0.hand[-1])           
            
            while self.judger.judge_score(self.player1.hand) < 17:
                self.dealer.deal_card(self.player1)
                self.player1.status, self.player1.score = self.judger.judge_round(self.player1)
            self.judger.judge_game(self)
            hand = [card.get_index() for card in self.player0.hand]
            player1_hand = [c.get_index() for c in self.player1.hand[1:]]
            dealerhand = [card.get_index() for card in self.dealer.hand]
            next_state['state'] = (hand, player1_hand, dealerhand) # show all hand of player1
            next_state['actions'] = ('call', 'raise', 'fold')

        return next_state, self.player0.get_player_id()


    def step_back(self):
        if len(self.history) > 0:
            self.player1, self.player0, self.winner = self.history.pop()
            return True
        return False

    def set_seed(self, seed):
        random.seed(seed)

    def get_player_num(self):
        return 1

    def get_action_num(self):
        return 3

    def get_player_id(self):
        return self.player0.get_player_id()

    def get_state(self, player):
        state = {}
        state['actions'] = ('call', 'raise', 'fold')
        player0_hand = [card.get_index() for card in self.player0.hand [0:2]]
        public_cards = [card.get_index() for card in self.player0.hand [2:]] 
        state['state'] = (player0_hand, public_cards)
        return state

    def is_over(self):
        if self.winner['player1'] != 0 or self.winner['player0'] != 0:
            return True
        else:
            return False




