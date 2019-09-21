
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
        self.str = self.get_str()

    def get_str(self):
        return self.color + '-' + self.trait
