'''
    File name: gin_rummy/round.py
    Author: William Hale
    Date created: 2/12/2020
'''
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .utils.move import GinRummyMove

from typing import List

from rlcard.games.gin_rummy.dealer import GinRummyDealer

from .utils.action_event import DrawCardAction, PickUpDiscardAction, DeclareDeadHandAction
from .utils.action_event import DiscardAction, KnockAction, GinAction
from .utils.action_event import ScoreNorthPlayerAction, ScoreSouthPlayerAction

from .utils.move import DealHandMove
from .utils.move import DrawCardMove, PickupDiscardMove, DeclareDeadHandMove
from .utils.move import DiscardMove, KnockMove, GinMove
from .utils.move import ScoreNorthMove, ScoreSouthMove

from .utils.gin_rummy_error import GinRummyProgramError

from .player import GinRummyPlayer
from . import judge

from rlcard.games.gin_rummy.utils import melding
from rlcard.games.gin_rummy.utils import utils


class GinRummyRound:

    def __init__(self, dealer_id: int, np_random):
        ''' Initialize the round class

            The round class maintains the following instances:
                1) dealer: the dealer of the round; dealer has stock_pile and discard_pile
                2) players: the players in the round; each player has his own hand_pile
                3) current_player_id: the id of the current player who has the move
                4) is_over: true if the round is over
                5) going_out_action: knock or gin or None
                6) going_out_player_id: id of player who went out or None
                7) move_sheet: history of the moves of the player (including the deal_hand_move)

            The round class maintains a list of moves made by the players in self.move_sheet.
            move_sheet is similar to a chess score sheet.
            I didn't want to call it a score_sheet since it is not keeping score.
            I could have called move_sheet just moves, but that might conflict with the name moves used elsewhere.
            I settled on the longer name "move_sheet" to indicate that it is the official list of moves being made.

        Args:
            dealer_id: int
        '''
        self.np_random = np_random
        self.dealer_id = dealer_id
        self.dealer = GinRummyDealer(self.np_random)
        self.players = [GinRummyPlayer(player_id=0, np_random=self.np_random), GinRummyPlayer(player_id=1, np_random=self.np_random)]
        self.current_player_id = (dealer_id + 1) % 2
        self.is_over = False
        self.going_out_action = None  # going_out_action: int or None
        self.going_out_player_id = None  # going_out_player_id: int or None
        self.move_sheet = []  # type: List[GinRummyMove]
        player_dealing = GinRummyPlayer(player_id=dealer_id, np_random=self.np_random)
        shuffled_deck = self.dealer.shuffled_deck
        self.move_sheet.append(DealHandMove(player_dealing=player_dealing, shuffled_deck=shuffled_deck))

    def get_current_player(self) -> GinRummyPlayer or None:
        current_player_id = self.current_player_id
        return None if current_player_id is None else self.players[current_player_id]

    def draw_card(self, action: DrawCardAction):
        # when current_player takes DrawCardAction step, the move is recorded and executed
        # current_player keeps turn
        current_player = self.players[self.current_player_id]
        if not len(current_player.hand) == 10:
            raise GinRummyProgramError("len(current_player.hand) is {}: should be 10.".format(len(current_player.hand)))
        card = self.dealer.stock_pile.pop()
        self.move_sheet.append(DrawCardMove(current_player, action=action, card=card))
        current_player.add_card_to_hand(card=card)

    def pick_up_discard(self, action: PickUpDiscardAction):
        # when current_player takes PickUpDiscardAction step, the move is recorded and executed
        # opponent knows that the card is in current_player hand
        # current_player keeps turn
        current_player = self.players[self.current_player_id]
        if not len(current_player.hand) == 10:
            raise GinRummyProgramError("len(current_player.hand) is {}: should be 10.".format(len(current_player.hand)))
        card = self.dealer.discard_pile.pop()
        self.move_sheet.append(PickupDiscardMove(current_player, action, card=card))
        current_player.add_card_to_hand(card=card)
        current_player.known_cards.append(card)

    def declare_dead_hand(self, action: DeclareDeadHandAction):
        # when current_player takes DeclareDeadHandAction step, the move is recorded and executed
        # north becomes current_player to score his hand
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(DeclareDeadHandMove(current_player, action))
        self.going_out_action = action
        self.going_out_player_id = self.current_player_id
        if not len(current_player.hand) == 10:
            raise GinRummyProgramError("len(current_player.hand) is {}: should be 10.".format(len(current_player.hand)))
        self.current_player_id = 0

    def discard(self, action: DiscardAction):
        # when current_player takes DiscardAction step, the move is recorded and executed
        # opponent knows that the card is no longer in current_player hand
        # current_player loses his turn and the opponent becomes the current player
        current_player = self.players[self.current_player_id]
        if not len(current_player.hand) == 11:
            raise GinRummyProgramError("len(current_player.hand) is {}: should be 11.".format(len(current_player.hand)))
        self.move_sheet.append(DiscardMove(current_player, action))
        card = action.card
        current_player.remove_card_from_hand(card=card)
        if card in current_player.known_cards:
            current_player.known_cards.remove(card)
        self.dealer.discard_pile.append(card)
        self.current_player_id = (self.current_player_id + 1) % 2

    def knock(self, action: KnockAction):
        # when current_player takes KnockAction step, the move is recorded and executed
        # opponent knows that the card is no longer in current_player hand
        # north becomes current_player to score his hand
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(KnockMove(current_player, action))
        self.going_out_action = action
        self.going_out_player_id = self.current_player_id
        if not len(current_player.hand) == 11:
            raise GinRummyProgramError("len(current_player.hand) is {}: should be 11.".format(len(current_player.hand)))
        card = action.card
        current_player.remove_card_from_hand(card=card)
        if card in current_player.known_cards:
            current_player.known_cards.remove(card)
        self.current_player_id = 0

    def gin(self, action: GinAction, going_out_deadwood_count: int):
        # when current_player takes GinAction step, the move is recorded and executed
        # opponent knows that the card is no longer in current_player hand
        # north becomes current_player to score his hand
        current_player = self.players[self.current_player_id]
        self.move_sheet.append(GinMove(current_player, action))
        self.going_out_action = action
        self.going_out_player_id = self.current_player_id
        if not len(current_player.hand) == 11:
            raise GinRummyProgramError("len(current_player.hand) is {}: should be 11.".format(len(current_player.hand)))
        _, gin_cards = judge.get_going_out_cards(current_player.hand, going_out_deadwood_count)
        card = gin_cards[0]
        current_player.remove_card_from_hand(card=card)
        if card in current_player.known_cards:
            current_player.known_cards.remove(card)
        self.current_player_id = 0

    def score_player_0(self, action: ScoreNorthPlayerAction):
        # when current_player takes ScoreNorthPlayerAction step, the move is recorded and executed
        # south becomes current player
        if not self.current_player_id == 0:
            raise GinRummyProgramError("current_player_id is {}: should be 0.".format(self.current_player_id))
        current_player = self.get_current_player()
        best_meld_clusters = melding.get_best_meld_clusters(hand=current_player.hand)
        best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
        deadwood_count = utils.get_deadwood_count(hand=current_player.hand, meld_cluster=best_meld_cluster)
        self.move_sheet.append(ScoreNorthMove(player=current_player,
                                              action=action,
                                              best_meld_cluster=best_meld_cluster,
                                              deadwood_count=deadwood_count))
        self.current_player_id = 1

    def score_player_1(self, action: ScoreSouthPlayerAction):
        # when current_player takes ScoreSouthPlayerAction step, the move is recorded and executed
        # south remains current player
        # the round is over
        if not self.current_player_id == 1:
            raise GinRummyProgramError("current_player_id is {}: should be 1.".format(self.current_player_id))
        current_player = self.get_current_player()
        best_meld_clusters = melding.get_best_meld_clusters(hand=current_player.hand)
        best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
        deadwood_count = utils.get_deadwood_count(hand=current_player.hand, meld_cluster=best_meld_cluster)
        self.move_sheet.append(ScoreSouthMove(player=current_player,
                                              action=action,
                                              best_meld_cluster=best_meld_cluster,
                                              deadwood_count=deadwood_count))
        self.is_over = True
