from rlcard.core import Judger
from rlcard.games.simpletexasholdem.player import Player
from rlcard.games.simpletexasholdem.game import LimitHoldemGame as game
RANKS = '23456789TJQKA'
class LimitHoldemJudger(Judger):
    def __init__(self):

        pass
    def judge_round(self, player):
        # coming soon
        pass

    def judge_game(self, game):
    #def compare_hands(self):
        #evaluate player's hand
        game.player0.evaluate()
        game.player1.evaluate()

        #compare hands
        house_category = game.player0.get_hand_category()
        player_category = game.player1.get_hand_category()
        if house_category > player_category:
            return 1
        elif house_category < player_category:
            return 2
        elif house_category == player_category:
            #compare equal category
            house_5_cards = game.player0.get_hand_five_cards()
            player_5_cards = game.player1.get_hand_five_cards()
            for i in reversed(range(5)):
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