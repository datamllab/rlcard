import random
from copy import deepcopy

from rlcard.games.mahjong.dealer import MahjongDealer as Dealer
from rlcard.games.mahjong.player import MahjongPlayer as Player
from rlcard.games.mahjong.round import MahjongRound as Round
from rlcard.games.mahjong.judger import MahjongJudger as Judger


random.seed(10)
class MahjongGame(object):

    def __init__(self):
        self.num_players = 4

    def init_game(self):
        # Initialize a dealer that can deal cards
        self.dealer = Dealer()

        # Initialize four players to play the game
        self.players = [Player(i) for i in range(self.num_players)]

        self.judger = Judger(self.players)
        self.round = Round(self.judger, self.dealer, self.num_players)

        # Deal 13 cards to each player to prepare for the game
        for player in self.players:
            # print(player.get_player_id(), end=':')
            self.dealer.deal_cards(player, 13)
            # for card in player.hand:
            # print(card.get_str(), end=',')

        # print test
        #for player in self.players:
        #    player.print_hand()
        #print(len(self.dealer.deck))
        # ##
        # Save the hisory for stepping back to the last state.
        self.history = []

        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id

    def step(self, action):
        # First snapshot the current state
        hist_dealer = deepcopy(self.dealer)
        hist_round = deepcopy(self.round)
        hist_players = deepcopy(self.players)
        self.history.append((hist_dealer, hist_players, hist_round))

        self.round.proceed_round(self.players, action)
        player_id = self.round.current_player
        state = self.get_state(player_id)
        return state, player_id
        # print(self.round.current_player, end=': ')

    def step_back(self):
        if not self.history:
            return False
        self.dealer, self.players, self.round = self.history.pop()
        return True

    def get_state(self, player_id):
        state = self.round.get_state(self.players, player_id)
        return state

    def get_legal_actions(self):
        #print(self.round.get_state(self.players, self.round.current_player)['valid_act'])
        if self.round.get_state(self.players, self.round.current_player)['valid_act'] == ['play']:
            return self.round.get_state(self.players, self.round.current_player)['action_cards']
        else:
            return self.round.get_state(self.players, self.round.current_player)['valid_act']

    def get_player_num(self):
        return self.num_players

    def is_over(self):
        return self.judger.judge_game(self)

# For test
if __name__ == '__main__':
    import time
    random.seed(0)
    start = time.time()
    game = MahjongGame()
    for _ in range(100):
        #print('*****init game*****')
        state, button = game.init_game()
        #print(button, state)
        i = 0
        while not game.is_over():
            i += 1
            legal_actions = game.get_legal_actions()
            #print('legal_actions', legal_actions)
            '''
            if i == 3:
                print('step back')
                print(game.step_back())
                print(game.get_player_id())
                legal_actions = game.get_legal_actions()
                print('back legal actions', legal_actions)
                input()
            '''
            action = random.choice(legal_actions)
            if len(legal_actions) < 3:
                print(legal_actions, action)
                exit()
            #print('action', action)
            #print()
            state, button = game.step(action)
            #print(button, state)
        print(len(game.dealer.deck))
    end = time.time()
    print(end-start)
