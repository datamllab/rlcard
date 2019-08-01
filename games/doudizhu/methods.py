# -*- coding: utf-8 -*-
"""for formatting"""


def cards2str(cards: list):
    response = ''
    for card in cards:
        if card.rank == '':
            response += card.suit[0]
        else:
            if card.rank == '10':
                response += 'T'
            else:
                response += card.rank
    return response
