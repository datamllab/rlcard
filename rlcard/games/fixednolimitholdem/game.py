from enum import Enum
import numpy as np
from copy import deepcopy
from rlcard.games.limitholdem import Game
from rlcard.games.limitholdem import PlayerStatus

from rlcard.games.fixednolimitholdem import Dealer
from rlcard.games.fixednolimitholdem import Player
from rlcard.games.fixednolimitholdem import Judger
from rlcard.games.fixednolimitholdem import Round, Action


class Stage(Enum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    END_HIDDEN = 4
    SHOWDOWN = 5
    WAITING_FOR_FLOP = 6  # Waiting for flop cards
    WAITING_FOR_TURN = 7  # Waiting for turn card
    WAITING_FOR_RIVER = 8  # Waiting for river card


class NolimitholdemGame(Game):
    def __init__(self, allow_step_back=False, num_players=2):
        """Initialize the class no limit holdem Game"""
        super().__init__(allow_step_back, num_players)

        self.np_random = np.random.RandomState()

        # small blind and big blind
        self.small_blind = 1
        self.big_blind = 2 * self.small_blind

        # config players
        self.init_chips = [self.big_blind * 100] * num_players

        # If None, the dealer will be randomly chosen
        self.dealer_id = None
        
        # For manually setting cards
        self.player0_hand = []
        self.manual_dealer = False  # Default to automatic dealing

    def configure(self, game_config):
        """
        Specify some game specific parameters, such as number of players, initial chips, and dealer id.
        If dealer_id is None, he will be randomly chosen
        """
        self.num_players = game_config['game_num_players']
        # must have num_players length
        self.init_chips = [game_config['chips_for_each']] * game_config["game_num_players"]
        self.dealer_id = game_config['dealer_id']
        
        # Check for manual dealer flag
        self.manual_dealer = game_config.get('manual_dealer', False)
        
        # Set player0 hand if provided and manual dealer is enabled
        if self.manual_dealer and 'player0_hand' in game_config:
            self.player0_hand = game_config['player0_hand']

    def init_game(self):
        """
        Initialize the game of not limit holdem

        This version supports two-player no limit texas holdem

        Returns:
            (tuple): Tuple containing:

                (dict): The first state of the game
                (int): Current player's id
        """
        if self.dealer_id is None:
            self.dealer_id = self.np_random.randint(0, self.num_players)
        else:
            self.dealer_id = (self.dealer_id + 1) % self.num_players
            
        # Initialize a dealer that can deal cards
        self.dealer = Dealer(self.np_random)
        
        # Enable manual mode if configured
        if self.manual_dealer:
            if hasattr(self.dealer, 'enable_manual_mode'):
                self.dealer.enable_manual_mode()
            
            # Set preset cards for Player 0's hand if provided
            if self.player0_hand and hasattr(self.dealer, 'set_player0_hand'):
                self.dealer.set_player0_hand(self.player0_hand)

        # Initialize players to play the game
        self.players = [Player(i, self.init_chips[i], self.np_random) for i in range(self.num_players)]

        # Initialize a judger class which will decide who wins in the end
        self.judger = Judger(self.np_random)

        # Deal cards to each player to prepare for the first round
        for i in range(self.num_players):
            for _ in range(2):  # Each player gets 2 cards
                # Pass player_id to deal_card if the dealer supports it
                if hasattr(self.dealer, 'deal_card') and 'player_id' in self.dealer.deal_card.__code__.co_varnames:
                    card = self.dealer.deal_card(player_id=i)
                else:
                    card = self.dealer.deal_card()
                self.players[i].hand.append(card)

        # Initialize public cards
        self.public_cards = []
        self.stage = Stage.PREFLOP

        # Big blind and small blind
        if self.num_players == 2:
            # In heads-up dealer posts small blind
            s = (self.dealer_id) % self.num_players
            b = (self.dealer_id + 1) % self.num_players
        else: 
            s = (self.dealer_id + 1) % self.num_players
            b = (self.dealer_id + 2) % self.num_players

        self.players[b].bet(chips=self.big_blind)
        self.players[s].bet(chips=self.small_blind)            

        # The player next to the big blind plays the first
        self.game_pointer = (b + 1) % self.num_players

        # Initialize a bidding round, in the first round, the big blind and the small blind needs to
        # be passed to the round for processing.
        self.round = Round(self.num_players, self.big_blind, dealer=self.dealer, np_random=self.np_random)

        self.round.start_new_round(game_pointer=self.game_pointer, raised=[p.in_chips for p in self.players])

        # Count the round. There are 4 rounds in each game.
        self.round_counter = 0

        # Save the history for stepping back to the last state.
        self.history = []

        state = self.get_state(self.game_pointer)

        return state, self.game_pointer
    
    def set_flop(self, cards):
        """Set specific flop cards
        
        Args:
            cards (list): List of 3 card objects to be used as flop
        """
        if not self.manual_dealer:
            return  # Do nothing if not in manual mode
            
        if hasattr(self.dealer, 'set_flop'):
            self.dealer.set_flop(cards)
            
            # If we were waiting for flop cards, resume the game
            if self.stage == Stage.WAITING_FOR_FLOP:
                self._deal_flop()
                self.stage = Stage.FLOP
    
    def set_turn(self, card):
        """Set specific turn card
        
        Args:
            card (object): Card object to be used as turn
        """
        if not self.manual_dealer:
            return  # Do nothing if not in manual mode
            
        if hasattr(self.dealer, 'set_turn'):
            self.dealer.set_turn(card)
            
            # If we were waiting for turn card, resume the game
            if self.stage == Stage.WAITING_FOR_TURN:
                self._deal_turn()
                self.stage = Stage.TURN
    
    def set_river(self, card):
        """Set specific river card
        
        Args:
            card (object): Card object to be used as river
        """
        if not self.manual_dealer:
            return  # Do nothing if not in manual mode
            
        if hasattr(self.dealer, 'set_river'):
            self.dealer.set_river(card)
            
            # If we were waiting for river card, resume the game
            if self.stage == Stage.WAITING_FOR_RIVER:
                self._deal_river()
                self.stage = Stage.RIVER
    
    def _deal_flop(self):
        """Deal the flop cards"""
        if hasattr(self.dealer, 'current_stage'):
            self.dealer.current_stage = 'flop'
        self.public_cards.append(self.dealer.deal_card())
        self.public_cards.append(self.dealer.deal_card())
        self.public_cards.append(self.dealer.deal_card())
    
    def _deal_turn(self):
        """Deal the turn card"""
        if hasattr(self.dealer, 'current_stage'):
            self.dealer.current_stage = 'turn'
        self.public_cards.append(self.dealer.deal_card())
    
    def _deal_river(self):
        """Deal the river card"""
        if hasattr(self.dealer, 'current_stage'):
            self.dealer.current_stage = 'river'
        self.public_cards.append(self.dealer.deal_card())

    def get_legal_actions(self):
        """
        Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        """
        # If we're waiting for manual cards, no betting actions are allowed
        if self.stage in (Stage.WAITING_FOR_FLOP, Stage.WAITING_FOR_TURN, Stage.WAITING_FOR_RIVER):
            return []  # No betting actions allowed while waiting for cards
        
        # Check if all players are either folded or all-in
        players_in_bypass = [1 if player.status in (PlayerStatus.FOLDED, PlayerStatus.ALLIN) else 0 for player in self.players]
        if sum(players_in_bypass) == self.num_players:
            return []  # No actions allowed when all players are all-in or folded
            
        return self.round.get_nolimit_legal_actions(players=self.players)

    def step(self, action):
        """
        Get the next state

        Args:
            action (str): a specific action. (call, raise, fold, or check)

        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next player id
        """
        # If we're waiting for manual cards, don't allow any actions
        if self.stage in (Stage.WAITING_FOR_FLOP, Stage.WAITING_FOR_TURN, Stage.WAITING_FOR_RIVER):
            raise Exception('Cannot take actions while waiting for manual cards')

        if action not in self.get_legal_actions():
            print(action, self.get_legal_actions())
            print(self.get_state(self.game_pointer))
            raise Exception('Action not allowed')

        if self.allow_step_back:
            # First snapshot the current state
            r = deepcopy(self.round)
            b = self.game_pointer
            r_c = self.round_counter
            d = deepcopy(self.dealer)
            p = deepcopy(self.public_cards)
            ps = deepcopy(self.players)
            self.history.append((r, b, r_c, d, p, ps))

        # Then we proceed to the next round
        self.game_pointer = self.round.proceed_round(self.players, action)

        players_in_bypass = [1 if player.status in (PlayerStatus.FOLDED, PlayerStatus.ALLIN) else 0 for player in self.players]
        if self.num_players - sum(players_in_bypass) == 1:
            last_player = players_in_bypass.index(0)
            if self.round.raised[last_player] >= max(self.round.raised):
                # If the last player has put enough chips, he is also bypassed
                players_in_bypass[last_player] = 1

        # Check if all players are either folded or all-in
        if sum(players_in_bypass) == self.num_players:
            # Skip all betting rounds and deal all remaining community cards
            if self.stage == Stage.PREFLOP:
                # Deal flop
                self._deal_flop()
                # Deal turn
                self._deal_turn()
                # Deal river
                self._deal_river()
                self.stage = Stage.SHOWDOWN
                self.round_counter = 3  # Set to end of river
            elif self.stage == Stage.FLOP:
                # Deal turn
                self._deal_turn()
                # Deal river
                self._deal_river()
                self.stage = Stage.SHOWDOWN
                self.round_counter = 3  # Set to end of river
            elif self.stage == Stage.TURN:
                # Deal river
                self._deal_river()
                self.stage = Stage.SHOWDOWN
                self.round_counter = 3  # Set to end of river
            elif self.stage == Stage.RIVER:
                self.stage = Stage.SHOWDOWN

        # If a round is over, we deal more public cards
        if self.round.is_over():
            # Game pointer goes to the first player not in bypass after the dealer, if there is one
            self.game_pointer = (self.dealer_id + 1) % self.num_players
            if sum(players_in_bypass) < self.num_players:
                while players_in_bypass[self.game_pointer]:
                    self.game_pointer = (self.game_pointer + 1) % self.num_players

            # Handle the end of each betting round
            if self.round_counter == 0:  # End of preflop
                if self.manual_dealer:
                    # Check if we have preset flop cards
                    if hasattr(self.dealer, 'has_preset_cards') and self.dealer.has_preset_cards('flop'):
                        self._deal_flop()
                        self.stage = Stage.FLOP
                    else:
                        # Wait for flop cards to be set
                        self.stage = Stage.WAITING_FOR_FLOP
                else:
                    # Automatic dealer mode
                    self._deal_flop()
                    self.stage = Stage.FLOP
                
            elif self.round_counter == 1:  # End of flop
                if self.manual_dealer:
                    # Check if we have preset turn card
                    if hasattr(self.dealer, 'has_preset_cards') and self.dealer.has_preset_cards('turn'):
                        self._deal_turn()
                        self.stage = Stage.TURN
                    else:
                        # Wait for turn card to be set
                        self.stage = Stage.WAITING_FOR_TURN
                else:
                    # Automatic dealer mode
                    self._deal_turn()
                    self.stage = Stage.TURN
                
            elif self.round_counter == 2:  # End of turn
                if self.manual_dealer:
                    # Check if we have preset river card
                    if hasattr(self.dealer, 'has_preset_cards') and self.dealer.has_preset_cards('river'):
                        self._deal_river()
                        self.stage = Stage.RIVER
                    else:
                        # Wait for river card to be set
                        self.stage = Stage.WAITING_FOR_RIVER
                else:
                    # Automatic dealer mode
                    self._deal_river()
                    self.stage = Stage.RIVER
            
            # Increment round counter
            self.round_counter += 1
            
            # Start a new bidding round
            self.round.start_new_round(self.game_pointer)

        state = self.get_state(self.game_pointer)

        return state, self.game_pointer

    def get_state(self, player_id):
        """
        Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        """
        self.dealer.pot = np.sum([player.in_chips for player in self.players])

        chips = [self.players[i].in_chips for i in range(self.num_players)]
        legal_actions = self.get_legal_actions()
        state = self.players[player_id].get_state(self.public_cards, chips, legal_actions)
        state['stakes'] = [self.players[i].remained_chips for i in range(self.num_players)]
        state['current_player'] = self.game_pointer
        state['pot'] = self.dealer.pot
        state['stage'] = self.stage
        
        # Add waiting_for_cards flag for manual dealer mode
        if self.stage in (Stage.WAITING_FOR_FLOP, Stage.WAITING_FOR_TURN, Stage.WAITING_FOR_RIVER):
            state['waiting_for_cards'] = True
            state['waiting_stage'] = self.stage
        else:
            state['waiting_for_cards'] = False
            
        return state

    def get_payoffs(self):
        """
        Return the payoffs of the game

        Returns:
            (list): Each entry corresponds to the payoff of one player
        """
        hands = [p.hand + self.public_cards if p.status in (PlayerStatus.ALIVE, PlayerStatus.ALLIN) else None for p in self.players]
        chips_payoffs = self.judger.judge_game(self.players, hands)
        return chips_payoffs

    def get_num_players(self):
        """
        Return the number of players in no limit texas holdem

        Returns:
            (int): The number of players in the game
        """
        return self.num_players

    def step_back(self):
        """
        Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        """
        if len(self.history) > 0:
            self.round, self.game_pointer, self.round_counter, self.dealer, self.public_cards, self.players = self.history.pop()
            self.stage = Stage(self.round_counter)
            return True
        return False

    @staticmethod
    def get_num_actions():
        """
        Return the number of applicable actions

        Returns:
            (int): The number of actions. There are 6 actions (call, raise_half_pot, raise_pot, all_in, check and fold)
        """
        return len(Action)
