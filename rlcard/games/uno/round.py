from rlcard.games.uno.card import UnoCard
from rlcard.games.uno.utils import cards2list, WILD, WILD_DRAW_4


class UnoRound:

    def __init__(self, dealer, num_players, np_random):
        ''' Initialize the round class

        Args:
            dealer (object): the object of UnoDealer
            num_players (int): the number of players in game
        '''
        self.np_random = np_random
        self.dealer = dealer
        self.target = None
        self.current_player = 0
        self.num_players = num_players
        self.direction = 1
        self.played_cards = []
        self.is_over = False
        self.winner = None

    def flip_top_card(self):
        ''' Flip the top card of the card pile

        Returns:
            (object of UnoCard): the top card in game

        '''
        top = self.dealer.flip_top_card()
        if top.trait == 'wild':
            top.color = self.np_random.choice(UnoCard.info['color'])
        self.target = top
        self.played_cards.append(top)
        return top

    def perform_top_card(self, players, top_card):
        ''' Perform the top card

        Args:
            players (list): list of UnoPlayer objects
            top_card (object): object of UnoCard
        '''
        if top_card.trait == 'skip':
            self.current_player = 1
        elif top_card.trait == 'reverse':
            self.direction = -1
            self.current_player = (0 + self.direction) % self.num_players
        elif top_card.trait == 'draw_2':
            player = players[self.current_player]
            self.dealer.deal_cards(player, 2)

    def proceed_round(self, players, action):
        ''' Call other Classes's functions to keep one round running

        Args:
            player (object): object of UnoPlayer
            action (str): string of legal action
        '''
        if action == 'draw':
            self._perform_draw_action(players)
            return None
        player = players[self.current_player]
        card_info = action.split('-')
        color = card_info[0]
        trait = card_info[1]
        # remove correspongding card
        remove_index = None
        if trait == 'wild' or trait == 'wild_draw_4':
            for index, card in enumerate(player.hand):
                if trait == card.trait:
                    remove_index = index
                    break
        else:
            for index, card in enumerate(player.hand):
                if color == card.color and trait == card.trait:
                    remove_index = index
                    break
        card = player.hand.pop(remove_index)
        if not player.hand:
            self.is_over = True
            self.winner = [self.current_player]
        self.played_cards.append(card)

        # perform the number action
        if card.type == 'number':
            self.current_player = (self.current_player + self.direction) % self.num_players
            self.target = card

        # perform non-number action
        else:
            self._preform_non_number_action(players, card)

    def get_legal_actions(self, players, player_id):
        wild_flag = 0
        wild_draw_4_flag = 0
        legal_actions = []
        wild_4_actions = []
        hand = players[player_id].hand
        target = self.target
        if target.type == 'wild':
            for card in hand:
                if card.type == 'wild':
                    if card.trait == 'wild_draw_4':
                        if wild_draw_4_flag == 0:
                            wild_draw_4_flag = 1
                            wild_4_actions.extend(WILD_DRAW_4)
                    else:
                        if wild_flag == 0:
                            wild_flag = 1
                            legal_actions.extend(WILD)
                elif card.color == target.color:
                    legal_actions.append(card.str)

        # target is aciton card or number card
        else:
            for card in hand:
                if card.type == 'wild':
                    if card.trait == 'wild_draw_4':
                        if wild_draw_4_flag == 0:
                            wild_draw_4_flag = 1
                            wild_4_actions.extend(WILD_DRAW_4)
                    else:
                        if wild_flag == 0:
                            wild_flag = 1
                            legal_actions.extend(WILD)
                elif card.color == target.color or card.trait == target.trait:
                    legal_actions.append(card.str)
        if not legal_actions:
            legal_actions = wild_4_actions
        if not legal_actions:
            legal_actions = ['draw']
        return legal_actions

    def get_state(self, players, player_id):
        ''' Get player's state

        Args:
            players (list): The list of UnoPlayer
            player_id (int): The id of the player
        '''
        state = {}
        player = players[player_id]
        state['hand'] = cards2list(player.hand)
        state['target'] = self.target.str
        state['played_cards'] = cards2list(self.played_cards)
        state['legal_actions'] = self.get_legal_actions(players, player_id)
        state['num_cards'] = []
        for player in players:
            state['num_cards'].append(len(player.hand))
        return state

    def replace_deck(self):
        ''' Add cards have been played to deck
        '''
        self.dealer.deck.extend(self.played_cards)
        self.dealer.shuffle()
        self.played_cards = []

    def _perform_draw_action(self, players):
        # replace deck if there is no card in draw pile
        if not self.dealer.deck:
            self.replace_deck()
            #self.is_over = True
            #self.winner = UnoJudger.judge_winner(players)
            #return None

        card = self.dealer.deck.pop()

        # draw a wild card
        if card.type == 'wild':
            card.color = self.np_random.choice(UnoCard.info['color'])
            self.target = card
            self.played_cards.append(card)
            self.current_player = (self.current_player + self.direction) % self.num_players

        # draw a card with the same color of target
        elif card.color == self.target.color:
            if card.type == 'number':
                self.target = card
                self.played_cards.append(card)
                self.current_player = (self.current_player + self.direction) % self.num_players
            else:
                self.played_cards.append(card)
                self._preform_non_number_action(players, card)

        # draw a card with the diffrent color of target
        else:
            players[self.current_player].hand.append(card)
            self.current_player = (self.current_player + self.direction) % self.num_players

    def _preform_non_number_action(self, players, card):
        current = self.current_player
        direction = self.direction
        num_players = self.num_players

        # perform reverse card
        if card.trait == 'reverse':
            self.direction = -1 * direction

        # perfrom skip card
        elif card.trait == 'skip':
            current = (current + direction) % num_players

        # perform draw_2 card
        elif card.trait == 'draw_2':
            if len(self.dealer.deck) < 2:
                self.replace_deck()
                #self.is_over = True
                #self.winner = UnoJudger.judge_winner(players)
                #return None
            self.dealer.deal_cards(players[(current + direction) % num_players], 2)
            current = (current + direction) % num_players

        # perfrom wild_draw_4 card
        elif card.trait == 'wild_draw_4':
            if len(self.dealer.deck) < 4:
                self.replace_deck()
                #self.is_over = True
                #self.winner = UnoJudger.judge_winner(players)
                #return None
            self.dealer.deal_cards(players[(current + direction) % num_players], 4)
            current = (current + direction) % num_players
        self.current_player = (current + self.direction) % num_players
        self.target = card
