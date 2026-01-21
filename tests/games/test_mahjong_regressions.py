import unittest

from rlcard.games.mahjong.card import MahjongCard
from rlcard.games.mahjong.game import MahjongGame
from rlcard.games.mahjong.player import MahjongPlayer
from rlcard.games.mahjong.utils import init_deck


def _take_card(deck, card_str):
    for index, card in enumerate(deck):
        if card.get_str() == card_str:
            return deck.pop(index)
    raise AssertionError("Card not found in deck: {}".format(card_str))


def _fill_hand(deck, size, seed_cards):
    hand = list(seed_cards)
    while len(hand) < size:
        hand.append(deck.pop())
    return hand


def _make_card(code):
    if len(code) == 2 and code[0] in ("B", "C", "D") and code[1].isdigit():
        suit = {"B": "bamboo", "C": "characters", "D": "dots"}[code[0]]
        trait = code[1]
    else:
        suit = "winds" if code in {"East", "South", "West", "North"} else "dragons"
        trait = code.lower()
    card = MahjongCard(suit, trait)
    if suit in {"bamboo", "characters", "dots"}:
        card.set_index_num(int(trait) - 1)
    else:
        card.set_index_num(0)
    return card


class TestMahjongRegressions(unittest.TestCase):

    def test_chow_available_without_pong_gong(self):
        game = MahjongGame()
        game.init_game()

        deck = init_deck()
        discard_card = _take_card(deck, "characters-9")
        deck = [card for card in deck if card.get_str() != "characters-9"]

        chow_cards = [
            _take_card(deck, "characters-7"),
            _take_card(deck, "characters-8"),
        ]

        game.players[0].hand = _fill_hand(deck, 14, [discard_card])
        game.players[1].hand = _fill_hand(deck, 13, chow_cards)
        game.players[2].hand = _fill_hand(deck, 13, [])
        game.players[3].hand = _fill_hand(deck, 13, [])
        game.dealer.deck = deck
        game.dealer.table = []
        game.round.current_player = 0
        game.round.valid_act = False

        game.round.proceed_round(game.players, discard_card)

        state = game.get_state(game.round.current_player)
        self.assertEqual(state["valid_act"], ["chow", "stand"])

    def test_hu_allows_pair_from_triplet(self):
        game = MahjongGame()
        game.init_game()

        player = MahjongPlayer(0, game.np_random)
        player.hand = [
            _make_card("C5"),
            _make_card("C6"),
            _make_card("C7"),
            _make_card("D7"),
            _make_card("D7"),
            _make_card("D7"),
            _make_card("D8"),
            _make_card("D9"),
        ]
        player.pile = [
            [_make_card("B9"), _make_card("B9"), _make_card("B9")],
            [_make_card("B5"), _make_card("B5"), _make_card("B5")],
        ]

        win, _ = game.judger.judge_hu(player)
        self.assertTrue(win)


if __name__ == "__main__":
    unittest.main()
