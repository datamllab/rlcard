
class MahjongCard:

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
        self.index_num = 0

    def get_str(self):
        ''' Get the string representation of card

        Return:
            (str): The string of card's color and trait
        '''
        return self.type+ '-'+ self.trait

    def set_index_num(self, index_num):

        self.index_num = index_num
        

