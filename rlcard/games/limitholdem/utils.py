

class Hand:
    def __init__(self, all_cards):
        self.all_cards = all_cards # two hand cards + five public cards
        self.category = 0
        #type of a players' best five cards, greater combination has higher number eg: 0:"Not_Yet_Evaluated" 1: "High_Card" , 9:"Straight_Flush"
        self.best_five = []
        #the largest combination of five cards in all the seven cards
        self.flush_cards = []
        #cards with same suit
        self.cards_by_rank = []
        #cards after sort
        self.product = 1
        #cards’ type indicator
        self.RANK_TO_STRING = {2: "2", 3: "3", 4: "4", 5: "5", 6: "6",
                               7: "7", 8: "8", 9: "9", 10: "T", 11: "J", 12: "Q", 13: "K", 14: "A"}
        self.RANK_LOOKUP = "23456789TJQKA"
        self.SUIT_LOOKUP = "SCDH"

    def get_hand_five_cards(self):
        '''
        Get the best five cards of a player
        Returns:
            (list): the best five cards among the seven cards of a player
        '''
        return self.best_five

    def _sort_cards(self):
        '''
        Sort all the seven cards ascendingly according to RANK_LOOKUP
        '''
        self.all_cards = sorted(
            self.all_cards, key=lambda card: self.RANK_LOOKUP.index(card[1]))

    def evaluateHand(self):
        """
        Evaluate all the seven cards, get the best combination catagory
        And pick the best five cards (for comparing in case 2 hands have the same Category) .
        """
        if len(self.all_cards) != 7:
            raise Exception(
                "There are not enough 7 cards in this hand, quit evaluation now ! ")

        self._sort_cards()
        self.cards_by_rank, self.product = self._getcards_by_rank(
            self.all_cards)

        if self._has_straight_flush():
            self.category = 9
            #Straight Flush
        elif self._has_four():
            self.category = 8
            #Four of a Kind
            self.best_five = self._get_Four_of_a_kind_cards()
        elif self._has_fullhouse():
            self.category = 7
            #Full house
            self.best_five = self._get_Fullhouse_cards()
        elif self._has_flush():
            self.category = 6
            #Flush
            i = len(self.flush_cards)
            self.best_five = [card for card in self.flush_cards[i-5:i]]
        elif self._has_straight(self.all_cards):
            self.category = 5
            #Straight
        elif self._has_three():
            self.category = 4
            #Three of a Kind
            self.best_five = self._get_Three_of_a_kind_cards()
        elif self._has_two_pairs():
            self.category = 3
            #Two Pairs
            self.best_five = self._get_Two_Pair_cards()
        elif self._has_pair():
            self.category = 2
            #One Pair
            self.best_five = self._get_One_Pair_cards()
        elif self._has_high_card():
            self.category = 1
            #High Card
            self.best_five = self._get_High_cards()

    def _has_straight_flush(self):
        '''
        Check the existence of straight_flush cards
        Returns:
            True: exist
            False: not exist
        '''
        self.flush_cards = self._getflush_cards()
        if len(self.flush_cards) > 0:
            straightflush_cards = self._get_straightflush_cards()
            if len(straightflush_cards) > 0:
                self.best_five = straightflush_cards
                return True
        return False

    def _get_straightflush_cards(self):
        '''
        Pick straight_flush cards
        Returns:
            (list): the straightflush cards
        '''
        straightflush_cards = self._get_straight_cards(self.flush_cards)
        return straightflush_cards

    def _getflush_cards(self):
        '''
        Pick flush cards
        Returns:
            (list): the flush cards
        '''
        card_string = ''.join(self.all_cards)
        for suit in self.SUIT_LOOKUP:
            suit_count = card_string.count(suit)
            if suit_count >= 5:
                flush_cards = [
                    card for card in self.all_cards if card[0] == suit]
                return flush_cards
        return []

    def _has_flush(self):
        '''
        Check the existence of flush cards
        Returns:
            True: exist
            False: not exist
        '''
        if len(self.flush_cards) > 0:
            return True
        else:
            return False

    def _has_straight(self, all_cards):
        '''
        Check the existence of straight cards
        Returns:
            True: exist
            False: not exist
        '''
        diff_rank_cards = self._get_different_rank_list(all_cards)
        self.best_five = self._get_straight_cards(diff_rank_cards)
        if len(self.best_five) != 0:
            return True
        else:
            return False
    @classmethod
    def _get_different_rank_list(self, all_cards):
        '''
        Get cards with different ranks, that is to say, remove duplicate-ranking cards, for picking straight cards' use
        Args:
            (list): two hand cards + five public cards
        Returns:
            (list): a list of cards with duplicate-ranking cards removed
        '''
        different_rank_list = []
        different_rank_list.append(all_cards[0])
        for card in all_cards:
            if(card[1] != different_rank_list[-1][1]):
                different_rank_list.append(card)
        return different_rank_list

    def _get_straight_cards(self, Cards):
        '''
        Pick straight cards
        Returns:
            (list): the straight cards
        '''
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
        '''
        Get cards by rank
        Args:
            (list): # two hand cards + five public cards
        Return:
            card_group(list): cards after sort
            product(int):cards‘ type indicator
        '''
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
                # if there is two Pair, then product = 4 ( 2, 1, 2, 1, 1) or product = 8 ( 2, 2, 2, 1)
                # if there is one Pair, then product = 2 (2, 1, 1, 1, 1, 1)
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
        '''
        Check the existence of four cards
        Returns:
            True: exist
            False: not exist
        '''
        if self.product == 5 or self.product == 10 or self.product == 15:
            return True
        else:
            return False

    def _has_fullhouse(self):
        '''
        Check the existence of fullhouse cards
        Returns:
            True: exist
            False: not exist
        '''
        if self.product == 6 or self.product == 9 or self.product == 12:
            return True
        else:
            return False

    def _has_three(self):
        '''
        Check the existence of three cards
        Returns:
            True: exist
            False: not exist
        '''
        if self.product == 3:
            return True
        else:
            return False

    def _has_two_pairs(self):
        '''
        Check the existence of 2 pair cards
        Returns:
            True: exist
            False: not exist
        '''
        if self.product == 4 or self.product == 8:
            return True
        else:
            return False

    def _has_pair(self):
        '''
        Check the existence of 1 pair cards
        Returns:
            True: exist
            False: not exist
        '''
        if self.product == 2:
            return True
        else:
            return False

    def _has_high_card(self):
        '''
        Check the existence of high cards
        Returns:
            True: exist
            False: not exist
        '''
        if self.product == 1:
            return True
        else:
            return False

    def _get_Four_of_a_kind_cards(self):
        '''
        Get the four of a kind cards among a player's cards
        Returns:
            (list): best five hand cards after sort
        '''
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
        '''
        Get the fullhouse cards among a player's cards
        Returns:
            (list): best five hand cards after sort
        '''
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
        '''
        Get the three of a kind cards among a player's cards
        Returns:
            (list): best five hand cards after sort
        '''
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
        '''
        Get the two pair cards among a player's cards
        Returns:
            (list): best five hand cards after sort
        '''
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
        '''
        Get the one pair cards among a player's cards
        Returns:
            (list): best five hand cards after sort
        '''
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
        '''
        Get the high cards among a player's cards
        Returns:
            (list): best five hand cards after sort
        '''
        High_cards = self.all_cards[2:7]
        return High_cards

def compare_ranks(position, handcard0, handcard1):
    '''
    Compare cards in same position of plays' five handcards
    Args:
        position(int): the position of a card in a sorted handcard
        handcard0(list) : five best cards of player0
        handcard1(list) : five best cards of player1
    Returns:
        [0, 1]: player1 wins
        [1, 0]: player0 wins
        [1, 1]: draw
    '''
    RANKS = '23456789TJQKA'
    if RANKS.index(handcard0[position][1]) > RANKS.index(handcard1[position][1]):
        return [1, 0]
    if RANKS.index(handcard0[position][1]) < RANKS.index(handcard1[position][1]):
        return [0, 1]
    if RANKS.index(handcard0[position][1]) == RANKS.index(handcard1[position][1]):
        return [1, 1]

def determine_winner(key_index, hand0_5_cards, hand1_5_cards):
    '''
    Determine who wins
    Args:
        key_index(int): the position of a card in a sorted handcard
        hand0_5_cards(list) : five best cards of player0
        hand0_5_cards(list) : five best cards of player1
    Returns:
        [0, 1]: player1 wins
        [1, 0]: player0 wins
        [1, 1]: draw
    '''
    for _ in key_index:
        winner = compare_ranks(_, hand0_5_cards, hand1_5_cards)
        if winner != [1, 1]:
            break
    return winner

def compare_hands(hand0, hand1):
    '''
    Compare two palyer's all seven cards
    Args:
        hand0(list) : all the seven cards of player0
        hand1(list) : all the seven cards of player1
    Returns:
        [0, 1]: player1 wins
        [1, 0]: player0 wins
        [1, 1]: draw
    '''

    if hand0 == None:
        return [0, 1]
    elif hand1 == None:
        return [1, 0]
    hand0 = Hand(hand0)
    hand1 = Hand(hand1)
    hand0.evaluateHand()
    hand1.evaluateHand()
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
        if hand0_category == 9 or hand0_category == 5 or hand0_category == 8:
            return determine_winner([0], hand0_5_cards, hand1_5_cards)
        if hand0_category == 7:
            return determine_winner([2, 0], hand0_5_cards, hand1_5_cards)
        if hand0_category == 4:
            return determine_winner([2, 1, 0], hand0_5_cards, hand1_5_cards)
        if hand0_category == 3:
            return determine_winner([4, 2, 0], hand0_5_cards, hand1_5_cards)
        if hand0_category == 2:
            return determine_winner([4, 2, 1, 0], hand0_5_cards, hand1_5_cards)
        if hand0_category == 1 or hand0_category == 6:
            return determine_winner([4, 3, 2, 1, 0], hand0_5_cards, hand1_5_cards)