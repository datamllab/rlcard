import random

from rlcard.games.uno.card import UnoCard
from rlcard.games.uno.utils import cards2list


class UnoRound(object):

    def __init__(self, dealer, num_players):
        self.dealer = dealer
        self.target = None
        self.current_player = 0
        self.num_players = num_players
        self.direction = 1
        self.played_cards = []
        self.is_over = False

    def flip_top_card(self):
        top = self.dealer.flip_top_card()
        if top.trait == 'wild':
            top.color = random.choice(UnoCard.info['color'])
        self.target = top
        self.played_cards.append(top)
        return top

    def perform_top_card(self, players, top_card):
        if top_card.trait == 'skip':
            self.current_player = 1
        elif top_card.trait == 'reverse':
            self.current_player = 3
            self.direction = -1
        elif top_card.trait == 'draw_2':
            player = players[self.current_player]
            self.dealer.deal_cards(player, 2)

    def proceed_round(self, players, action):
        if action == 'draw':
            self._perform_draw_action(players)
            return None
        player = players[self.current_player]
        card_info = action.split('-')
        color = card_info[0]
        trait = card_info[1]

        #print('proceed round', color, trait)

        # remove correspongding card
        remove_index = None
        if 'wild' in trait:
            for index, card in enumerate(player.hand):
                if trait == card.trait:
                    remove_index = index
                    break
        else:
            for index, card in enumerate(player.hand):
                if color == card.color and trait == card.trait:
                    remove_index = index
        card = player.hand.pop(remove_index)
        if not player.hand:
            self.is_over = True
        self.played_cards.append(card)
        #print('proceed card', card.type, card.color, card.trait)

        # perform the number action
        if card.type == 'number':
            self.current_player = (self.current_player + self.direction) % self.num_players
            self.target = card

        # perform non-number action
        else:
            #print('perfrom non number')
            self._preform_non_number_action(players, card)

    def _perform_draw_action(self, players):
        if not self.dealer.deck:
            self.dealer.deck = self.played_cards
            self.dealer.shuffle()
            self.played_cards = []
        card = self.dealer.deck.pop()
        if card.type == 'wild':
            card.color = random.choice(UnoCard.info['color'])
            self.target = card
            self.played_cards.append(card)
            self.current_player = (self.current_player + self.direction) % self.num_players
        elif card.color == self.target.color:
            if card.type == 'number':
                self.target = card
                self.played_cards.append(card)
                self.current_player = (self.current_player + self.direction) % self.num_players
            else:
                self.played_cards.append(card)
                self._preform_non_number_action(players, card)
        else:
            players[self.current_player].hand.append(card)
            self.current_player = (self.current_player + self.direction) % self.num_players

    def _preform_non_number_action(self, players, card):
        current = self.current_player
        direction = self.direction
        num_players = self.num_players
        if card.trait == 'reverse':
            self.direction = -1 * direction
        elif card.trait == 'skip':
            current = (current + direction) % num_players
            #print('skip current', current)
        elif card.trait == 'draw_2':
            self.dealer.deal_cards(players[(current + direction) % num_players], 2)
            current = (current + direction) % num_players
            #print('draw_2 current', current)
        elif card.trait == 'wild_draw_4':
            self.dealer.deal_cards(players[(current + direction) % num_players], 4)
            current = (current + direction) % num_players
            #print('wild_draw_4 current', current)
        self.current_player = (current + self.direction) % num_players
        #print('non number current player', self.current_player)
        self.target = card
        #print('non number card', card.type, card.color, card.trait)
        #print('non number target', self.target.type, self.target.color, self.target.trait)

    def get_legal_actions(self, players, player_id):
        legal_actions = []
        wild_4_actions = []
        hand = players[player_id].hand
        target = self.target
        #print('legal action target: ', target.type, target.color, target.trait)
        # target is wild card
        if target.type == 'wild':
            for card in hand:
                if card.type == 'wild':
                    card.color = random.choice(UnoCard.info['color'])
                    if card.trait == 'wild_draw_4':
                        wild_4_actions.append(card.get_str())
                    else:
                        legal_actions.append(card.get_str())
                elif card.color == target.color:
                    legal_actions.append(card.get_str())

        # target is aciton card or number card
        else:
            for card in hand:
                if card.type == 'wild':
                    card.color = random.choice(UnoCard.info['color'])
                    if card.trait == 'wild_draw_4':
                        #print('target is not wild')
                        wild_4_actions.append(card.get_str())
                        #print('wild actions', wild_4_actions)
                    else:
                        legal_actions.append(card.get_str())
                elif card.color == target.color or card.trait == target.trait:
                    legal_actions.append(card.get_str())
        if not legal_actions:
            return wild_4_actions
        return legal_actions

    def get_state(self, players, player_id):
        state = {}
        player = players[player_id]
        state['hand'] = cards2list(player.hand)
        state['target'] = self.target.get_str()
        state['played_cards'] = cards2list(self.played_cards)
        others_hand = []
        for player in players:
            if player.player_id != player_id:
                others_hand.extend(player.hand)
        state['others_hand'] = cards2list(others_hand)
        return state
