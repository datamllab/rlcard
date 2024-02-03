from termcolor import colored

class SkullKingCard:

    info = {'type':  ['suit','black', 'escape', 'pirate'],
            'color': ['green', 'yellow', 'purple', 'black','pirate','escape','special_pirate'],
            'trait': ['1', '2', '3', '4', '5', '6', '7', '8', '9','10','11','12','13'
                      'pirate', 'tigress', 'skull king', 'escape']
            }

    def __init__(self, card_type, color, trait):
        ''' Initialize the class of SkullKingCard

        Args:
            card_type (str): The type of card
            color (str): The color of card
            trait (str): The trait of card
        '''
        self.type = card_type
        self.color = color
        self.trait = trait
        self.str = self.get_str()

    def get_str(self):
        ''' Get the string representation of card

        Return:
            (str): The string of card's color and trait
        '''
        return self.color + '-' + self.trait


    @staticmethod
    def print_cards(cards):
        ''' Print out card in a nice form

        Args:
            card (str or list): The string form or a list of a UNO card
            wild_color (boolean): True if assign collor to wild cards
        '''
        if isinstance(cards, str):
            cards = [cards]
        for i, card in enumerate(cards):
            if card == 'escape':
                trait = 'Escape'
            else:
                color, trait = card.split('-')

                if trait == 'pirate':
                    trait = 'Pirate'
                elif trait == 'tigress':
                    trait = 'Tigress'
                elif trait == 'skull_king':
                    trait = 'Skull King'
                else :
                    trait = 'Suit'

            if trait == 'Escape' or trait == 'Pirate' or trait == 'Skull King' or trait == 'Tigress':
                print(trait, end='')
            elif color == 'yellow':
                print(colored(trait, 'yellow'), end='')
            elif color == 'green':
                print(colored(trait, 'green'), end='')
            elif color == 'purple':
                print(colored(trait, 'purple'), end='')
            elif color == 'black':
                print(colored(trait, 'black'), end='')

            if i < len(cards) - 1:
                print(', ', end='')
