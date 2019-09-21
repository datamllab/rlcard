from rlcard.games.uno.card import UnoCard as Card


def init_deck():
    deck = []
    card_info = Card.info
    for color in card_info['color']:

        # init number cards
        for num in card_info['trait'][:10]:
            deck.append(Card('number', color, num))
            if num != '0':
                deck.append(Card('number', color, num))

        # init action cards
        for action in card_info['trait'][10:13]:
            deck.append(Card('action', color, action))
            deck.append(Card('action', color, action))

        # init wild cards
        for wild in card_info['trait'][-2:]:
            deck.append(Card('wild', color, wild))
    return deck


def cards2list(cards):
    cards_list = []
    for card in cards:
        cards_list.append(card.get_str())
    return cards_list
