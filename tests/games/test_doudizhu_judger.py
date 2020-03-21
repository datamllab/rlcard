import unittest

from rlcard.games.doudizhu.utils import CARD_TYPE
from rlcard.games.doudizhu.judger import DoudizhuJudger as Judger

class TestDoudizhuGame(unittest.TestCase):

    def test_playable_cards_from_hand(self):
        # #solo
        # in_cards, not_in_cards, hand = ('3', '4', '5', '6', '8', '9', 'J', 'Q', 'B', 'R'), (), '334445555689JQBR'
        # playable_cards = Judger.playable_cards_from_hand(hand)
        # for e in in_cards:
        #     self.assertIn(e, playable_cards)
        # for e in not_in_cards:
        #     self.assertNotIn(e, playable_cards)

        # #pair
        # in_cards, not_in_cards, hand = ('33', '44', '55'), (), '334445555689JQBR'
        # playable_cards = Judger.playable_cards_from_hand(hand)
        # for e in in_cards:
        #     self.assertIn(e, playable_cards)
        # for e in not_in_cards:
        #     self.assertNotIn(e, playable_cards)
 
        # #trio
        # in_cards, not_in_cards, hand = ('444', '555'), (), '334445555689JQBR'
        # playable_cards = Judger.playable_cards_from_hand(hand)
        # for e in in_cards:
        #     self.assertIn(e, playable_cards)
        # for e in not_in_cards:
        #     self.assertNotIn(e, playable_cards)

        # #bomb
        # in_cards, not_in_cards, hand = ('5555', ), (), '334445555689JQBR'
        # playable_cards = Judger.playable_cards_from_hand(hand)
        # for e in in_cards:
        #     self.assertIn(e, playable_cards)
        # for e in not_in_cards:
        #     self.assertNotIn(e, playable_cards)

        # #rocket
        # in_cards, not_in_cards, hand = ('BR', ), (), '334445555689JQBR'
        # playable_cards = Judger.playable_cards_from_hand(hand)
        # for e in in_cards:
        #     self.assertIn(e, playable_cards)
        # for e in not_in_cards:
        #     self.assertNotIn(e, playable_cards)

        # #solo_chain_5 -- #solo_chain_12
        # in_cards = ('34567', '345678', '3456789', '3456789T', '3456789TJ',
        #     '3456789TJQ', '3456789TJQK', '3456789TJQKA', '45678', '456789',
        #     '3456789T', '3456789TJ', '456789TJQ', '456789TJQK', '456789TJQKA',
        #     '56789', '56789T', '56789TJ', '56789TJQ', '56789TJQK', '56789TJQKA',
        #     '6789T', '6789TJ', '6789TJQ', '6789TJQK', '6789TJQKA', '789TJ',
        #     '789TJQ', '789TJQK', '789TJQKA', '89TJQ', '89TJQK',
        #     '89TJQKA', '9TJQK', '9TJQKA', 'TJQKA')
        # not_in_cards = ('JQKA2', )
        # hand = '3344455556789TJQKA2BR'
        # playable_cards = Judger.playable_cards_from_hand(hand)
        # for e in in_cards:
        #     self.assertIn(e, playable_cards)
        # for e in not_in_cards:
        #     self.assertNotIn(e, playable_cards)

        # #pair_chain_3 -- #pair_chain_10
        # in_cards = ('334455', '33445566', '3344556677', '334455667788', '33445566778899',
        # '33445566778899TT', '33445566778899TTJJ', '33445566778899TTJJQQ', '445566', '44556677',
        # '4455667788', '445566778899', '445566778899TT', '445566778899TTJJ', '445566778899TTJJQQ',
        # '445566778899TTJJQQKK', '556677', '55667788', '5566778899', '5566778899TT',
        # '5566778899TTJJ', '5566778899TTJJQQ', '5566778899TTJJQQKK', '5566778899TTJJQQKKAA',
        # '667788', '66778899', '66778899TT', '66778899TTJJ', '66778899TTJJQQ',
        # '66778899TTJJQQKK', '66778899TTJJQQKKAA', '778899', '778899TT', '778899TTJJ',
        # '778899TTJJQQ', '778899TTJJQQKK', '778899TTJJQQKKAA', '8899TT', '8899TTJJ',
        # '8899TTJJQQ', '8899TTJJQQKK', '8899TTJJQQKKAA', '99TTJJ', '99TTJJQQ', 
        # '99TTJJQQKK', '99TTJJQQKKAA', 'TTJJQQ', 'TTJJQQKK', 'TTJJQQKKAA',
        # 'JJQQKK', 'JJQQKKAA', 'QQKKAA')
        # not_in_cards = ('33445566778899TTJJQQKK', 'KKAA22')
        # hand =  '33444555566778899TTJJQQKKAA22'
        # playable_cards = Judger.playable_cards_from_hand(hand)
        # for e in in_cards:
        #     self.assertIn(e, playable_cards)
        # for e in not_in_cards:
        #     self.assertNotIn(e, playable_cards)

        # #trio_chain_2 -- #trio_chain_6
        # in_cards = ('333444', '333444555', '333444555666', '333444555666777', '333444555666777888',
        # '444555', '444555666', '444555666777', '444555666777888', '444555666777888999',
        # '555666', '555666777', '555666777888', '555666777888999', '555666777888999TTT',
        # '666777', '666777888', '666777888999', '666777888999TTT', '666777888999TTTJJJ',
        # '777888', '777888999', '777888999TTT', '777888999TTTJJJ', '777888999TTTJJJQQQ',
        # '888999', '888999TTT', '888999TTTJJJ', '888999TTTJJJQQQ', '888999TTTJJJQQQKKK',
        # '999TTT', '999TTTJJJ', '999TTTJJJQQQ', '999TTTJJJQQQKKK', '999TTTJJJQQQKKKAAA',
        # 'TTTJJJ', 'TTTJJJQQQ', 'TTTJJJQQQKKK', 'TTTJJJQQQKKKAAA',
        # 'JJJQQQ', 'JJJQQQKKK', 'JJJQQQKKKAAA',
        # 'QQQKKK', 'QQQKKKAAA',
        # 'KKKAAA')
        # not_in_cards = ('333444555666777888999', 'AAA222')
        # hand =  '333444455556667778889999TTTJJJQQQKKKAAA222BR'
        # playable_cards = Judger.playable_cards_from_hand(hand)
        # for e in in_cards:
        #     self.assertIn(e, playable_cards)
        # for e in not_in_cards:
        #     self.assertNotIn(e, playable_cards)

        # #trio_solo, trio_pair
        # in_cards = ('3777', '4777', '5777', '6777', '7778',
        # '7772', '44777', '55777', '77788', '77722')
        # not_in_cards = ()
        # hand =  '344455677778889TJQKA2222BR'
        # playable_cards = Judger.playable_cards_from_hand(hand)
        # for e in in_cards:
        #     self.assertIn(e, playable_cards)
        # for e in not_in_cards:
        #     self.assertNotIn(e, playable_cards)

        # #trio_solo_chain_2 -- trio_solo_chain_5
        # in_cards = ('34777888', '3777888T', '3456777888999TTTJJJQ', '66777888')
        # not_in_cards = ('37777888', '777888999TTTJJJQK2BR', '777888999TTTJJJJ')
        # hand =  '34556677778888999TTTTJJJJQQQQKA2BR'
        # playable_cards = Judger.playable_cards_from_hand(hand)
        # for e in in_cards:
        #     self.assertIn(e, playable_cards)
        # for e in not_in_cards:
        #     self.assertNotIn(e, playable_cards)

        # #trio_pair_chain_2 -- #trio_pair_chain_4
        # in_cards = ('5566777888', '55777888TT')
        # not_in_cards = ('777888QQQQ', )
        # hand =  '34556677778888999TTTTJJJJQQQQKA2BR'
        # playable_cards = Judger.playable_cards_from_hand(hand)
        # for e in in_cards:
        #     self.assertIn(e, playable_cards)
        # for e in not_in_cards:
        #     self.assertNotIn(e, playable_cards)

        # #four_two_solo, #four_two_pair
        # in_cards = ('357777', '557777', '567777', '777788', '55667777', '66777799', '557777TT', '55777788')
        # not_in_cards = ('77778888', )
        # hand =  '34556677778888999TTTTJJJJQQQQKA2BR'
        # playable_cards = Judger.playable_cards_from_hand(hand)
        # for e in in_cards:
        #     self.assertIn(e, playable_cards)
        # for e in not_in_cards:
        #     self.assertNotIn(e, playable_cards)

        playable_cards = list(Judger.playable_cards_from_hand('3333444455556666777788889999TTTTJJJJQQQQKKKKAAAA2222BR'))
        all_cards_list = CARD_TYPE[1]
        for c in playable_cards:
            # if (c not in all_cards_list):
            #     print(c)
            self.assertIn(c, all_cards_list)
        for c in all_cards_list:
            # if (c not in playable_cards):
            #     print('\t' + c)
            self.assertIn(c, playable_cards)
        self.assertEqual(len(playable_cards), len(all_cards_list))

if __name__ == '__main__':
    unittest.main()
