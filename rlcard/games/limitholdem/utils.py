

class Hand:
    def __init__(self):
        self.all_cards = []
        self.category = 0  # 0:"Not_Yet_Evaluated" 1: "High_Card" , 9:"Straight_Flush" etc
        self.best_five = []
        self.flush_cards = []
        self.cards_by_rank = []
        self.product = 1
        self.RANK_TO_STRING = {2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
                               7: "7", 8: "8", 9: "9", 10: "T", 11: "J", 12: "Q", 13: "K", 14: "A"}
        self.RANK_LOOKUP = "23456789TJQKA"
        self.SUIT_LOOKUP = "SCDH"

    def setCards(self, seven_cards=[]):
        self.all_cards = seven_cards

    def get_hand_five_cards(self):
        return self.best_five

    def _sort_cards(self):
        self.all_cards = sorted(
            self.all_cards, key=lambda card: self.RANK_LOOKUP.index(card[1]))

    def evaluateHand(self):
        """
        Do Hand Evaluation and
        Get the best Five Cards (for or comparing in case 2 hands have the same Category) .

        """
        if len(self.all_cards) != 7:
            raise Exception(
                "There are not enough 7 cards in this hand, quit evaluation now ! ")

        self._sort_cards()
        self.cards_by_rank, self.product = self._getcards_by_rank(
            self.all_cards)

        if self._has_straight_flush():
            self.category = 9
            self._hand_name = "Straight Flush"
        elif self._has_four():
            self.category = 8
            self._hand_name = "Four of a Kind"
            self.best_five = self._get_Four_of_a_kind_cards()
        elif self._has_fullhouse():
            self.category = 7
            self._hand_name = "Full house"
            self.best_five = self._get_Fullhouse_cards()
        elif self._has_flush():
            self.category = 6
            self._hand_name = "Flush"
            i = len(self.flush_cards)
            self.best_five = [card for card in self.flush_cards[i-5:i]]
        elif self._has_straight(self.all_cards):
            self.category = 5
            self._hand_name = "Straight"
        elif self._has_three():
            self.category = 4
            self._hand_name = "Three of a Kind"
            self.best_five = self._get_Three_of_a_kind_cards()
        elif self._has_two_pairs():
            self.category = 3
            self._hand_name = "Two Pairs"
            self.best_five = self._get_Two_Pair_cards()
        elif self._has_pair():
            self.category = 2
            self._hand_name = "One Pair"
            self.best_five = self._get_One_Pair_cards()
        elif self._has_high_card():
            self.category = 1
            self._hand_name = "High Card"
            self.best_five = self._get_High_cards()

    def _has_straight_flush(self):
        self.flush_cards = self._getflush_cards()
        if len(self.flush_cards) > 0:
            straightflush_cards = self._get_straightflush_cards()
            if len(straightflush_cards) > 0:
                self.best_five = straightflush_cards
                return True
        return False

    def _get_straightflush_cards(self):
        straightflush_cards = self._get_straight_cards(self.flush_cards)
        return straightflush_cards

    def _getflush_cards(self):
        card_string = ''.join(self.all_cards)
        for suit in self.SUIT_LOOKUP:
            suit_count = card_string.count(suit)
            if suit_count >= 5:
                flush_cards = [
                    card for card in self.all_cards if card[1] == suit]
                return flush_cards
        return []

    def _has_flush(self):
        if len(self.flush_cards) > 0:
            return True
        else:
            return False

    def _has_straight(self, all_cards):
        diff_rank_cards = self._get_different_rank_list(all_cards)
        self.best_five = self._get_straight_cards(diff_rank_cards)
        if len(self.best_five) != 0:
            return True
        else:
            return False

    def _get_different_rank_list(self, all_cards):
        different_rank_list = []
        different_rank_list.append(all_cards[0])
        for card in all_cards:
            if(card[1] != different_rank_list[-1][0]):
                different_rank_list.append(card)
        return different_rank_list

    def _get_straight_cards(self, Cards):
        highest_card = Cards[-1]
        if highest_card[1] == 'A':
            Cards.insert(0, highest_card)

        i = len(Cards)
        while (i - 5 >= 0):
            hand_to_check = ''.join(card[1] for card in Cards[i-5:i])
            is_straight = self.RANK_LOOKUP.find(hand_to_check)
            if is_straight > 0:
                five_cards = [card for card in Cards[i-5:i]]
                return five_cards
            i -= 1
        return []

    def _getcards_by_rank(self, all_cards):
        card_group = []
        card_group_element = []
        product = 1
        prime_lookup = {0: 1, 1: 1, 2: 2, 3: 3, 4: 5}
        count = 0
        current_rank = 0

        for card in all_cards:
            rank = self.RANK_LOOKUP.index(card[1])
            if rank == current_rank:
                count += 1
                card_group_element.append(card)
            elif rank != current_rank:
                product *= prime_lookup[count]
                # Explanation :
                # if count == 2, then product *= 2
                # if count == 3, then product *= 3
                # if count == 4, then product *= 5
                # if there is a Quad, then product = 5 ( 4, 1, 1, 1) or product = 10 ( 4, 2, 1) or product= 15 (4,3)
                # if there is a Fullhouse, then product = 12 ( 3, 2, 2) or product = 9 (3, 3, 1) or product = 6 ( 3, 2, 1, 1)
                # if there is a Trip, then product = 3 ( 3, 1, 1, 1, 1)
                # if there is TwoPair, then product = 4 ( 2, 1, 2, 1, 1) or product = 8 ( 2, 2, 2, 1)
                # if there is a Pair, then product = 2 (2, 1, 1, 1, 1, 1)
                # if there is HighCard, then product = 1 (1, 1, 1, 1, 1, 1, 1)
                card_group_element.insert(0, count)
                card_group.append(card_group_element)
                # reset counting
                count = 1
                card_group_element = []
                card_group_element.append(card)
                current_rank = rank
        # the For Loop misses operation for the last card
        # These 3 lines below to compensate that
        product *= prime_lookup[count]
        # insert the number of same rank card to the beginning of the
        card_group_element.insert(0, count)
        # after the loop, there is still one last card to add
        card_group.append(card_group_element)
        return card_group, product

    def _has_four(self):
        if self.product == 5 or self.product == 10 or self.product == 15:
            return True
        else:
            return False

    def _has_fullhouse(self):
        if self.product == 6 or self.product == 9 or self.product == 12:
            return True
        else:
            return False

    def _has_three(self):
        if self.product == 3:
            return True
        else:
            return False

    def _has_two_pairs(self):
        if self.product == 4 or self.product == 8:
            return True
        else:
            return False

    def _has_pair(self):
        if self.product == 2:
            return True
        else:
            return False

    def _has_high_card(self):
        if self.product == 1:
            return True
        else:
            return False

    def _get_Four_of_a_kind_cards(self):
        Four_of_a_Kind = []
        cards_by_rank = self.cards_by_rank
        cards_len = len(cards_by_rank)
        for i in reversed(range(cards_len)):
            if cards_by_rank[i][0] == 4:
                Four_of_a_Kind = cards_by_rank.pop(i)
                break
        # The Last cards_by_rank[The Second element]
        kicker = cards_by_rank[-1][1]
        Four_of_a_Kind[0] = kicker

        return Four_of_a_Kind

    def _get_Fullhouse_cards(self):
        Fullhouse = []
        cards_by_rank = self.cards_by_rank
        cards_len = len(cards_by_rank)
        for i in reversed(range(cards_len)):
            if cards_by_rank[i][0] == 3:
                Trips = cards_by_rank.pop(i)[1:4]
                break
        for i in reversed(range(cards_len - 1)):
            if cards_by_rank[i][0] >= 2:
                TwoPair = cards_by_rank.pop(i)[1:3]
                break
        Fullhouse = TwoPair + Trips
        return Fullhouse

    def _get_Three_of_a_kind_cards(self):
        Trip_cards = []
        cards_by_rank = self.cards_by_rank
        cards_len = len(cards_by_rank)
        for i in reversed(range(cards_len)):
            if cards_by_rank[i][0] == 3:
                Trip_cards += cards_by_rank.pop(i)[1:4]
                break

        Trip_cards += cards_by_rank.pop(-1)[1:2]
        Trip_cards += cards_by_rank.pop(-1)[1:2]
        Trip_cards.reverse()
        return Trip_cards

    def _get_Two_Pair_cards(self):
        Two_Pair_cards = []
        cards_by_rank = self.cards_by_rank
        cards_len = len(cards_by_rank)
        for i in reversed(range(cards_len)):
            if cards_by_rank[i][0] == 2 and len(Two_Pair_cards) < 3:
                Two_Pair_cards += cards_by_rank.pop(i)[1:3]

        Two_Pair_cards += cards_by_rank.pop(-1)[1:2]
        Two_Pair_cards.reverse()
        return Two_Pair_cards

    def _get_One_Pair_cards(self):
        One_Pair_cards = []
        cards_by_rank = self.cards_by_rank
        cards_len = len(cards_by_rank)
        for i in reversed(range(cards_len)):
            if cards_by_rank[i][0] == 2:
                One_Pair_cards += cards_by_rank.pop(i)[1:3]
                break

        One_Pair_cards += cards_by_rank.pop(-1)[1:2]
        One_Pair_cards += cards_by_rank.pop(-1)[1:2]
        One_Pair_cards += cards_by_rank.pop(-1)[1:2]
        One_Pair_cards.reverse()
        return One_Pair_cards

    def _get_High_cards(self):
        High_cards = self.all_cards[2:7]
        return High_cards


def compare_hands(hand0, hand1):
        # evaluate player's hand

    if hand0 == None:
        return [0, 1]
    elif hand1 == None:
        return [1, 0]
        # put this in judger
    cards0, cards1 = hand0, hand1
    hand0 = Hand()
    hand1 = Hand()
    RANKS = '23456789TJQKA'

    for card in cards0:

        hand0.all_cards.append(card)

    for card in cards1:

        hand1.all_cards.append(card)

    hand0.evaluateHand()
    hand1.evaluateHand()
    #var = hand1.get_hand_five_cards()
    #print(var)
    # compare hands
    hand0_category = hand0.category
    hand1_category = hand1.category

    if hand0_category > hand1_category:
        return [1, 0]
    elif hand0_category < hand1_category:
        return [0, 1]
    elif hand0_category == hand1_category:
        # compare equal category
        hand0_5_cards = hand0.get_hand_five_cards()
        hand1_5_cards = hand1.get_hand_five_cards()
        

        if hand0_category == 9 or hand0_category == 5 or hand0_category == 6:
            for i in reversed(range(5)):
                hand0_card_rank = hand0_5_cards[i][1]
                hand1_card_rank = hand1_5_cards[i][1]
                if RANKS.index(hand0_card_rank) > RANKS.index(hand1_card_rank):
                    return [1, 0]
                elif RANKS.index(hand0_card_rank) < RANKS.index(hand1_card_rank):
                    return [0, 1]
                elif RANKS.index(hand0_card_rank) == RANKS.index(hand1_card_rank):
                    return [1, 1]   
        if hand0_category == 8:
            seen = []
            duplicated0 = []
            five_cards_0 = []
            five_cards_1 = []
            handcard0 = hand0.get_hand_five_cards()
            handcard1 = hand1.get_hand_five_cards()
            for i in range(5):              
                five_cards_0.append(handcard0[i][1])
            for _ in five_cards_0:  
                if _ not in seen:  
                    seen.append(_)
                else:
                    duplicated0.append(_)            
            seen = []
            duplicated1 = []
            for i in range(5):              
                five_cards_1.append(handcard1[i][1])
            for _ in five_cards_1:  
                if _ not in seen:  
                    seen.append(_)
                else:
                    duplicated1.append(_) 
            if RANKS.index(duplicated0[0][1]) > RANKS.index(duplicated1[0][1]):
                return [1, 0]
            elif RANKS.index(duplicated0[0][1]) < RANKS.index(duplicated1[0][1]):
                return [0, 1]
            elif RANKS.index(duplicated0[0][1]) == RANKS.index(duplicated1[0][1]):
                return [1, 1]

        if hand0_category == 7:
            five_cards_0 = []
            five_cards_1 = []
            handcard0 = hand0.get_hand_five_cards()
            handcard1 = hand1.get_hand_five_cards()
            for i in range(5):              
                five_cards_0.append(RANKS.index(handcard0[i][1]))
            for i in range(5):              
                five_cards_1.append(RANKS.index(handcard1[i][1]))
            five_cards_0.sort()
            five_cards_1.sort()
            if five_cards_0[2] > five_cards_1[2]:
                return [1,0]
            if five_cards_0[2] < five_cards_1[2]:
                return [0,1]
            if five_cards_0[2] == five_cards_1[2]:
                if five_cards_0[4] > five_cards_1[4]:
                    return [1,0]
                if five_cards_0[4] < five_cards_1[4]:
                    return [0,1]
                if five_cards_0[4] == five_cards_1[4]:
                    return [1,1]
 
        if hand0_category == 4:
            five_cards_0 = []
            five_cards_1 = []
            handcard0 = hand0.get_hand_five_cards()
            handcard1 = hand1.get_hand_five_cards()
            for i in range(5):              
                five_cards_0.append(RANKS.index(handcard0[i][1]))
            for i in range(5):              
                five_cards_1.append(RANKS.index(handcard1[i][1]))
            five_cards_0.sort()
            five_cards_1.sort()
            if five_cards_0[2] > five_cards_1[2]:
                return [1,0]
            if five_cards_0[2] < five_cards_1[2]:
                return [0,1]
            if five_cards_0[2] == five_cards_1[2]:
                for _ in range(3):
                    five_cards_0.remove(five_cards_0[2])
                    five_cards_1.remove(five_cards_1[2])
                if five_cards_0[1] > five_cards_1[1]:
                    return [1,0]
                if five_cards_0[1] < five_cards_1[1]:
                    return [0,1]
                if five_cards_0[1] == five_cards_1[1]:
                    if five_cards_0[0] > five_cards_1[0]:
                        return [1,0]
                    if five_cards_0[0] < five_cards_1[0]:
                        return [0,1] 
                    if five_cards_0[0] == five_cards_1[0]:
                        return [1,1]
        
        if hand0_category == 3:
            seen = []
            duplicated0 = []
            five_cards_0 = []
            five_cards_1 = []
            handcard0 = hand0.get_hand_five_cards()
            handcard1 = hand1.get_hand_five_cards()
            for i in range(5):              
                five_cards_0.append(handcard0[i][1])
            for _ in five_cards_0:  
                if _ not in seen:  
                    seen.append(_)
                else:
                    duplicated0.append(_)            
            seen = []
            duplicated1 = []
            for i in range(5):              
                five_cards_1.append(handcard1[i][1])
            for _ in five_cards_1:  
                if _ not in seen:  
                    seen.append(_)
                else:
                    duplicated1.append(_) 
            
            if RANKS.index(duplicated0[0][0]) > RANKS.index(duplicated0[1][0]):
                large_pair0 = RANKS.index(duplicated0[0][0])
                small_pair0 = RANKS.index(duplicated0[1][0])
            else:
                large_pair0 = RANKS.index(duplicated0[1][0])
                small_pair0 = RANKS.index(duplicated0[0][0])
            
            if RANKS.index(duplicated1[0][0]) > RANKS.index(duplicated1[1][0]):
                large_pair1 = RANKS.index(duplicated1[0][0])
                small_pair1 = RANKS.index(duplicated1[1][0])
            else:
                large_pair1 = RANKS.index(duplicated1[1][0])
                small_pair1 = RANKS.index(duplicated1[0][0])
            
            if large_pair0 > large_pair1:
                return [1,0]
            if large_pair0 < large_pair1:
                return [0,1]
            if large_pair0 == large_pair1:
                if small_pair0 > small_pair1:
                    return [1,0]
                if small_pair0 < small_pair1:
                    return [0,1]
                if small_pair0 == small_pair1:
                    return [1,1]
                    #five_cards_0.sort()
                    #five_cards_1.sort()
                    #for _ in range (2):
                       # five_cards_0.remove(large_pair0)
                      #  five_cards_0.remove(small_pair0)
                      #  five_cards_1.remove(large_pair0)
                        #five_cards_1.remove(small_pair0)
                    #if RANKS.index(five_cards_0[0][1]) > RANKS.index(five_cards_1[0][1]):
                        #return [1, 0]
                    #if RANKS.index(five_cards_0[0][1]) < RANKS.index(five_cards_1[0][1]):
                        #return [0, 1]
                    #if RANKS.index(five_cards_0[0][1]) == RANKS.index(five_cards_1[0][1]):
                        #return [1, 1]

        if hand0_category == 2:
            seen = []
            duplicated0 = []
            five_cards_0 = []
            five_cards_1 = []
            handcard0 = hand0.get_hand_five_cards()
            handcard1 = hand1.get_hand_five_cards()
            for i in range(5):              
                five_cards_0.append(handcard0[i][1])
            for _ in five_cards_0:  
                if _ not in seen:  
                    seen.append(_)
                else:
                    duplicated0.append(_)            
            seen = []
            duplicated1 = []
            for i in range(5):              
                five_cards_1.append(handcard1[i][1])
            for _ in five_cards_1:  
                if _ not in seen:  
                    seen.append(_)
                else:
                    duplicated1.append(_) 
            
            if RANKS.index(duplicated0[0][0]) > RANKS.index(duplicated1[0][0]):
                return [1, 0]
            
            if RANKS.index(duplicated0[0][0]) > RANKS.index(duplicated1[0][0]):
                return [0, 1]
            if RANKS.index(duplicated0[0][0]) == RANKS.index(duplicated1[0][0]):
                    for _ in range (2):
                        five_cards_0.remove(duplicated0[0][0])
                        five_cards_1.remove(duplicated1[0][0])
                    five_cards_0.sort()
                    five_cards_1.sort()

                    if RANKS.index(five_cards_0[2]) > RANKS.index(five_cards_1[2]):
                        return [1, 0]
                    if RANKS.index(five_cards_0[2]) < RANKS.index(five_cards_1[2]):
                        return [0, 1]
                    if RANKS.index(five_cards_0[2]) == RANKS.index(five_cards_1[2]):
                        if RANKS.index(five_cards_0[1]) > RANKS.index(five_cards_1[1]):
                            return [1, 0]
                        if RANKS.index(five_cards_0[1]) < RANKS.index(five_cards_1[1]):
                            return [0, 1]
                        if RANKS.index(five_cards_0[1]) == RANKS.index(five_cards_1[1]):
                            if RANKS.index(five_cards_0[0]) > RANKS.index(five_cards_1[0]):
                                return [1, 0]
                            if RANKS.index(five_cards_0[0]) < RANKS.index(five_cards_1[0]):
                                return [0, 1]
                            if RANKS.index(five_cards_0[0]) == RANKS.index(five_cards_1[0]):
                                return [1, 1]
            else:
                return [1, 1]

            if hand0_category == 1:

                for i in range(5):              
                    five_cards_0.append(RANKS.index(handcard0[i][1]))
                for i in range(5):              
                    five_cards_1.append(RANKS.index(handcard1[i][1]))
                five_cards_0.sort()
                five_cards_1.sort()
                if five_cards_0[4] > five_cards_1[4]:
                    return [1, 0]              
                if five_cards_0[4] < five_cards_1[4]:
                    return [0, 1]
                if five_cards_0[4] == five_cards_1[4]:
                    if five_cards_0[3] > five_cards_1[3]:
                        return [1, 0]              
                    if five_cards_0[3] < five_cards_1[3]:
                        return [0, 1]
                    if five_cards_0[3] == five_cards_1[3]:
                        if five_cards_0[2] > five_cards_1[2]:
                            return [1, 0]              
                        if five_cards_0[2] < five_cards_1[2]:
                            return [0, 1]
                        if five_cards_0[2] == five_cards_1[2]:
                            if five_cards_0[1] > five_cards_1[1]:
                                return [1, 0]              
                            if five_cards_0[1] < five_cards_1[1]:
                                return [0, 1]
                            if five_cards_0[1] == five_cards_1[1]:
                                if five_cards_0[1] > five_cards_1[1]:
                                    return [1, 0]              
                                if five_cards_0[1] < five_cards_1[1]:
                                    return [0, 1]
                                if five_cards_0[1] == five_cards_1[1]:
                                    return [1, 1]

        else:
            return [1, 1]
    else:
        return [1, 1]


