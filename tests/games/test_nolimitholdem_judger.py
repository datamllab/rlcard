import unittest
import numpy as np
from rlcard.games.nolimitholdem.player import NolimitholdemPlayer as Player
from rlcard.games.base import Card
from rlcard.games.limitholdem.judger import LimitHoldemJudger as Judger
from rlcard.games.limitholdem.utils import Hand 


rand_state = np.random.RandomState()

class TestNolimitholdemGame(unittest.TestCase):

    def get_players(self, num_players=2):
        players = []
        
        for i in range(num_players):
            players.append(Player(i, 100 + 100*i, rand_state))
            players[i].bet(players[i].remained_chips) # All in
            
        return players
    
    def get_hands(self, player_hands, public_card):
        hands = []
        for hand in player_hands:
            hands.append(hand + public_card)
        return hands        
    
    def test_judge_with_4_players(self):

        '''
        suit_list = ['S', 'H', 'D', 'C']
        rank_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
        '''
        players = self.get_players(4)
        
        
        public_card = [Card('S', 'A'), Card('S', 'K'), Card('S', 'Q'), Card('S', '2'), Card('S', '3')]
        hands = [[Card('S', 'J'), Card('S', 'T')],
                 [Card('S', '4'), Card('S', '5')], 
                 [Card('S', '9'), Card('C', 'T')], 
                 [Card('H', 'T'), Card('C', 'J')]]
        
        payoffs = Judger(rand_state).judge_game(players, self.get_hands(hands, public_card))
        self.assertEqual(payoffs, [300, 100, -100, -300])
        
        public_card = [Card('H', 'A'), Card('H', 'K'), Card('S', 'Q'), Card('S', 'T'), Card('S', '9')]
        
        hands = [[Card('S', 'A'), Card('H', '4')], 
                 [Card('D', 'A'), Card('H', '5')], 
                 [Card('D', 'K'), Card('H', '6')], 
                 [Card('S', 'K'), Card('H', '7')]]
        
        payoffs = Judger(rand_state).judge_game(players, self.get_hands(hands, public_card))
        self.assertEqual(payoffs, [100, 300, -200, -200])
        
    def test_judge_with_6_players(self):
        rand_state = np.random.RandomState()
        
        public_card = [Card('S', 'A'), Card('S', 'K'), Card('D', 'Q'), Card('D', 'T'), Card('C', '9')]
        players = self.get_players(6)
        
        hands = [[Card('C', 'A'), Card('H', '2')], 
                 [Card('D', 'A'), Card('H', '3')], 
                 [Card('C', 'K'), Card('C', '2')], 
                 [Card('D', 'K'), Card('C', '3')],
                 [Card('C', 'Q'), Card('S', '2')], 
                 [Card('D', 'Q'), Card('S', '3')]]

        payoffs = Judger(rand_state).judge_game(players, self.get_hands(hands, public_card))
        self.assertEqual(payoffs, [200, 600, -100, 100, -400, -400])


if __name__ == '__main__':
    unittest.main()
