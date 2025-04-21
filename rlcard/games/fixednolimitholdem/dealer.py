from rlcard.games.limitholdem import Dealer


class NolimitholdemDealer(Dealer):
    def __init__(self, np_random):
        super().__init__(np_random)
        # Initialize new properties with default values
        self.preset_player0_hand = []
        self.preset_flop = []
        self.preset_turn = None
        self.preset_river = None
        self.current_stage = None
        self.manual_mode = False  # Default to automatic dealing
        self.player0_cards_dealt = 0  # Track how many cards have been dealt to player 0
    
    def enable_manual_mode(self):
        """Enable manual card selection mode"""
        self.manual_mode = True
    
    def set_player0_hand(self, cards):
        """Set specific cards for Player 0's hand
        
        Args:
            cards (list): List of card objects to be used as Player 0's hand
        """
        if not self.manual_mode:
            return  # Do nothing if not in manual mode
            
        self.preset_player0_hand = cards.copy()  # Make a copy to avoid modifying the original
        # Remove these cards from the deck
        for card in cards:
            if card in self.deck:
                self.deck.remove(card)
    
    def set_flop(self, cards):
        """Set specific flop cards
        
        Args:
            cards (list): List of 3 card objects to be used as flop
        """
        if not self.manual_mode:
            return  # Do nothing if not in manual mode
            
        if len(cards) != 3:
            raise ValueError("Flop must consist of exactly 3 cards")
        self.preset_flop = cards.copy()  # Make a copy to avoid modifying the original
        # Remove these cards from the deck
        for card in cards:
            if card in self.deck:
                self.deck.remove(card)
    
    def set_turn(self, card):
        """Set specific turn card
        
        Args:
            card (object): Card object to be used as turn
        """
        if not self.manual_mode:
            return  # Do nothing if not in manual mode
            
        self.preset_turn = card
        # Remove this card from the deck
        if card in self.deck:
            self.deck.remove(card)
    
    def set_river(self, card):
        """Set specific river card
        
        Args:
            card (object): Card object to be used as river
        """
        if not self.manual_mode:
            return  # Do nothing if not in manual mode
            
        self.preset_river = card
        # Remove this card from the deck
        if card in self.deck:
            self.deck.remove(card)
    
    def has_preset_cards(self, stage):
        """Check if dealer has preset cards for the given stage
        
        Args:
            stage (str): The stage to check ('flop', 'turn', or 'river')
            
        Returns:
            (bool): True if dealer has preset cards for the stage
        """
        if not self.manual_mode:
            return True  # In automatic mode, we always have cards
            
        if stage == 'flop':
            return len(self.preset_flop) == 3
        elif stage == 'turn':
            return self.preset_turn is not None
        elif stage == 'river':
            return self.preset_river is not None
        return False
    
    def deal_card(self, player_id=None):
        """Deal a card from the deck
        
        Args:
            player_id (int, optional): The ID of the player to deal to
            
        Returns:
            (object): A card object
        """
        # Only use preset cards if in manual mode
        if self.manual_mode and player_id == 0 and self.player0_cards_dealt < 2 and len(self.preset_player0_hand) > 0:
            # For player 0's hand (first two cards)
            card = self.preset_player0_hand.pop(0)
            self.player0_cards_dealt += 1
            return card
            
        # For community cards based on current stage
        if self.manual_mode:
            if self.current_stage == 'flop' and len(self.preset_flop) > 0:
                return self.preset_flop.pop(0)
            elif self.current_stage == 'turn' and self.preset_turn is not None:
                card = self.preset_turn
                self.preset_turn = None
                return card
            elif self.current_stage == 'river' and self.preset_river is not None:
                card = self.preset_river
                self.preset_river = None
                return card
        
        # Default behavior - deal from deck
        return super().deal_card()
    
    def shuffle(self):
        """Shuffle the deck"""
        super().shuffle()
        # Reset the player0_cards_dealt counter when shuffling
        self.player0_cards_dealt = 0
