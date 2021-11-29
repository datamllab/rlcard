'''
    File name: envs/bridge.py
    Author: William Hale
    Date created: 11/26/2021
'''

import numpy as np
from collections import OrderedDict

from rlcard.envs import Env

from rlcard.games.bridge import Game

from rlcard.games.bridge.game import BridgeGame
from rlcard.games.bridge.utils.action_event import ActionEvent
from rlcard.games.bridge.utils.bridge_card import BridgeCard
from rlcard.games.bridge.utils.move import CallMove, PlayCardMove

#   [] Why no_bid_action_id in bidding_rep ?
#       It allows the bidding always to start with North.
#       If North is not the dealer, then he must call 'no_bid'.
#       Until the dealer is reached, 'no_bid' must be the call.
#       I think this might help because it keeps a player's bid in a fixed 'column'.
#       Note: the 'no_bid' is only inserted in the bidding_rep, not in the actual game.
#
#   [] Why current_player_rep ?
#       Explanation here.
#
#   [] Note: hands_rep maintain the hands by N, E, S, W.
#
#   [] Note: trick_rep maintains the trick cards by N, E, S, W.
#      The trick leader can be deduced since play is in clockwise direction.
#
#   [] Note: is_bidding_rep can be deduced from bidding_rep.
#      I think I added is_bidding_rep before bidding_rep and thus it helped in early testing.
#      My early testing had just the player's hand: I think the model conflated the bidding phase with the playing phase in this situation.
#      Although is_bidding_rep is not needed, keeping it may improve learning.
#
#   [] Note: bidding_rep uses the action_id instead of one hot encoding.
#      I think one hot encoding would make the input dimension significantly larger.
#


class BridgeEnv(Env):
    ''' Bridge Environment
    '''
    def __init__(self, config):
        self.name = 'bridge'
        self.game = Game()
        super().__init__(config=config)
        self.bridgePayoffDelegate = DefaultBridgePayoffDelegate()
        self.bridgeStateExtractor = DefaultBridgeStateExtractor()
        state_shape_size = self.bridgeStateExtractor.get_state_shape_size()
        self.state_shape = [[1, state_shape_size] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]

    def get_payoffs(self):
        ''' Get the payoffs of players.

        Returns:
            (list): A list of payoffs for each player.
        '''
        return self.bridgePayoffDelegate.get_payoffs(game=self.game)

    def get_perfect_information(self):
        ''' Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        return self.game.round.get_perfect_information()

    def _extract_state(self, state):  # wch: don't use state 211126
        ''' Extract useful information from state for RL.

        Args:
            state (dict): The raw state

        Returns:
            (numpy.array): The extracted state
        '''
        return self.bridgeStateExtractor.extract_state(game=self.game)

    def _decode_action(self, action_id):
        ''' Decode Action id to the action in the game.

        Args:
            action_id (int): The id of the action

        Returns:
            (ActionEvent): The action that will be passed to the game engine.
        '''
        return ActionEvent.from_action_id(action_id=action_id)

    def _get_legal_actions(self):
        ''' Get all legal actions for current state.

        Returns:
            (list): A list of legal actions' id.
        '''
        raise NotImplementedError  # wch: not needed


class BridgePayoffDelegate(object):

    def get_payoffs(self, game: BridgeGame):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            (list): A list of payoffs for each player.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError


class DefaultBridgePayoffDelegate(BridgePayoffDelegate):

    def __init__(self):
        self.make_bid_bonus = 2

    def get_payoffs(self, game: BridgeGame):
        ''' Get the payoffs of players.

        Returns:
            (list): A list of payoffs for each player.
        '''
        contract_bid_move = game.round.contract_bid_move
        if contract_bid_move:
            declarer = contract_bid_move.player
            bid_trick_count = contract_bid_move.action.bid_amount + 6
            won_trick_counts = game.round.won_trick_counts
            declarer_won_trick_count = won_trick_counts[declarer.player_id % 2]
            defender_won_trick_count = won_trick_counts[(declarer.player_id + 1) % 2]
            declarer_payoff = bid_trick_count + self.make_bid_bonus if bid_trick_count <= declarer_won_trick_count else declarer_won_trick_count - bid_trick_count
            defender_payoff = defender_won_trick_count
            payoffs = []
            for player_id in range(4):
                payoff = declarer_payoff if player_id % 2 == declarer.player_id % 2 else defender_payoff
                payoffs.append(payoff)
        else:
            payoffs = [0, 0, 0, 0]
        return np.array(payoffs)


class BridgeStateExtractor(object):  # interface

    def get_state_shape_size(self) -> int:
        raise NotImplementedError

    def extract_state(self, game: BridgeGame):
        ''' Extract useful information from state for RL. Must be implemented in the child class.

        Args:
            game (BridgeGame): The game

        Returns:
            (numpy.array): The extracted state
        '''
        raise NotImplementedError

    @staticmethod
    def get_legal_actions(game: BridgeGame):
        ''' Get all legal actions for current state.

        Returns:
            (OrderedDict): A OrderedDict of legal actions' id.
        '''
        legal_actions = game.judger.get_legal_actions()
        legal_actions_ids = {action_event.action_id: None for action_event in legal_actions}
        return OrderedDict(legal_actions_ids)


class DefaultBridgeStateExtractor(BridgeStateExtractor):

    def __init__(self):
        super().__init__()
        self.max_bidding_rep_index = 40  # Note: max of 40 calls
        self.last_bid_rep_size = 1 + 35 + 3  # no_bid, bid, pass, dbl, rdbl

    def get_state_shape_size(self) -> int:
        state_shape_size = 0
        state_shape_size += 4 * 52  # hands_rep_size
        state_shape_size += 4 * 52  # trick_rep_size
        state_shape_size += 52  # hidden_cards_rep_size
        state_shape_size += 4  # vul_rep_size
        state_shape_size += 4  # dealer_rep_size
        state_shape_size += 4  # current_player_rep_size
        state_shape_size += 1  # is_bidding_rep_size
        state_shape_size += self.max_bidding_rep_index  # bidding_rep_size
        state_shape_size += self.last_bid_rep_size  # last_bid_rep_size
        state_shape_size += 8  # bid_amount_rep_size
        state_shape_size += 5  # trump_suit_rep_size
        return state_shape_size

    def extract_state(self, game: BridgeGame):
        ''' Extract useful information from state for RL.

        Args:
            game (BridgeGame): The game

        Returns:
            (numpy.array): The extracted state
        '''
        extracted_state = {}
        legal_actions: OrderedDict = self.get_legal_actions(game=game)
        raw_legal_actions = list(legal_actions.keys())
        current_player = game.round.get_current_player()
        current_player_id = current_player.player_id

        # construct hands_rep of hands of players
        hands_rep = [np.zeros(52, dtype=int) for _ in range(4)]
        if not game.is_over():
            for card in game.round.players[current_player_id].hand:
                hands_rep[current_player_id][card.card_id] = 1
            if game.round.is_bidding_over():
                dummy = game.round.get_dummy()
                other_known_player = dummy if dummy.player_id != current_player_id else game.round.get_declarer()
                for card in other_known_player.hand:
                    hands_rep[other_known_player.player_id][card.card_id] = 1

        # construct trick_pile_rep
        trick_pile_rep = [np.zeros(52, dtype=int) for _ in range(4)]
        if game.round.is_bidding_over() and not game.is_over():
            trick_moves = game.round.get_trick_moves()
            for move in trick_moves:
                player = move.player
                card = move.card
                trick_pile_rep[player.player_id][card.card_id] = 1

        # construct hidden_card_rep (during trick taking phase)
        hidden_cards_rep = np.zeros(52, dtype=int)
        if not game.is_over():
            if game.round.is_bidding_over():
                declarer = game.round.get_declarer()
                if current_player_id % 2 == declarer.player_id % 2:
                    hidden_player_ids = [(current_player_id + 1) % 2, (current_player_id + 3) % 2]
                else:
                    hidden_player_ids = [declarer.player_id, (current_player_id + 2) % 2]
                for hidden_player_id in hidden_player_ids:
                    for card in game.round.players[hidden_player_id].hand:
                        hidden_cards_rep[card.card_id] = 1
            else:
                for player in game.round.players:
                    if player.player_id != current_player_id:
                        for card in player.hand:
                            hidden_cards_rep[card.card_id] = 1

        # construct vul_rep
        vul_rep = np.array(game.round.tray.vul, dtype=int)

        # construct dealer_rep
        dealer_rep = np.zeros(4, dtype=int)
        dealer_rep[game.round.tray.dealer_id] = 1

        # construct current_player_rep
        current_player_rep = np.zeros(4, dtype=int)
        current_player_rep[current_player_id] = 1

        # construct is_bidding_rep
        is_bidding_rep = np.array([1] if game.round.is_bidding_over() else [0])

        # construct bidding_rep
        bidding_rep = np.zeros(self.max_bidding_rep_index, dtype=int)
        bidding_rep_index = game.round.dealer_id  # no_bid_action_ids allocated at start so that north always 'starts' the bidding
        for move in game.round.move_sheet:
            if bidding_rep_index >= self.max_bidding_rep_index:
                break
            elif isinstance(move, PlayCardMove):
                break
            elif isinstance(move, CallMove):
                bidding_rep[bidding_rep_index] = move.action.action_id
                bidding_rep_index += 1

        # last_bid_rep
        last_bid_rep = np.zeros(self.last_bid_rep_size, dtype=int)
        last_move = game.round.move_sheet[-1]
        if isinstance(last_move, CallMove):
            last_bid_rep[last_move.action.action_id - ActionEvent.no_bid_action_id] = 1

        # bid_amount_rep and trump_suit_rep
        bid_amount_rep = np.zeros(8, dtype=int)
        trump_suit_rep = np.zeros(5, dtype=int)
        if game.round.is_bidding_over() and not game.is_over() and game.round.play_card_count == 0:
            contract_bid_move = game.round.contract_bid_move
            if contract_bid_move:
                bid_amount_rep[contract_bid_move.action.bid_amount] = 1
                bid_suit = contract_bid_move.action.bid_suit
                bid_suit_index = 4 if not bid_suit else BridgeCard.suits.index(bid_suit)
                trump_suit_rep[bid_suit_index] = 1

        rep = []
        rep += hands_rep
        rep += trick_pile_rep
        rep.append(hidden_cards_rep)
        rep.append(vul_rep)
        rep.append(dealer_rep)
        rep.append(current_player_rep)
        rep.append(is_bidding_rep)
        rep.append(bidding_rep)
        rep.append(last_bid_rep)
        rep.append(bid_amount_rep)
        rep.append(trump_suit_rep)

        obs = np.concatenate(rep)
        extracted_state['obs'] = obs
        extracted_state['legal_actions'] = legal_actions
        extracted_state['raw_legal_actions'] = raw_legal_actions
        extracted_state['raw_obs'] = obs
        return extracted_state
