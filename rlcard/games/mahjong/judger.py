# -*- coding: utf-8 -*-
''' Implement Mahjong Judger class
'''
from collections import Counter
from collections import defaultdict
from rlcard.games.mahjong.player import MahjongPlayer as Player
from rlcard.games.mahjong.card import MahjongCard as Card

class MahjongJudger(object):
    ''' Determine what cards a player can play
    '''

    def __init__(self):
        ''' Initilize the Judger class for Dou Dizhu
        '''
        pass


    def judge_pong_gong(self, dealer, players, last_player):  
        last_card = dealer.table[-1]
        last_card_str = last_card.get_str()
        last_card_value = last_card_str.split("-")[-1]
        last_card_type = last_card_str.split("-")[0]
        for player in players:
            hand = [card.get_str() for card in player.hand]
            hand_dict = defaultdict(list)
            for card in hand:
                hand_dict[card.split("-")[0]].append(card.split("-")[1])
            pile = player.pile 
            # check gong
            if hand.count(last_card_str) == 3 and last_player != player.player_id:
                return 'gong', player, [last_card]*4
            # check pong
            if hand.count(last_card_str) == 2 and last_player != player.player_id:
                return 'pong', player, [last_card]*3
        return False, None, None

    def judge_chow(self, dealer, players, last_player):
        last_card = dealer.table[-1]
        last_card_str = last_card.get_str()
        last_card_value = last_card_str.split("-")[-1]
        last_card_type = last_card_str.split("-")[0]
        for player in players:
            hand = [card.get_str() for card in player.hand]
            hand_dict = defaultdict(list)
            for card in hand:
                hand_dict[card.split("-")[0]].append(card.split("-")[1])
            pile = player.pile 
            # check chow
            if last_card_type != "dragons" and last_card_type != "winds" and last_player == player.get_player_id() - 1:
                flag = False
                type_values = hand_dict[last_card_type]
                type_values.append(last_card_value)
                test_value_list = sorted(type_values)
                if len(test_value_list) < 3:
                    continue 
                test_card_index = test_value_list.index(last_card_value)
                test_cases = []
                if test_card_index == 0:
                    test_cases.append([test_value_list[test_card_index], test_value_list[test_card_index+1], test_value_list[test_card_index+2]])
                elif test_card_index < len(test_value_list): 
                    test_cases.append([test_value_list[test_card_index-2], test_value_list[test_card_index-1], test_value_list[test_card_index]])
                else:
                    test_cases.append([test_value_list[test_card_index-1], test_value_list[test_card_index], test_value_list[test_card_index+1]])

                for l in test_cases:
                    if self.check_consecutive(l):
                        suit = last_card_type
                        cards_str= [suit+"-"+i for i in l]
                        cards = []
                        for card in player.hand:
                            if card.get_str() in cards_str and card.get_str() != last_card_str:
                                cards.append(card)
                                cards_str.pop(cards_str.index(card.get_str()))
                            if len(cards_str) == 1:
                                cards.append(last_card)
                                break
                        return 'chow', player, cards
        return False, None, None

    def judge_game(self, game):
        if len(game.dealer.deck) == 0:
            return True, -1
        players_val = []
        for player in game.players:
            win, val = self.judge_hu(player)
            if win == True:
                return True, player.player_id
            players_val.append(val)
        player_id = players_val.index(max(players_val))
        return False, player_id 

    def judge_hu(self, player):
        set_count = 0
        hand = [card.get_str() for card in player.hand]
        count_dict = {card: hand.count(card) for card in hand}
        pile = player.pile 
        set_count += len(pile)
        used = []
        maximum = 0
        for each in count_dict:
            if each in used:
                continue
            tmp_set_count = 0
            tmp_hand = hand.copy()
            if count_dict[each] == 2:
                for i in range(count_dict[each]):
                    tmp_hand.pop(tmp_hand.index(each))    
                tmp_set_count, _set = self.cal_set(tmp_hand)
                used.extend(_set)
                if tmp_set_count + set_count > maximum:
                    maximum = tmp_set_count + set_count
                if tmp_set_count + set_count >= 4:
                    #print(player.get_player_id(), sorted([card.get_str() for card in player.hand]))
                    #print([[c.get_str() for c in s] for s in player.pile])
                    #print(len(player.hand), sum([len(s) for s in player.pile]))
                    #exit()
                    return True, maximum
        return False, maximum


    def check_consecutive(self, _list):
        l = list(map(int, _list))
        if sorted(l) == list(range(min(l), max(l)+1)):
            return True
        return False

    def cal_set(self, cards): 
        tmp_cards = cards.copy()
        sets = []
        set_count = 0
        _dict = {card: tmp_cards.count(card) for card in tmp_cards}
        # check pong/gang
        for each in _dict:
            if _dict[each] == 3 or _dict[each] == 4:
                set_count += 1
                for i in range(_dict[each]):
                    tmp_cards.pop(tmp_cards.index(each))

        _dict_by_type = defaultdict(list)
        for card in tmp_cards:
            _type = card.split("-")[0]
            _trait = card.split("-")[1]
            if _type == 'dragons' or _type == 'winds':
                continue
            else:
                _dict_by_type[_type].append(_trait)
        for _type in _dict_by_type.keys():
            values = sorted(_dict_by_type[_type]) 
            if len(values) > 2:
                for index, val in enumerate(values):
                    if index == 0:
                        test_case = [values[index], values[index+1], values[index+2]]
                    elif index == len(values)-1:
                        test_case = [values[index-2], values[index-1], values[index]]
                    else:
                        test_case = [values[index-1], values[index], values[index+1]]
                    if self.check_consecutive(test_case):
                        set_count += 1
                        for each in test_case:
                            values.pop(values.index(each))
                            c = _type+"-"+str(each)
                            sets.append(c)
                            if c in tmp_cards:
                                tmp_cards.pop(tmp_cards.index(c))
        return set_count, sets

if __name__ == "__main__":
    judger = MahjongJudger()
    player = Player(0)
    card_info = Card.info
    #print(card_info)
    player.pile.append([Card(card_info['type'][0], card_info['trait'][0])]*3)
    #player.hand.extend([Card(card_info['type'][0], card_info['trait'][0])]*2)
    player.hand.extend([Card(card_info['type'][1], card_info['trait'][1])]*4)
    player.hand.extend([Card(card_info['type'][2], card_info['trait'][1])]*3)
    player.hand.extend([Card(card_info['type'][0], card_info['trait'][2])]*3)
    player.hand.extend([Card(card_info['type'][3], card_info['trait'][9])]*2)
    #player.hand.extend([Card(card_info['type'][2], card_info['trait'][4])]*1)
    print([card.get_str() for card in player.hand])
    print(judger.judge_hu(player))
