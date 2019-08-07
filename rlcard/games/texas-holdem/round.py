# -*- coding: utf-8 -*-
"""Implement Texasholdem Round class"""
import sys
from core import Round
from dealer import TexasDealer



class TexasRound(Round):
   def start_new_round(self):
        self._round_count += 1
        action = ''
        player_is_in = True
        bet_amount = 0
        round_winner = -1
        # round_winner not yet determined : -1
        # Draw : 0 , house wins : 1 , player wins : 2

        print ("---------------------ROUND", self._round_count , "-----------------------")
        print (self._player.name , "has ", self._player.get_chips(), "chips")
        print (self._house.name , "has ", self._house.get_chips(), "chips")
        print ("Big blind is", self._big)


        print ("Dealer has dealt 2 cards for each player")
        self._deck.reset_deck()
        self._deck.deal_to(self._player)
        self._deck.deal_to(self._house)
        self._deck.deal_to(self._player)
        self._deck.deal_to(self._house)

        # Put up an Ante before dealing cards
        self.transfer_chips_and_display_cards(self._big)

        player_is_in, action, bet_amount = self.ask_for_user_action()
        if player_is_in:
            print ("----------------------------------------------------")
            print ("Player", action)
            print ("This is the FLOP")
            self._deck.deal_to(self._board)
            self._deck.deal_to(self._board)
            self._deck.deal_to(self._board)

            self.transfer_chips_and_display_cards(bet_amount)
            player_is_in, action, bet_amount = self.ask_for_user_action()
        else:
            pass

        if player_is_in:
            print ("----------------------------------------------------")
            print ("Player", action)
            print ("This is the TURN")
            self._deck.deal_to(self._board)

            self.transfer_chips_and_display_cards(bet_amount)
            player_is_in, action, bet_amount = self.ask_for_user_action()
        else:
            pass

        if player_is_in:
            print ("----------------------------------------------------")
            print ("Player", action)
            print ("This is the RIVER")
            self._deck.deal_to(self._board)

            self.transfer_chips_and_display_cards(bet_amount)
            player_is_in, action, bet_amount = self.ask_for_user_action()
        else:
            pass

        if player_is_in:
            print ("----------------------------------------------------")
            print ("Player", action)
            print ("This is the FINAL")
            #TODO : Compare Hands and transfer money to winner
            self.transfer_chips_and_display_cards(bet_amount)

            #add 5 cards from board to each player
            board_cards = self._board.get_cards()
            player_cards = self._player.get_cards()
            house_cards = self._house.get_cards()

            self._player.add_card_to_hand(board_cards)
            self._player.add_card_to_hand(player_cards)
            self._house.add_card_to_hand(board_cards)
            self._house.add_card_to_hand(house_cards)


            #compare the hands
            round_winner = self.compare_hands()

            # transferring money to the winner
            print ("\n")
            if round_winner == 1:
                print ("The house WINS this round")
                self.transfer_chips(self._board , self._house, "all")
            elif round_winner == 2:
                print ("Player WINS this round")
                self.transfer_chips(self._board , self._player, "all")
            elif round_winner == 0:
                print ("DRAWS , player and the house split the pot")
                half = self._board.get_chips() / 2
                self.transfer_chips(self._board , self._house, half)
                self.transfer_chips(self._board , self._player, half)

            house_5_cards = self._house.get_hand_five_cards()
            player_5_cards = self._player.get_hand_five_cards()

            print ("Common cards on table:" , board_cards)
            print ("House has 2 cards:", house_cards)
            print ("Player has 2 cards:" , player_cards)
            print ("\n")
            print ("House has", self._house.get_hand_name() , house_5_cards)
            print ("Player has", self._player.get_hand_name() ,  player_5_cards)
            print (self._player.name , ":", self._player.get_chips(), "chips." \
                , self._house.name , ":", self._house.get_chips(), "chips. " \
                , "Pot:", self._board.get_chips(), "chips")

        else:
            print ("Player folded. The house WINS this round")
            self.transfer_chips(self._board , self._house, "all")
            print (self._player.name , ":", self._player.get_chips(), "chips." \
                , self._house.name , ":", self._house.get_chips(), "chips. " \
                , "Pot:", self._board.get_chips(), "chips")

        # reset players cards
        self._player.reset_player_cards()
        self._house.reset_player_cards()
        self._board.reset_player_cards()


    def compare_hands(self):
        #evaluate player's hand
        self._player.evaluate()
        self._house.evaluate()

        #compare hands
        house_category = self._house.get_hand_category()
        player_category = self._player.get_hand_category()
        if house_category > player_category:
            return 1
        elif house_category < player_category:
            return 2
        elif house_category == player_category:
            #compare equal category
            house_5_cards = self._house.get_hand_five_cards()
            player_5_cards = self._player.get_hand_five_cards()
            for i in reversed(xrange(5)):
                house_card_rank = house_5_cards[i][0]
                player_card_rank = player_5_cards[i][0]
                if RANKS.index(house_card_rank) > RANKS.index(player_card_rank):
                    return 1
                elif RANKS.index(house_card_rank) < RANKS.index(player_card_rank):
                    return 2
                else:
                    pass
            # this else below belongs to for..else.. statement
            # return 0 means both hands are equal
            else:
                return 0


    def avaliable_orders(self):
        action = ''
        action_list = ['C','R','F']

        if self._player.get_chips() <= 0 or self._house.get_chips() <= 0 :
            action_list = ['C','F']
            print ("No more chips. Raise is not available")



    def transfer_chips_and_display_cards(self, bet_amount):
        self.transfer_chips(self._player , self._board, bet_amount)
        self.transfer_chips(self._house , self._board, bet_amount)
        self._player.display_cards()
        self._house.display_cards()
        self._board.display_cards()
        print (self._player.name , ":", self._player.get_chips(), "chips." \
            , self._house.name , ":", self._house.get_chips(), "chips. " \
            , "Pot:", self._board.get_chips(), "chips")