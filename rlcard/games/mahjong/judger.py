# -*- coding: utf-8 -*-
''' Implement Mahjong Judger class
'''
from collections import Counter
from collections import defaultdict

class MahjongJudger(object):
    ''' Determine what cards a player can play
    '''

    def __init__(self, players):
        ''' Initilize the Judger class for Dou Dizhu
        '''
        pass

    def judge_round(self, dealer, players, last_player):
        if len(dealer.table) == 0:
            return 'play', None, None
        last_card = dealer.table[-1]
        last_card_str = last_card.get_str()
        last_card_value = last_card_str.split("-")[-1]
        last_card_type = last_card_str.split("-")[0]
        for player in players:
            hand = [card.get_str() for card in player.hand]
            #print("LAST:", last_card_str,"HAND:", hand, "Num:", hand.count(last_card_str))
            hand_dict = defaultdict(list)
            for card in hand:
                hand_dict[card.split("-")[0]].append(card.split("-")[1])
            pile = player.pile 
            # check pong
            if hand.count(last_card_str) == 2:
                return 'pong', player, [last_card]*3

            # check gong
            if hand.count(last_card_str) == 3:
                return 'gong', player, [last_card]*4

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
                #elif test_card_index <= len(test_value_list) - 2:
                elif test_card_index < len(test_value_list): 
                    test_cases.append([test_value_list[test_card_index-2], test_value_list[test_card_index-1], test_value_list[test_card_index]])
                #if test_card_index >= 2 and test_card_index <= len(test_value_list) - 2:
                else:
                    test_cases.append([test_value_list[test_card_index-1], test_value_list[test_card_index], test_value_list[test_card_index+1]])
                    #test_cases.append([test_value_list[test_card_index-2], test_value_list[test_card_index-1], test_value_list[test_card_index]])
                    #test_cases.append([test_value_list[test_card_index], test_value_list[test_card_index+1], test_value_list[test_card_index+2]])

                for l in test_cases:
                    if self.check_consecutive(l):
                        return 'chow', player, l

        return 'play', None, None

    def judge_game(self, game):
        if len(game.dealer.deck) == 0:
            return True
        for player in game.players:
            set_count = 0
            hand = [card.get_str() for card in player.hand]
            count_dict = {card: hand.count(card) for card in hand}
            pile = player.pile 
            set_count += len(pile)
            #if set_count != 0:
            #    print(hand, set_count, player.pile)
            used = []
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
                    if tmp_set_count + set_count >= 4:
                        #print(set_count)
                        print(player.get_player_id(), sorted([card.get_str() for card in player.hand]))
                        return True
        return False

    def check_consecutive(self, l):
        l = list(map(int, l))
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
