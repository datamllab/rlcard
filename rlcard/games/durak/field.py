class Field:
    """A playing field containing the deck, players and cards that are
    put for everyone to see.
    Contains a list of cards on the field and a list that pairs an
    attack card with a card used to defend it.
    """

    def __init__(self):
        """Construct an empty field."""
        self.attack_cards = []
        self.defence_cards = []

    def __eq__(self, other):
        return (self.attack_cards == other.attack_cards
                and self.defence_cards == other.defence_cards)

    def __str__(self):
        return ('Attacks: ' + deck.cards_to_string(self.attack_cards)
                + '\nDefended: ' + deck.cards_to_string(self.defence_cards))

    def __repr__(self):
        return ('Attacks: ' + deck.cards_to_string(self.attack_cards, True)
                + '\nDefended: '
                + deck.cards_to_string(self.defence_cards, True))

    def get_cards(self):
        c = []
        for i in range(len(self.attack_cards)):
            c += [[self.attack_cards[i], self.defence_cards[i]]]
        return c

    def get_attack_cards(self):
        return self.attack_cards

    def get_defence_cards(self):
        return self.defence_cards



    def attack(self, cards):
        """Put the cards as attacks on the field."""
        self.attack_cards.extend(cards)

    def defend(self, to_defend, card):
        """Defend the card to defend with the given card."""
        assert to_defend in self.attack_cards, 'Card is not on the field'
        self.attack_cards.remove(to_defend)
        self.defence_cards.append((to_defend, card))

    def push(self, cards):
        """Add the cards used to push to the attack cards."""
        self.attack_cards.extend(cards)

    def take(self):
        """Return all cards on the field and clear it."""
        to_take = self.attack_cards[:]
        to_take.extend(
                [card for cards in self.defence_cards for card in cards])
        self.clear()
        return to_take

    def values_on_field(self, cards):
        """Test whether the given cards' values are on the
        field aleady.
        """
        found = [False] * len(cards)
        for i, card in enumerate(cards):
            for att_card in self.attack_cards:
                if card.num_value == att_card.num_value:
                    found[i] = True
                    break
            if not found[i]:
                for (att_card, def_card) in self.defence_cards:
                    if (card.num_value == att_card.num_value
                            or card.num_value == def_card.num_value):
                        found[i] = True
                        break
        return False not in found

    def on_field(self, card):
        """Test whether the given card is on the field."""
        for att_card in self.attack_cards:
            if att_card == card:
                return True
        for (att_card, def_card) in self.defence_cards:
            if att_card == card or def_card == card:
                return True
        return False

    def on_field_attack(self, card):
        """Test whether the given card is on the field as an attack."""
        for att_card in self.attack_cards:
            if att_card == card:
                return True
        return False

    def is_empty(self):
        """Test whether no cards are on the field."""
        return not (self.attack_cards or self.defence_cards)

    def clear(self):
        """Clear the playing field of cards."""
        del self.attack_cards[:]
        del self.defence_cards[:]