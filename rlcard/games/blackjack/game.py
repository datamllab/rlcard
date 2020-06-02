from copy import deepcopy
import numpy as np

from rlcard.games.blackjack import Dealer
from rlcard.games.blackjack import Player
from rlcard.games.blackjack import Judger

class BlackjackGame(object):

    def __init__(self, allow_step_back=False):
        ''' Initialize the class Blackjack Game
        '''
        self.allow_step_back = allow_step_back
        self.num_players = 2
        self.np_random = np.random.RandomState()


    def init_game(self):
        ''' Initialilze the game

        Returns:
            state (dict): the first state of the game
            player_id (int): current player's id
        '''
        self.dealer = Dealer(self.np_random)

        self.player = []
        for i in range(self.num_players):
            self.player.append(Player(i, self.np_random))

        self.judger = Judger(self.np_random)

        for i in range(2):
            for j in range(self.num_players):
                self.dealer.deal_card(self.player[j])
            self.dealer.deal_card(self.dealer)

        for i in range(self.num_players):
            self.player[i].status, self.player[i].score = self.judger.judge_round(self.player[i])

        self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)

        self.winner = {'dealer':0}
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
            p = deepcopy(self.player[self.game_pointer])
            d = deepcopy(self.dealer)
            w = deepcopy(self.winner)
            self.history.append((d,p,w))

        next_state = {}
        # Play hit
        if action != "stand":
            self.dealer.deal_card(self.player[self.game_pointer])
            self.player[self.game_pointer].status, self.player[self.game_pointer].score = self.judger.judge_round(self.player[self.game_pointer])
            if self.player[self.game_pointer].status == 'bust':
                # game over, set up the winner, print out dealer's hand
                self.judger.judge_game(self, self.game_pointer)
        elif action == "stand":
            while self.judger.judge_score(self.dealer.hand) < 17:
                self.dealer.deal_card(self.dealer)
                self.dealer.status, self.dealer.score = self.judger.judge_round(self.dealer)
            self.player[self.game_pointer].status, self.player[self.game_pointer].score = self.judger.judge_round(self.player[self.game_pointer])
            self.judger.judge_game(self, self.game_pointer)

        hand = [card.get_index() for card in self.player[self.game_pointer].hand]

        if self.is_over():
            dealer_hand = [card.get_index() for card in self.dealer.hand]
        else:
            dealer_hand = [card.get_index() for card in self.dealer.hand[1:]]

        for i in range(self.num_players):
            next_state['player' + str(i) + ' hand'] = [card.get_index() for card in self.player[i].hand]
        next_state['dealer hand'] = dealer_hand
        next_state['actions'] = ('hit', 'stand')
        next_state['state'] = (hand, dealer_hand)

        if self.game_pointer >= self.num_players - 1:
            self.game_pointer = 0
        else:
            self.game_pointer += 1

        return next_state, self.game_pointer

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            Status (bool): check if the step back is success or not
        '''
        #while len(self.history) > 0:
        if len(self.history) > 0:
            self.dealer, self.player[self.game_pointer], self.winner = self.history.pop()
            return True
        return False

    def get_player_num(self):
        ''' Return the number of players in blackjack

        Returns:
            number_of_player (int): blackjack only have 1 player
        '''
        return self.num_players

    @staticmethod
    def get_action_num():
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
        hand = [card.get_index() for card in self.player[player_id].hand]
        if self.is_over():
            dealer_hand = [card.get_index() for card in self.dealer.hand]
        else:
            dealer_hand = [card.get_index() for card in self.dealer.hand[1:]]

        for i in range(self.num_players):
            state['player' + str(i) + ' hand'] = [card.get_index() for card in self.player[i].hand]
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

##########################################################
#    # For testing
#    def _start_game(self):
#        while True:
#            self.init_game()
#            player = self.player.get_player_id()
#            #state = self.get_state(player)
#            action = ['hit', 'stand']
#            while not self.is_over():
#                act = random.choice(action)
#                print("Status(Player, Dealer): ",(self.player.status, self.dealer.status))
#                print("Score(Player, Dealer): ",(self.player.score, self.dealer.score))
#                print("Player_action:",act)
#                next_state, next_player = self.step(act)
#
#            print("Status(Player, Dealer): ",(self.player.status, self.dealer.status))
#            print("Score(Player, Dealer): ",(self.player.score, self.dealer.score))
#            print(self.winner)
#            if self.dealer.score < 17 and self.winner['dealer'] == 1 and self.winner['player'] == 0:
#                print(next_state)
#                break
#
#if __name__ == "__main__":
#    game = BlackjackGame()
#    game._start_game()
