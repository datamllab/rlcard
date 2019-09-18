import random

from rlcard.games.uno.card import UnoCard


class UnoRound(object):

    def __init__(self, dealer, num_players):
        self.dealer = dealer
        self.target = None
        self.current_player = 0
        self.num_players = num_players
        self.direction = 1

    def flip_top_card(self):
        top = self.dealer.flip_top_card()
        if top.trait == 'wild':
            top.color = random.choice(UnoCard.info['color'])
        self.target = top
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

        # perform the number action
        if self.target.type == 'number':
            self.current_player = (self.current_player + self.direction) % self.num_players
            self.target = card

        # perform non-number action
        else:
            self._preform_non_number_action(players, self.target)

    def _perform_draw_action(self, players):
        card = self.dealer.deck.pop()
        if card.type == 'wild':
            card.color = random.choice(UnoCard.info['color'])
            self.target = card
            self.current_player = (self.current_player + self.direction) % self.num_players
        elif card.color == self.target.color:
            if card.type == 'number':
                self.target = card
                self.current_player = (self.current_player + self.direction) % self.num_players
            else:
                self._preform_non_number_action(players, card)
        else:
            players[self.current_player].hand.append(card)

    def _preform_non_number_action(self, players, card):
        current = self.current_player
        direction = self.direction
        num_players = self.num_players
        if card.trait == 'reverse':
            self.direction = -1 * direction
        elif card.trait == 'skip':
            current = (current + direction) % num_players
        elif card.trait == 'draw_2':
            self.dealer.deal_cards(players[(current + direction) % num_players], 2)
            current = (current + direction) % num_players
        elif card.trait == 'wild_draw_4':
            self.dealer.deal_cards(players[(current + direction) % num_players], 4)
            current = (current + direction) % num_players
        self.current_player = (current + self.direction) % num_players
        self.target = card

    def get_legal_actions(self, players, player_id):
        legal_actions = []
        wild_actions = []
        hand = players[player_id].hand
        target = self.target

        # target is wild card
        if target == 'wild' or self.target == 'wild_draw_4':
            for card in hand:
                if card.type == 'wild':
                    card.color = random.choice(UnoCard.info['color'])
                    wild_actions.append(card.get_str())
                elif card.color == target.color:
                    legal_actions.append(card.get_str())

        # target is aciton card or number card
        else:
            for card in hand:
                if card.type == 'wild':
                    card.color = random.choice(UnoCard.info['color'])
                    wild_actions.append(card.get_str())
                if card.color == target.color or card.trait == target.trait:
                    legal_actions.append(card.get_str())
        if not legal_actions:
            return wild_actions
        return legal_actions
