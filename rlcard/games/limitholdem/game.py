import random
from copy import deepcopy
from rlcard.core import Game
from rlcard.games.limitholdem.dealer import LimitholdemDealer as Dealer
from rlcard.games.limitholdem.player import LimitholdemPlayer as Player
from rlcard.games.limitholdem.judger import LimitholdemJudger as Judger

class LimitholdemGame(Game):

    def __init__(self):
        ''' Initialize the class limitholdem Game
        '''
        super().__init__()


    def init_game(self):
        ''' Initialilze the game

        Returns:
            state (dict): the first state of the game
            player_id (int): current player's id
        '''
        self.dealer = Dealer()
        self.player0 = Player(0)
        self.player1 = Player(1)
        self.judger = Judger()
        self.dealer.deal_card(self.player0)
        self.dealer.deal_card(self.player1)
        self.dealer.deal_card(self.player0)
        self.dealer.deal_card(self.player1)
        self.dealer.deal_chips(self.player0, 10)
        self.dealer.deal_chips(self.player1, 20)
        self.winner = {'player1':0, 'player0':0}
        self.history = []
        return self.get_state(self.get_player_id()), self.get_player_id()
        
    def step(self, action):
        ''' Get the next state

        Args:
            action (str): a specific action. (call or raise or fold)

        Returns:
            dict: next player's state
            int: next plater's id
        '''
        next_state = {}
        p = deepcopy(self.player0)
        d = deepcopy(self.player1)
        w = deepcopy(self.winner)
        self.history.append((d,p,w))
        # Play call
        if action == "call":
            self.dealer.deal_card(self.player0)
            self.player1.hand.append(self.player0.hand[-1])
                
            if len(self.player1.hand) == 3:
                self.dealer.deal_card(self.player0)
                self.player1.hand.append(self.player0.hand[-1])
                self.dealer.deal_card(self.player0)
                self.player1.hand.append(self.player0.hand[-1])  

            hand = [card.get_index() for card in self.player0.hand[0:2]]
            public_cards = [c.get_index() for c in self.player1.hand[2:]]
            #dealerhand = [card.get_index() for card in self.dealer.hand]
            next_state['state'] = (hand, public_cards) # show all hand of player1
            next_state['actions'] = ('call', 'raise', 'fold')

        elif action == "raise":
            
            self.dealer.deal_card(self.player0)
            self.player1.hand.append(self.player0.hand[-1])
                
            if len(self.player1.hand) == 3:
                #self.dealer.deal_card(self.player0)
                #self.player1.hand.append(self.player0.hand[-1])
                self.dealer.deal_card(self.player0)
                self.player1.hand.append(self.player0.hand[-1])
                self.dealer.deal_card(self.player0)
                self.player1.hand.append(self.player0.hand[-1])  

            self.judger.judge_game(self)
            hand = [card.get_index() for card in self.player0.hand[0:2]]
            public_cards = [c.get_index() for c in self.player1.hand[2:]]
            next_state['state'] = (hand, public_cards) 
            next_state['actions'] = ('call', 'raise', 'fold')

        elif action == "fold":

            self.player0.status = 'bust'
            hand = [card.get_index() for card in self.player0.hand[0:2]]
            public_cards = [c.get_index() for c in self.player1.hand[2:]]
            #dealerhand = [card.get_index() for card in self.dealer.hand]
            next_state['state'] = (hand, public_cards) # show all hand of player1
            next_state['actions'] = ('call', 'raise', 'fold')
        return next_state, self.player0.get_player_id()

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            Status (bool): check if the step back is success or not
        '''
        if len(self.history) > 0:
            self.dealer, self.player, self.winner = self.history.pop()
            return True
        return False

    def get_player_num(self):
        ''' Return the number of players in blackjack

        Returns:
            number_of_player (int): blackjack only have 1 player
        '''
        return 1

    def get_action_num(self):
        ''' Return the number of applicable actions

        Returns:
            number_of_actions (int): there are only two actions (call and raise)
        '''
        return 3

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            player_id (int): current player's id
        '''
        return self.player0.get_player_id()

    def get_state(self, player):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            state (dict): corresponding player's state
        '''
        state = {}
        state['actions'] = ('call', 'raise', 'fold')
        player0_hand = [card.get_index() for card in self.player0.hand [0:2]]
        public_cards = [card.get_index() for card in self.player0.hand [2:]] 
        state['state'] = (player0_hand, public_cards)
        return state

    def is_over(self):
        ''' Check if the game is over

        Returns:
            status (bool): True/False
        '''
        if len(self.player0.hand) == 7 or self.player0.status == 'bust':
            return True
        else:
            return False
    

