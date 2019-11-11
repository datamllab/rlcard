
class MahjongCard(object):

    info = {'type':  ['dots', 'bamboo', 'characters', 'dragons', 'winds'],
            'trait': ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'green', 'red', 'white', 'east', 'west', 'north', 'south']
            }

    def __init__(self, card_type, trait):
        ''' Initialize the class of MahjongCard

        Args:
            card_type (str): The type of card
            trait (str): The trait of card
        '''
        self.type = card_type
        self.trait = trait

    def get_str(self):
        ''' Get the string representation of card

        Return:
            (str): The string of card's color and trait
        '''
        return self.type+ '-'+ self.trait


# for test
#if __name__ == '__main__':
#    a = MajongCard('dots', '5')
#    b = MajongCard('bamboo', '6')
#    c = MajongCard('winds', 'south')
#    cards = [a, b, c]
#    for card in cards:
#        print(card.get_str())
