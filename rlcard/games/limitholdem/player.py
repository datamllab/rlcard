
from rlcard.core import Player


class LimitholdemPlayer(Player):

    def __init__(self, player_id):
        self.player_id = player_id
        self.hand = []
        self.status = 'alive'

        # The chips that this player has put in until now
        self.in_chips = 0 

    def get_state(self, public_cards, opponent_chips):
        ''' Encode the state for the player

        Args:
            public_cards (list): A list of public cards that seen by all the players
            opponent_chips (int): the chips that the opponent has put in

        Returns:
            A dictionary of the state
        '''

        state = {}
        state['hand'] = [c.get_index() for c in self.hand]
        state['public_cards'] = [c.get_index() for c in public_cards]
        state['opponent_chips'] = opponent_chips
        state['my_chips'] = self.in_chips
        return state

    def get_player_id(self):
        return self.player_id

