class LeducholdemPlayer(object):

    def __init__(self, player_id):
        ''' Initilize a player.

        Args:
            player_id (int): The id of the player
        '''
        self.player_id = player_id
        self.status = 'alive'
        self.hand = None

        # The chips that this player has put in until now
        self.in_chips = 0

    def get_state(self, public_card, all_chips, legal_actions):
        ''' Encode the state for the player

        Args:
            public_card (object): The public card that seen by all the players
            all_chips (int): The chips that all players have put in

        Returns:
            (dict): The state of the player
        '''
        state = {}
        state['hand'] = self.hand.get_index()
        state['public_card'] = public_card.get_index() if public_card else None
        state['all_chips'] = all_chips
        state['my_chips'] = self.in_chips
        state['legal_actions'] = legal_actions
        return state

    def get_player_id(self):
        ''' Return the id of the player
        '''
        return self.player_id
