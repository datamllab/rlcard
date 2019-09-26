import random
from rlcard.games.mahjong.judger import MahjongJudger as Judger


class MahjongRound(object):

    def __init__(self, judger, dealer, num_players):
        self.judger = judger
        self.dealer = dealer
        self.target = None
        self.current_player = 0
        self.last_player = None
        self.num_players = num_players
        self.direction = 1
        self.played_cards = []
        self.is_over = False
        self.prev_status = None

    def proceed_round(self, players, action):
        self.dealer.deal_cards(players[self.current_player], 1)
        if action == 'stand':
            self.last_player = self.current_player

        elif action == 'gong':
            if self.prev_statVus['player'] == self.current_player and self.prev_status['valid_act'] == action:
                self.current_player.gong(self.prev_status['action_cards'])
                self.prev_status = None
            self.last_player = self.current_player

        elif action == 'pong':
            if self.prev_statVus['player'] == self.current_player and self.prev_status['valid_act'] == action:
                self.current_player.pong(self.prev_status['action_cards'])
                self.prev_status = None
            self.last_player = self.current_player

        elif action == 'chow':
            if self.prev_statVus['player'] == self.current_player and self.prev_status['valid_act'] == action:
                self.current_player.pong(self.prev_status['action_cards'])
                self.prev_status = None
            self.last_player = self.current_player

        else: # Play game: Proceed to next player
            players[self.current_player].play_card(self.dealer, action)
            self.last_player = self.current_player
            self.current_player = (self.current_player + 1) % 4

    def get_state(self, players, player_id):
        #if self.prev_status != None:
            #print(self.prev_status['valid_act'])
        state = {}
        player = players[player_id]
        if self.prev_status != None and self.prev_status['valid_act'] != 'play':
            state['valid_act'] = ['play'] 
            state['table'] = self.dealer.table
            state['player'] = self.current_player 
            state['player_pile'] = players[player_id].pile
            state['action_cards'] = players[player_id].hand # For doing action (pong, chow, gong)
        else:
            (valid_act, player, cards) = self.judger.judge_round(self.dealer, players, self.last_player)
            print("judge_round", valid_act, player, cards)
            if valid_act != 'play':
                state['valid_act'] = [valid_act] 
                state['table'] = self.dealer.table
                state['player'] = player_id
                state['player_pile'] = player.pile
                state['action_cards'] = cards # For doing action (pong, chow, gong)
            else:
                state['valid_act'] = [valid_act]
                state['table'] = self.dealer.table
                state['player'] = self.current_player 
                state['player_pile'] = players[player_id].pile
                state['action_cards'] = players[player_id].hand # For doing action (pong, chow, gong)
            if state['valid_act'] != 'play':
                self.prev_status = state 
            else:
                self.prev_status = None
            self.current_player = player_id
        return state 

