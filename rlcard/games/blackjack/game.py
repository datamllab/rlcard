from copy import deepcopy
import numpy as np

from rlcard.games.blackjack import Dealer
from rlcard.games.blackjack import Player
from rlcard.games.blackjack import Judger

class BlackjackGame:

    def __init__(self, allow_step_back=False):
        ''' Initialize the class Blackjack Game
        '''
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()

    def configure(self, game_config):
        ''' Specifiy some game specific parameters, such as number of players
        '''
        self.num_players = game_config['game_num_players']

    def init_game(self):
        ''' Initialilze the game

        Returns:
            state (dict): the first state of the game
            player_id (int): current player's id
        '''
        self.dealer = Dealer(self.np_random)

        self.players = []
        for i in range(self.num_players):
            self.players.append(Player(i, self.np_random))

        self.judger = Judger(self.np_random)

        for i in range(2):
            for j in range(self.num_players):
                self.dealer.deal_card(self.players[j])
            self.dealer.deal_card(self.dealer)

        for i in range(self.num_players):
            self.players[i].status, self.players[i].score = self.judger.judge_round(self.players[i])

        self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)

        self.winner = {'dealer': 0}
        for i in range(self.num_players):
            self.winner['player' + str(i)] = 0

        self.history = []
        self.game_pointer = 0

        return self.get_state(self.game_pointer), self.game_pointer

    def step(self, action):
        ''' Get the next state

        Args:
            action (str): a specific action of blackjack. (Hit or Stand)

        Returns:/
            dict: next player's state
            int: next plater's id
        '''
        if self.allow_step_back:
            p = deepcopy(self.players[self.game_pointer])
            d = deepcopy(self.dealer)
            w = deepcopy(self.winner)
            self.history.append((d, p, w))

        next_state = {}
        # Play hit
        if action != "stand":
            self.dealer.deal_card(self.players[self.game_pointer])
            self.players[self.game_pointer].status, self.players[self.game_pointer].score = self.judger.judge_round(
                self.players[self.game_pointer])
            if self.players[self.game_pointer].status == 'bust':
                # game over, set up the winner, print out dealer's hand # If bust, pass the game pointer
                if self.game_pointer >= self.num_players - 1:
                    while self.judger.judge_score(self.dealer.hand) < 17:
                        self.dealer.deal_card(self.dealer)
                    self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)
                    for i in range(self.num_players):
                        self.judger.judge_game(self, i) 
                    self.game_pointer = 0
                else:
                    self.game_pointer += 1

                
        elif action == "stand": # If stand, first try to pass the pointer, if it's the last player, dealer deal for himself, then judge game for everyone using a loop
            self.players[self.game_pointer].status, self.players[self.game_pointer].score = self.judger.judge_round(
                self.players[self.game_pointer])
            if self.game_pointer >= self.num_players - 1:
                while self.judger.judge_score(self.dealer.hand) < 17:
                    self.dealer.deal_card(self.dealer)
                self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)
                for i in range(self.num_players):
                    self.judger.judge_game(self, i) 
                self.game_pointer = 0
            else:
                self.game_pointer += 1


            
            

        hand = [card.get_index() for card in self.players[self.game_pointer].hand]

        if self.is_over():
            dealer_hand = [card.get_index() for card in self.dealer.hand]
        else:
            dealer_hand = [card.get_index() for card in self.dealer.hand[1:]]

        for i in range(self.num_players):
            next_state['player' + str(i) + ' hand'] = [card.get_index() for card in self.players[i].hand]
        next_state['dealer hand'] = dealer_hand
        next_state['actions'] = ('hit', 'stand')
        next_state['state'] = (hand, dealer_hand)

        

        return next_state, self.game_pointer

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            Status (bool): check if the step back is success or not
        '''
        #while len(self.history) > 0:
        if len(self.history) > 0:
            self.dealer, self.players[self.game_pointer], self.winner = self.history.pop()
            return True
        return False

    def get_num_players(self):
        ''' Return the number of players in blackjack

        Returns:
            number_of_player (int): blackjack only have 1 player
        '''
        return self.num_players

    @staticmethod
    def get_num_actions():
        ''' Return the number of applicable actions

        Returns:
            number_of_actions (int): there are only two actions (hit and stand)
        '''
        return 2

    def get_player_id(self):
        ''' Return the current player's id

        Returns:
            player_id (int): current player's id
        '''
        return self.game_pointer

    def get_state(self, player_id):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            state (dict): corresponding player's state
        '''
        '''
                before change state only have two keys (action, state)
                but now have more than 4 keys (action, state, player0 hand, player1 hand, ... , dealer hand)
                Although key 'state' have duplicated information with key 'player hand' and 'dealer hand', I couldn't remove it because of other codes
                To remove it, we need to change dqn agent too in my opinion
                '''
        state = {}
        state['actions'] = ('hit', 'stand')
        hand = [card.get_index() for card in self.players[player_id].hand]
        if self.is_over():
            dealer_hand = [card.get_index() for card in self.dealer.hand]
        else:
            dealer_hand = [card.get_index() for card in self.dealer.hand[1:]]

        for i in range(self.num_players):
            state['player' + str(i) + ' hand'] = [card.get_index() for card in self.players[i].hand]
        state['dealer hand'] = dealer_hand
        state['state'] = (hand, dealer_hand)

        return state

    def is_over(self):
        ''' Check if the game is over

        Returns:
            status (bool): True/False
        '''
        '''
                I should change here because judger and self.winner is changed too
                '''
        for i in range(self.num_players):
            if self.winner['player' + str(i)] == 0:
                return False

        return True
