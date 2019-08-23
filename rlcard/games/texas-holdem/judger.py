# -*- coding: utf-8 -*-
# For comparing cards
RANK_TO_STRING = {2: "2", 3: "3", 4: "4", 5: "5", 6: "6",7: "7",8: "8",9: "9",10: "T",11: "J",12: "Q",13: "K",14: "A"}
RANK_LOOKUP = "0023456789TJQKA2345"
SUIT_LOOKUP = "SCDH"

class Methods:
	def __init__(self, name):
		self._all_cards = []
		self.name = name            #   Player1_hand , Player2_hand
		self._category = 0			#	0:"Not_Yet_Evaluated" 1: "High_Card" , 9:"Straight_Flush"
		self._five_cards = []        #  ['4D','5D','9S','AS', 'AD']
		self._hand_name = ""        # High_Card , One_Pair , Flush etc
		self._flush_cards = []	    # self._flush_cards = ['4D','5D','6D','7D','8D','AD']
		self._cards_by_rank = []     
		self._product = 1

	def setCards(self,seven_cards = []):
		self._all_cards = seven_cards

	def _sort_cards(self):
		self._all_cards = sorted(self._all_cards ,key=lambda card: RANK_LOOKUP.index(card[0]))

	def evaluateHand(self):
		"""
		Do Hand Evaluation and
		Get the best Five Cards ( for displaying, or comparing in case 2 hands have the same Category) .

		"""
		if len(self._all_cards) != 7 :
			raise Exception("There are not enough 7 cards in this hand, quit evaluation now ! ")


		self._sort_cards()
		self._cards_by_rank , self._product = self._get_cards_by_rank(self._all_cards)


		if self._has_straight_flush() :
			self._category = 9
			self._hand_name = "Straight Flush"
		elif self._has_four() :
			self._category = 8
			self._hand_name = "Four of a Kind"
			self._five_cards = self._get_Four_of_a_kind_cards()
		elif self._has_fullhouse() :
			self._category = 7
			self._hand_name = "Full house"
			self._five_cards = self._get_Fullhouse_cards()
		elif self._has_flush() :
			self._category = 6
			self._hand_name = "Flush"
			i = len(self._flush_cards)
			self._five_cards = [card for card in self._flush_cards[i-5:i]]
		elif self._has_straight(self._all_cards) :
			self._category = 5
			self._hand_name = "Straight"
		elif self._has_three() :
			self._category = 4
			self._hand_name = "Three of a Kind"
			self._five_cards = self._get_Three_of_a_kind_cards()
		elif self._has_two_pairs() :
			self._category = 3
			self._hand_name = "Two Pairs"
			self._five_cards = self._get_Two_Pair_cards()
		elif self._has_pair() :
			self._category = 2
			self._hand_name = "One Pair"
			self._five_cards = self._get_One_Pair_cards()
		elif self._has_high_card() :
			self._category = 1
			self._hand_name = "High Card"
			self._five_cards = self._get_High_cards()


	def _has_straight_flush(self):
		self._flush_cards = self._get_flush_cards()
		if len(self._flush_cards) > 0 :
			straight_flush_cards = self._get_straight_flush_cards()
			if len(straight_flush_cards) > 0:
				self._five_cards = straight_flush_cards
				return True
		return False

	def _get_straight_flush_cards(self):
		straight_flush_cards = self._get_straight_cards(self._flush_cards)
		return straight_flush_cards


	def _get_flush_cards(self) :
		card_string = ''.join(self._all_cards)
		for suit in SUIT_LOOKUP:
			suit_count = card_string.count(suit)
			if suit_count >= 5 :
				flush_cards = [card for card in self._all_cards if card[1]== suit]
				return flush_cards
		return []

	def _has_flush(self):
		if len(self._flush_cards) > 0 :
			return True
		else:
			return False

	def _has_straight(self, all_cards) :
		diff_rank_cards = self._get_different_rank_list(all_cards)
		self._five_cards = self._get_straight_cards(diff_rank_cards)
		if len(self._five_cards) != 0 :
			return True
		else:
			return False

	def _get_different_rank_list(self, all_cards):
		different_rank_list = []
		different_rank_list.append(all_cards[0])
		for card in all_cards:
		    if(card[0] != different_rank_list[-1][0]):
        	     different_rank_list.append(card)
		return different_rank_list

	def _get_straight_cards(self, Cards):
		highest_card = Cards[-1]
		if highest_card[0] == 'A':
			Cards.insert(0,highest_card)

		i = len(Cards)
		while ( i - 5 >= 0):
			hand_to_check = ''.join(card[0] for card in Cards[i-5:i])
			is_straight = RANK_LOOKUP.find(hand_to_check)
			if is_straight > 0 :
				five_cards = [card for card in Cards[i-5:i]]
				return five_cards
			i -= 1
		return []

	def _get_cards_by_rank(self, all_cards):
		card_group = []
		card_group_element = []
		product = 1
		prime_lookup = {0:1, 1:1, 2:2, 3:3, 4:5}
		count = 0
		current_rank = 0

		for card in all_cards:
			rank = RANK_LOOKUP.index(card[0])
			if rank == current_rank :
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
				card_group_element.insert(0,count)
				card_group.append(card_group_element)
				# reset counting
				count = 1
				card_group_element = []
				card_group_element.append(card)
				current_rank = rank
		# the For Loop misses operation for the last card
		# These 3 lines below to compensate that
		product *= prime_lookup[count]
		card_group_element.insert(0,count)      # insert the number of same rank card to the beginning of the
		card_group.append(card_group_element)	# after the loop, there is still one last card to add
		return card_group , product

	def _has_four(self):
		if self._product == 5 or self._product == 10 or self._product == 15:
			return True
		else:
			return False

	def _has_fullhouse(self) :
		if self._product == 6 or self._product == 9 or self._product == 12:
			return True
		else:
			return False

	def _has_three(self) :
		if self._product == 3:
			return True
		else:
			return False

	def _has_two_pairs(self) :
		if self._product == 4 or self._product == 8:
			return True
		else:
			return False

	def _has_pair(self) :
		if self._product == 2:
			return True
		else:
			return False


	def _has_high_card(self) :
		if self._product == 1:
			return True
		else:
			return False

	def _get_Four_of_a_kind_cards(self):
		Four_of_a_Kind = []
		cards_by_rank = self._cards_by_rank
		cards_len = len(cards_by_rank)
		for i in reversed(xrange(cards_len)):
			if cards_by_rank[i][0] == 4 :
				Four_of_a_Kind = cards_by_rank.pop(i)
				break
		kicker = cards_by_rank[-1][1]     # The Last cards_by_rank[The Second element]
		Four_of_a_Kind[0] = kicker

		return Four_of_a_Kind

	def _get_Fullhouse_cards(self):
		Fullhouse = []
		cards_by_rank = self._cards_by_rank
		cards_len = len(cards_by_rank)
		for i in reversed(xrange(cards_len)):
			if cards_by_rank[i][0] == 3 :
				Trips = cards_by_rank.pop(i)[1:4]
				break
		for i in reversed(xrange(cards_len - 1)):
			if cards_by_rank[i][0] >= 2 :
				TwoPair = cards_by_rank.pop(i)[1:3]
				break
		Fullhouse = TwoPair + Trips
		return Fullhouse

	def _get_Three_of_a_kind_cards(self):
		Trip_cards = []
		cards_by_rank = self._cards_by_rank
		cards_len = len(cards_by_rank)
		for i in reversed(xrange(cards_len)):
			if cards_by_rank[i][0] == 3 :
				Trip_cards += cards_by_rank.pop(i)[1:4]
				break

		Trip_cards += cards_by_rank.pop(-1)[1:2]
		Trip_cards += cards_by_rank.pop(-1)[1:2]
		Trip_cards.reverse()
		return Trip_cards

	def _get_Two_Pair_cards(self):
		Two_Pair_cards = []
		cards_by_rank = self._cards_by_rank
		cards_len = len(cards_by_rank)
		for i in reversed(xrange(cards_len)):
			if cards_by_rank[i][0] == 2 and len(Two_Pair_cards) < 3 :
				Two_Pair_cards += cards_by_rank.pop(i)[1:3]

		Two_Pair_cards += cards_by_rank.pop(-1)[1:2]
		Two_Pair_cards.reverse()
		return Two_Pair_cards

	def _get_One_Pair_cards(self):
		One_Pair_cards = []
		cards_by_rank = self._cards_by_rank
		cards_len = len(cards_by_rank)
		for i in reversed(xrange(cards_len)):
			if cards_by_rank[i][0] == 2 :
				One_Pair_cards += cards_by_rank.pop(i)[1:3]
				break

		One_Pair_cards += cards_by_rank.pop(-1)[1:2]
		One_Pair_cards += cards_by_rank.pop(-1)[1:2]
		One_Pair_cards += cards_by_rank.pop(-1)[1:2]
		One_Pair_cards.reverse()
		return One_Pair_cards

	def _get_High_cards(self):
		High_cards = self._all_cards[2:7]
		return High_cards

	def show_player_cards(self):
		print ("Player %s has these cards %s" %(self.name, self._all_cards))

	def show_player_evaluated_hand_name(self):
		print ("The hand is %s" %(self._hand_name))

	def show_player_evaluated_five_cards(self):
		print ("Five cards with best hand are %s" %(self._five_cards))
