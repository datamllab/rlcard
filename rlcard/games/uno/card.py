
class UnoCard(object):

    info = {'type':  ['number', 'action', 'wild'],
            'color': ['r', 'g', 'b', 'y'],
            'trait': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
                      'skip', 'reverse', 'draw_2', 'wild', 'wild_draw_4']
            }

    def __init__(self, card_type, color, trait):
        self.type = card_type
        self.color = color
        self.trait = trait

    def get_str(self):
        return self.color + '-' + self.trait

# for test
if __name__ == '__main__':
    a = UnoCard('number', 'r', '5')
    b = UnoCard('number', 'r', '6')
    c = UnoCard('number', 'r', '7')
    cards = [a, b, c]
    for card in cards:
        card.color = 'g'

    for card in cards:
        print(card.get_str())
