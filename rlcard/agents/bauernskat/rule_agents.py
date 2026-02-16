'''
    File name: rlcard/games/bauernskat/rule_agents.py
    Author: Oliver Czerwinski
    Date created: 08/12/2025
    Date last modified: 12/25/2025
    Python Version: 3.9+
'''

import random
from collections import Counter
import math
import random

from rlcard.games.bauernskat.action_event import ActionEvent, DeclareTrumpAction, PlayCardAction
from rlcard.games.bauernskat.card import BauernskatCard


def _get_card_strength(card: BauernskatCard, trump_suit: str, led_suit: str) -> int:
    """
    Helper function to calculate the relative strength of a card.
    """
    
    STRENGTH_MAP = {'7': 0, '8': 1, '9': 2, 'Q': 3, 'K': 4, '10': 5, 'A': 6, 'J': 7}

    if trump_suit != 'G':
        if card.rank == 'J':
            jack_strength = {'C': 3, 'S': 2, 'H': 1, 'D': 0}
            return 400 + jack_strength[card.suit]
        if card.suit == trump_suit:
            return 300 + STRENGTH_MAP[card.rank]

    if card.suit == led_suit:
        STRENGTH_MAP_SUIT = {'7': 0, '8': 1, '9': 2, 'J': 3, 'Q': 4, 'K': 5, '10': 6, 'A': 7}
        return 200 + STRENGTH_MAP_SUIT[card.rank]
        
    return 100 + STRENGTH_MAP[card.rank]


def _is_trump(card, ts):
    """
    Helper function to determine if a card is a trump.
    """
    
    if ts == 'G': return False
    return card.rank == 'J' or card.suit == ts


class BauernskatRandomRuleAgent:
    """
    An agent that selects any legal action randomly.
    """
    
    def __init__(self, seed=None):
        """
        Initialized BauernskatRandomRuleAgent.
        """
        
        self.use_raw = False
        self.rng = random.Random(seed)

    def seed(self, seed=None):
        """
        Sets a seed.
        """
        
        self.rng = random.Random(seed)

    def step(self, state):
        """
        Selects a random legal action.
        """
        
        return self.rng.choice(list(state['legal_actions'].keys()))

    def eval_step(self, state):
        """
        Selects a random legal action for evaluation.
        """
        
        action = self.step(state)
        return action, {}


class BauernskatFrugalRuleAgent:
    """
    A simple agent, that plays conservatively to minimize losses.
    """
    
    def __init__(self, seed=None):
        """
        Initialized BauernskatFrugalRuleAgent.
        """
        
        self.use_raw = True
        self.rng = random.Random(seed)

    def seed(self, seed=None):
        """
        Sets a seed.
        """
        
        self.rng = random.Random(seed)

    def step(self, state):
        """
        Selects a legal action with a conservative strategy.
        """
        
        legal_action_ids = list(state['legal_actions'].keys())
        raw_info = state['raw_state_info']
        round_phase = raw_info['round_phase']

        # Simple rule based trump declaration
        if round_phase == 'declare_trump':
            my_cards = raw_info['my_cards']
            num_jacks = sum(1 for card in my_cards if card.rank == 'J')
            if num_jacks >= 3:
                for action_id in legal_action_ids:
                    action = ActionEvent.from_action_id(action_id)
                    if isinstance(action, DeclareTrumpAction) and action.trump_suit == 'G':
                        return action_id
            
            suit_counts = Counter(card.suit for card in my_cards)
            
            if not suit_counts:
                return self.rng.choice(legal_action_ids)
            max_count = max(suit_counts.values())
            best_suits = [suit for suit, count in suit_counts.items() if count == max_count]
            
            if len(best_suits) == 1:
                best_suit_choice = best_suits[0]
            else: 
                best_rank_val = -1
                rank_order = BauernskatCard.ranks
                best_suit_choice = best_suits[0]
                for suit in best_suits:
                    cards_of_suit = [card for card in my_cards if card.suit == suit]
                    max_rank_in_suit = max(rank_order.index(c.rank) for c in cards_of_suit)
                    if max_rank_in_suit > best_rank_val:
                        best_rank_val = max_rank_in_suit
                        best_suit_choice = suit
            
            for action_id in legal_action_ids:
                action = ActionEvent.from_action_id(action_id)
                if isinstance(action, DeclareTrumpAction) and action.trump_suit == best_suit_choice:
                    return action_id
            
            return self.rng.choice(legal_action_ids)

        # Only play good cards if necessary or really worth it
        if round_phase == 'play':
            trick_moves = raw_info['trick_moves']
            trump_suit = raw_info['trump_suit']
            legal_play_actions = [a for a in (ActionEvent.from_action_id(aid) for aid in legal_action_ids) if isinstance(a, PlayCardAction)]

            if not trick_moves:
                min_points = min(action.card.points for action in legal_play_actions)
                min_point_actions = [action for action in legal_play_actions if action.card.points == min_points]
                
                non_trump_options = [action for action in min_point_actions if not _is_trump(action.card, trump_suit)]
                if non_trump_options:
                    return non_trump_options[0].action_id
                else:
                    return min_point_actions[0].action_id

            else:
                led_card = trick_moves[0][1]
                led_suit = led_card.suit
                led_card_strength = _get_card_strength(led_card, trump_suit, led_suit)
                
                winning_moves = [action for action in legal_play_actions if _get_card_strength(action.card, trump_suit, led_suit) > led_card_strength]
                losing_moves = [action for action in legal_play_actions if action not in winning_moves]

                should_win = False
                
                if winning_moves:
                    weakest_winning_move = min(winning_moves, key=lambda a: _get_card_strength(a.card, trump_suit, led_suit))
                    potential_trick_value = led_card.points + weakest_winning_move.card.points
                    
                    if potential_trick_value >= 10:
                        should_win = True

                if should_win:
                    return min(winning_moves, key=lambda a: _get_card_strength(a.card, trump_suit, led_suit)).action_id
                else:
                    if losing_moves:
                        return min(losing_moves, key=lambda a: a.card.points).action_id
                    else:
                        return min(winning_moves, key=lambda a: _get_card_strength(a.card, trump_suit, led_suit)).action_id

        return self.rng.choice(legal_action_ids)

    def eval_step(self, state):
        """
        Selects a legal action for evaluation.
        """
        
        action = self.step(state)
        return action, {}


class BauernskatLookaheadRuleAgent:
    """
    An agent simulating the outcome of each legal move aswell as the opponents likely response.
    """
    
    def __init__(self, seed=None):
        """
        Initialized BauernskatLookaheadRuleAgent.
        """
        
        self.use_raw = True
        self.rng = random.Random(seed)

    def seed(self, seed=None):
        """
        Sets a seed.
        """
        
        self.rng = random.Random(seed)

    def step(self, state):
        """
        Selects a legal action using lookahead simulations.
        """
        
        legal_action_ids = list(state['legal_actions'].keys())
        raw_info = state['raw_state_info']
        round_phase = raw_info['round_phase']

        # Simple rule based trump declaration
        if round_phase == 'declare_trump':
            my_cards = raw_info['my_cards']
            num_jacks = sum(1 for card in my_cards if card.rank == 'J')
            
            if num_jacks >= 2:
                for action_id in legal_action_ids:
                    action = ActionEvent.from_action_id(action_id)
                    if isinstance(action, DeclareTrumpAction) and action.trump_suit == 'G':
                        return action_id
            
            suit_counts = Counter(card.suit for card in my_cards)
            if not suit_counts: return self.rng.choice(legal_action_ids)

            max_count = max(suit_counts.values())
            best_suits = [suit for suit, count in suit_counts.items() if count == max_count]

            if len(best_suits) == 1:
                best_suit_choice = best_suits[0]
            else:
                best_rank_val = -1
                rank_order = BauernskatCard.ranks
                best_suit_choice = best_suits[0]
                for suit in best_suits:
                    cards_of_suit = [card for card in my_cards if card.suit == suit]
                    max_rank_in_suit = max(rank_order.index(c.rank) for c in cards_of_suit)
                    if max_rank_in_suit > best_rank_val:
                        best_rank_val = max_rank_in_suit
                        best_suit_choice = suit
            
            for action_id in legal_action_ids:
                action = ActionEvent.from_action_id(action_id)
                if isinstance(action, DeclareTrumpAction) and action.trump_suit == best_suit_choice:
                    return action_id
            
            return self.rng.choice(legal_action_ids)

        # Go through all legal moves and simulate opponent response to determine the best action
        if round_phase == 'play':
            legal_play_actions = [a for a in (ActionEvent.from_action_id(aid) for aid in legal_action_ids) if isinstance(a, PlayCardAction)]

            if len(legal_play_actions) == 1:
                return legal_play_actions[0].action_id

            best_move = None
            best_score = float('-inf')

            trick_moves = raw_info['trick_moves']

            for action in legal_play_actions:
                if not trick_moves:
                    # If starting a trick
                    score = self._score_leading_move(action, raw_info)
                else:
                    # If answering a trick
                    score = self._score_following_move(action, raw_info)
                
                if score > best_score:
                    best_score = score
                    best_move = action
            
            return best_move.action_id if best_move else self.rng.choice(legal_action_ids)

        return self.rng.choice(legal_action_ids)

    def _score_leading_move(self, action: PlayCardAction, raw_info: dict) -> float:
        """
        Rates card actions according to simulated opponent response.
        """
        
        my_card = action.card
        trump_suit = raw_info['trump_suit']
        opponent_visible_cards = raw_info['opponent_visible_cards']
        
        # Simulation of response
        led_suit = my_card.suit
        is_led_trump = _is_trump(my_card, trump_suit)
        
        legal_replies = []
        if is_led_trump:
            trumps_in_hand = [c for c in opponent_visible_cards if _is_trump(c, trump_suit)]
            legal_replies = trumps_in_hand if trumps_in_hand else opponent_visible_cards
        else:
            suit_in_hand = [c for c in opponent_visible_cards if c.suit == led_suit and not _is_trump(c, trump_suit)]
            legal_replies = suit_in_hand if suit_in_hand else opponent_visible_cards
        
        my_strength = _get_card_strength(my_card, trump_suit, led_suit)

        if not legal_replies:
            return my_card.points - (1 if my_card.points >= 10 else 0)

        winning_replies = [c for c in legal_replies if _get_card_strength(c, trump_suit, led_suit) > my_strength]
        losing_replies = [c for c in legal_replies if c not in winning_replies]

        # Outcome evaluation
        if winning_replies:
            # Bad if opponent can win
            weakest_winner = min(winning_replies, key=lambda c: _get_card_strength(c, trump_suit, led_suit))
            points_lost = my_card.points + weakest_winner.points
            return -points_lost
        else:
            # Good if opponent cannot win
            most_frugal_discard = min(losing_replies, key=lambda c: c.points)
            points_gained = my_card.points + most_frugal_discard.points
            
            # Bonus for making the opponent use a trump
            if _is_trump(most_frugal_discard, trump_suit):
                points_gained += 1
                
            return points_gained

    def _score_following_move(self, action: PlayCardAction, raw_info: dict) -> float:
        """
        Rates card actions when answering a card in the trick.
        """
        
        my_card = action.card
        trump_suit = raw_info['trump_suit']
        led_card = raw_info['trick_moves'][0][1]
        led_suit = led_card.suit

        my_strength = _get_card_strength(my_card, trump_suit, led_suit)
        led_strength = _get_card_strength(led_card, trump_suit, led_suit)

        if my_strength > led_strength:
            reward = led_card.points + my_card.points
            
            # Small cost for using a strong card
            cost = my_strength / 50.0 
            
            # Bonus for winning tricks with high pips
            if reward >= 10:
                reward *= 1.5

            return reward - cost
        else:
            # Lost the trick
            points_lost = led_card.points + my_card.points
            
            # Bonus for using low pips cards
            discard_bonus = (11 - my_card.points) / 10.0

            return -points_lost + discard_bonus

    def eval_step(self, state):
        """
        Selects a legal action for evaluation.
        """
        
        action = self.step(state)
        return action, {}


class BauernskatSHOTAlphaBetaRuleAgent:
    """
    A hybrid agent combining Simple Heuristic Search (SHOT), Alpha-Beta search, and PIMC for Bauernskat.
    """
    
    def __init__(self, num_simulations=16, alpha_beta_depth=2, use_shot=True, use_move_ordering=True, use_alpha_beta=True, seed=None):
        """
        Initialized BauernskatSHOTAlphaBetaRuleAgent.
        """
        
        self.use_raw = True
        self.rng = random.Random(seed)
        
        self.num_simulations = num_simulations
        self.alpha_beta_depth = alpha_beta_depth
        
        self.use_shot = use_shot
        self.use_move_ordering = use_move_ordering
        self.use_alpha_beta = use_alpha_beta
        
        self.card_strength_cache = {}
        
        try:
            deck = BauernskatCard.get_deck()
        except NameError:
            deck = []
            
        for trump in ['G', 'C', 'S', 'H', 'D']:
            for led in ['C', 'S', 'H', 'D']:
                for card in deck:
                    self.card_strength_cache[(card, trump, led)] = _get_card_strength(card, trump, led)

    def seed(self, seed=None):
        """
        Sets a seed.
        """
        
        self.rng = random.Random(seed)

    def _cached_get_card_strength(self, card, trump_suit, led_suit):
        """
        Retrieves cached card strength.
        """
        
        key = (card, trump_suit, led_suit)
        return self.card_strength_cache[key]

    def _shallow_copy_state(self, state_info):
        """
        Manual state copy to avoid overhead.
        """
        
        new_state = {
            'player_id': state_info['player_id'],
            'my_score': state_info['my_score'],
            'opponent_score': state_info['opponent_score'],
            'my_cards': list(state_info['my_cards']),
            'opponent_visible_cards': list(state_info['opponent_visible_cards']),
            'played_cards': set(state_info['played_cards']),
            'trick_moves': list(state_info['trick_moves']),
            'trump_suit': state_info['trump_suit'],
            'round_phase': state_info['round_phase']
        }
        
        return new_state

    def step(self, state):
        """
        Selects a legal action using SHOT and Alpha-Beta search with move ordering.
        """
        
        legal_action_ids = list(state['legal_actions'].keys())
        raw_info = state['raw_state_info']
        round_phase = raw_info['round_phase']

        # Simple rule based trump declaration
        if round_phase == 'declare_trump':
            my_cards = raw_info['my_cards']
            num_jacks = sum(1 for card in my_cards if card.rank == 'J')
            
            if num_jacks >= 2:
                for action_id in legal_action_ids:
                    action = ActionEvent.from_action_id(action_id)
                    if isinstance(action, DeclareTrumpAction) and action.trump_suit == 'G':
                        return action_id
            
            suit_counts = Counter(card.suit for card in my_cards)
            if not suit_counts: return self.rng.choice(legal_action_ids)

            max_count = max(suit_counts.values())
            best_suits = [suit for suit, count in suit_counts.items() if count == max_count]

            if len(best_suits) == 1:
                best_suit_choice = best_suits[0]
            else:
                best_rank_val = -1
                rank_order = BauernskatCard.ranks
                best_suit_choice = best_suits[0]
                for suit in best_suits:
                    cards_of_suit = [card for card in my_cards if card.suit == suit]
                    max_rank_in_suit = max(rank_order.index(c.rank) for c in cards_of_suit)
                    if max_rank_in_suit > best_rank_val:
                        best_rank_val = max_rank_in_suit
                        best_suit_choice = suit
            
            for action_id in legal_action_ids:
                action = ActionEvent.from_action_id(action_id)
                if isinstance(action, DeclareTrumpAction) and action.trump_suit == best_suit_choice:
                    return action_id
            
            return self.rng.choice(legal_action_ids)

        # Play with SHOT and Alpha-Beta search
        if round_phase == 'play':
            legal_actions = [ActionEvent.from_action_id(aid) for aid in legal_action_ids if isinstance(ActionEvent.from_action_id(aid), PlayCardAction)]
            if not legal_actions: return self.rng.choice(legal_action_ids)
            if len(legal_actions) == 1: return legal_actions[0].action_id

            # Using SHOT for filtering actions
            if self.use_shot:
                candidate_actions = list(legal_actions)
                num_rounds = math.ceil(math.log2(len(candidate_actions)))
                sims_per_round = self.num_simulations // num_rounds if num_rounds > 0 else self.num_simulations
                
                for _ in range(num_rounds):
                    if len(candidate_actions) == 1: break
                    sims_per_candidate = max(1, sims_per_round // len(candidate_actions))
                    scores = {action.action_id: 0 for action in candidate_actions}
                    
                    for action in candidate_actions:
                        post_move_state = self._shallow_copy_state(raw_info)
                        card_to_play = action.card
                        post_move_state['my_cards'].remove(card_to_play)
                        post_move_state['trick_moves'].append((post_move_state['player_id'], card_to_play))
                        
                        if len(post_move_state['trick_moves']) == 2:
                            self._resolve_trick(post_move_state, original_player_id=raw_info['player_id'])
                        else:
                            post_move_state['player_id'] = 1 - post_move_state['player_id']

                        opponent_hand = self._determinize(post_move_state)
                        
                        for _ in range(sims_per_candidate):
                            sim_state = self._shallow_copy_state(post_move_state)
                            my_hand = list(sim_state['my_cards'])
                            if self.use_alpha_beta:
                                score = self._run_alpha_beta(
                                    state_info=sim_state,
                                    p0_hand=my_hand,
                                    p1_hand=opponent_hand,
                                    depth=self.alpha_beta_depth,
                                    alpha=-999999,
                                    beta=999999,
                                    is_maximizing=(sim_state['player_id'] == raw_info['player_id']),
                                    original_player_id=raw_info['player_id']
                                )
                            else:
                                score = self._run_heuristic_playout(sim_state, my_hand, opponent_hand, raw_info['player_id'])
                            scores[action.action_id] += score
                    
                    sorted_actions = sorted(candidate_actions, key=lambda a: scores[a.action_id], reverse=True)
                    num_to_keep = math.ceil(len(sorted_actions) / 2)
                    candidate_actions = sorted_actions[:num_to_keep]
                
                return candidate_actions[0].action_id if candidate_actions else self.rng.choice(legal_action_ids)
            
            else:
                # PIMC
                best_action = None
                best_avg_score = float('-inf')
                
                for action in legal_actions:
                    post_move_state = self._shallow_copy_state(raw_info)
                    card_to_play = action.card
                    post_move_state['my_cards'].remove(card_to_play)
                    post_move_state['trick_moves'].append((post_move_state['player_id'], card_to_play))
                    
                    if len(post_move_state['trick_moves']) == 2:
                        self._resolve_trick(post_move_state, original_player_id=raw_info['player_id'])
                    else:
                        post_move_state['player_id'] = 1 - post_move_state['player_id']

                    opponent_hand = self._determinize(post_move_state)
                    
                    total_score = 0
                    
                    for _ in range(self.num_simulations):
                        sim_state = self._shallow_copy_state(post_move_state)
                        my_hand = list(sim_state['my_cards'])
                        if self.use_alpha_beta:
                            score = self._run_alpha_beta(
                                state_info=sim_state,
                                p0_hand=my_hand,
                                p1_hand=opponent_hand,
                                depth=self.alpha_beta_depth,
                                alpha=-999999,
                                beta=999999,
                                is_maximizing=(sim_state['player_id'] == raw_info['player_id']),
                                original_player_id=raw_info['player_id']
                            )
                        else:
                            score = self._run_heuristic_playout(sim_state, my_hand, opponent_hand, raw_info['player_id'])
                        total_score += score
                    
                    avg_score = total_score / self.num_simulations
                    if avg_score > best_avg_score:
                        best_avg_score = avg_score
                        best_action = action
                
                return best_action.action_id if best_action else self.rng.choice(legal_action_ids)
        
        return self.rng.choice(legal_action_ids)

    def _determinize(self, state_info):
        """
        Creates a state for the opponent by using publicly known information.
        """
        
        all_cards = set(BauernskatCard.get_deck())
        
        # Rule out cards that are not in the opponents closed cards
        opponent_visible = set(state_info['opponent_visible_cards'])
        played = set(state_info['played_cards'])
        in_trick = {c for _, c in state_info['trick_moves']}
        my_hand = set(state_info['my_cards'])

        publicly_known_cards = opponent_visible | played | in_trick | my_hand
        
        unknown_cards_pool = list(all_cards - publicly_known_cards)
        self.rng.shuffle(unknown_cards_pool)

        num_opponent_hidden = 16 - len(state_info['opponent_visible_cards'])
        
        num_to_draw = min(num_opponent_hidden, len(unknown_cards_pool))
        
        opponent_hidden_cards = unknown_cards_pool[:num_to_draw]
        
        return state_info['opponent_visible_cards'] + opponent_hidden_cards

    def _run_heuristic_playout(self, state_info, p0_hand, p1_hand, original_player_id):
        """
        Runs a heuristic simulation.
        """
        
        playout_state = self._shallow_copy_state(state_info)
        p0_h = set(p0_hand)
        p1_h = set(p1_hand)
        
        num_played = len(playout_state['played_cards'])
        tricks_to_play = (32 - num_played - len(playout_state['trick_moves'])) // 2

        if len(playout_state['trick_moves']) == 1:
            current_hand = p1_h if playout_state['player_id'] == (1 - original_player_id) else p0_h
            legal_moves = self._get_legal_in_playout(current_hand, playout_state['trick_moves'], playout_state['trump_suit'])
            if legal_moves:
                move = max(legal_moves, key=lambda c: c.points)
                current_hand.remove(move)
                playout_state['trick_moves'].append((playout_state['player_id'], move))
                self._resolve_trick(playout_state, original_player_id)
        
        for _ in range(tricks_to_play):
            leader_hand = p0_h if playout_state['player_id'] == original_player_id else p1_h
            follower_hand = p1_h if playout_state['player_id'] == original_player_id else p0_h

            leader_legal = self._get_legal_in_playout(leader_hand, [], playout_state['trump_suit'])
            if not leader_legal: break
            leader_move = max(leader_legal, key=lambda c: c.points)
            leader_hand.remove(leader_move)
            playout_state['trick_moves'].append((playout_state['player_id'], leader_move))

            follower_legal = self._get_legal_in_playout(follower_hand, playout_state['trick_moves'], playout_state['trump_suit'])
            if not follower_legal: break
            follower_move = max(follower_legal, key=lambda c: c.points)
            follower_hand.remove(follower_move)
            playout_state['trick_moves'].append((1 - playout_state['player_id'], follower_move))

            self._resolve_trick(playout_state, original_player_id)

        return playout_state['my_score'] - playout_state['opponent_score']

    def _run_alpha_beta(self, state_info, p0_hand, p1_hand, depth, alpha, beta, is_maximizing, original_player_id):
        """
        Runs the alpha-beta pruning on the given state.
        """
        
        if depth == 0 or (len(p0_hand) == 0 and len(p1_hand) == 0 and not state_info['trick_moves']):
            return self._evaluate_state(state_info, p0_hand, p1_hand, original_player_id)

        current_player_id = state_info['player_id']
        current_hand = p0_hand if current_player_id == original_player_id else p1_hand
        legal_moves = self._get_legal_in_playout(current_hand, state_info['trick_moves'], state_info['trump_suit'])
        if not legal_moves:
            return self._evaluate_state(state_info, p0_hand, p1_hand, original_player_id)

        trump_suit = state_info['trump_suit']
        non_trump_hand = [c for c in current_hand if not _is_trump(c, trump_suit)]
        suit_counts = Counter(c.suit for c in non_trump_hand)
        if self.use_move_ordering:
            sorted_moves = sorted(legal_moves, key=lambda card: self._advanced_heuristic_move_score(card, current_hand, state_info, suit_counts), reverse=True)
        else:
            sorted_moves = legal_moves

        if is_maximizing:
            max_eval = -999999
            for card in sorted_moves:
                child_state = self._get_next_state(state_info, p0_hand, p1_hand, card, current_player_id, original_player_id)
                eval_score = self._run_alpha_beta(child_state['state'], child_state['p0_hand'], child_state['p1_hand'], depth - 1, alpha, beta, not is_maximizing, original_player_id)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = 999999
            for card in sorted_moves:
                child_state = self._get_next_state(state_info, p0_hand, p1_hand, card, current_player_id, original_player_id)
                eval_score = self._run_alpha_beta(child_state['state'], child_state['p0_hand'], child_state['p1_hand'], depth - 1, alpha, beta, not is_maximizing, original_player_id)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha: break
            return min_eval

    def _advanced_heuristic_move_score(self, card, hand, state_info, suit_counts=None):
        """
        Create a score for move ordering in alpha-beta search.
        """
        
        trump_suit = state_info['trump_suit']
        is_creating_void = False
        if not _is_trump(card, trump_suit):
            if suit_counts is None:
                count_in_suit = sum(1 for c in hand if c.suit == card.suit and not _is_trump(c, trump_suit))
            else:
                count_in_suit = suit_counts.get(card.suit, 0)
            if count_in_suit == 1: is_creating_void = True
        
        if state_info['trick_moves']:
            led_card = state_info['trick_moves'][0][1]
            led_suit = led_card.suit
            led_strength = self._cached_get_card_strength(led_card, trump_suit, led_suit)
            my_strength = self._cached_get_card_strength(card, trump_suit, led_suit)
            
            if my_strength > led_strength:
                trick_points = led_card.points + card.points
                if trick_points >= 10: return 500 + trick_points
                else: return 400 - my_strength
            else:
                score = 200 + (11 - card.points)
                if is_creating_void: score += 100
                return score
        else:
            if card.rank == 'J' and trump_suit != 'G': return 600 + self._cached_get_card_strength(card, trump_suit, card.suit)
            if card.suit == trump_suit and trump_suit != 'G': return 500 + self._cached_get_card_strength(card, trump_suit, card.suit)
            if card.points >= 10: return 400 + card.points
            score = 200 - card.points
            if is_creating_void: score += 100
            return score

    def _evaluate_state(self, state_info, p0_hand, p1_hand, original_player_id):
        """
        Evaluate the current game state.
        """
        
        score_diff = state_info['my_score'] - state_info['opponent_score']
        p0_hand_value = sum(c.points for c in p0_hand)
        p1_hand_value = sum(c.points for c in p1_hand)
        hand_diff = p0_hand_value - p1_hand_value
        if state_info['player_id'] == original_player_id:
            score_diff += hand_diff // 10
        else:
            score_diff -= hand_diff // 10
        return score_diff

    def _get_next_state(self, state_info, p0_hand, p1_hand, played_card, player_id, original_player_id):
        """
        Gives the next state after a card is played.
        """
        
        next_state = self._shallow_copy_state(state_info)
        p0_h = list(p0_hand)
        p1_h = list(p1_hand)
        if player_id == original_player_id: 
            if played_card in p0_h: p0_h.remove(played_card)
        else: 
            if played_card in p1_h: p1_h.remove(played_card)
        next_state['trick_moves'].append((player_id, played_card))
        if len(next_state['trick_moves']) == 2:
            self._resolve_trick(next_state, original_player_id)
        else:
            next_state['player_id'] = 1 - player_id
        return {'state': next_state, 'p0_hand': p0_h, 'p1_hand': p1_h}

    def _resolve_trick(self, state_info, original_player_id):
        """
        Resolves a trick and updates the game state.
        """
        
        p0_move = state_info['trick_moves'][0]
        p1_move = state_info['trick_moves'][1]
        led_suit = p0_move[1].suit
        p0_strength = self._cached_get_card_strength(p0_move[1], state_info['trump_suit'], led_suit)
        p1_strength = self._cached_get_card_strength(p1_move[1], state_info['trump_suit'], led_suit)
        winner_id = p0_move[0] if p0_strength > p1_strength else p1_move[0]
        trick_points = p0_move[1].points + p1_move[1].points
        if winner_id == original_player_id:
            state_info['my_score'] += trick_points
        else:
            state_info['opponent_score'] += trick_points
        state_info['played_cards'].add(p0_move[1])
        state_info['played_cards'].add(p1_move[1])
        state_info['trick_moves'] = []
        state_info['player_id'] = winner_id

    def _get_legal_in_playout(self, hand, trick_moves, trump_suit):
        """
        Returns the legal cards in a simulation.
        """
        
        if not hand: return []
        if not trick_moves: return list(hand)
        led_card = trick_moves[0][1]
        trumps_in_hand = {card for card in hand if _is_trump(card, trump_suit)}
        if _is_trump(led_card, trump_suit):
            if trumps_in_hand: return list(trumps_in_hand)
        else:
            led_suit = led_card.suit
            suit_in_hand = {card for card in hand if card.suit == led_suit and not _is_trump(card, trump_suit)}
            if suit_in_hand: return list(suit_in_hand)
        return list(hand)

    def eval_step(self, state):
        """
        Selects a legal action for evaluation.
        """
        
        action = self.step(state)
        return action, {}