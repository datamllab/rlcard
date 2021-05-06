from enum import Enum


class PlayerStatus(Enum):
    ALIVE = 0
    FOLDED = 1
    ALLIN = 2


class LimitholdemPlayer:

    def __init__(self, player_id, np_random):
        ''' Initilize a player.

        Args:
            player_id (int): The id of the player
        '''
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []
        self.status = PlayerStatus.ALIVE

        # The chips that this player has put in until now
        self.in_chips = 0

    def get_state(self, public_cards, all_chips, legal_actions):
        ''' Encode the state for the player

        Args:
            public_cards (list): A list of public cards that seen by all the players
            all_chips (int): The chips that all players have put in

        Returns:
            (dict): The state of the player
        '''
        state = {}
        state['hand'] = [c.get_index() for c in self.hand]
        state['public_cards'] = [c.get_index() for c in public_cards]
        state['all_chips'] = all_chips
        state['my_chips'] = self.in_chips
        state['legal_actions'] = legal_actions
        return state

    def get_player_id(self):
        ''' Return the id of the player
        '''
        return self.player_id
