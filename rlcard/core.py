''' Game-related and Env-related base classes
'''

class Card(object):
    '''
    Card stores the suit and rank of a single card

    Note:
        The suit variable in a standard card game should be one of [S, H, D, C, BJ, RJ] meaning [Spades, Hearts, Diamonds, Clubs, Black Joker, Red Joker]
        Similarly the rank variable should be one of [A, 2, 3, 4, 5, 6, 7, 8, 9, T, J, Q, K]
    '''

    suit = None
    rank = None
    valid_suit = ['S', 'H', 'D', 'C', 'BJ', 'RJ']
    valid_rank = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']

    def __init__(self, suit, rank):
        ''' Initialize the suit and rank of a card

        Args:
            suit: string, suit of the card, should be one of valid_suit
            rank: string, rank of the card, should be one of valid_rank
        '''
        self.suit = suit
        self.rank = rank

    def get_index(self):
        ''' Get index of a card.

        Returns:
            string: the combination of suit and rank of a card. Eg: 1S, 2H, AD, BJ, RJ...
        '''
        return self.suit+self.rank


class Dealer(object):
    ''' Dealer stores a deck of playing cards, remained cards holded by dealer, and can deal cards to players

    Note: deck variable means all the cards in a single game, and should be a list of Card objects.
    '''

    deck = []
    remained_cards = []

    def __init__(self):
        ''' The dealer should have all the cards at the beginning of a game
        '''
        raise NotImplementedError

    def shuffle(self):
        ''' Shuffle the cards holded by dealer(remained_cards)
        '''
        raise NotImplementedError

    def deal_cards(self, **kwargs):
        ''' Deal specific number of cards to a specific player

        Args:
            player_id: the id of the player to be dealt cards
            num: number of cards to be dealt
        '''
        raise NotImplementedError

class Player(object):
    ''' Player stores cards in the player's hand, and can determine the actions can be made according to the rules
    '''

    player_id = None
    hand = []

    def __init__(self, player_id):
        ''' Every player should have a unique player id
        '''
        self.player_id = player_id

    def available_order(self):
        ''' Get the actions can be made based on the rules

        Returns:
            list: a list of available orders
        '''
        raise NotImplementedError

    def play(self):
        ''' Player's actual action in the round
        '''
        raise NotImplementedError

class Judger(object):
    ''' Judger decides whether the round/game ends and return the winner of the round/game
    '''

    def judge_round(self, **kwargs):
        ''' Decide whether the round ends, and return the winner of the round

        Returns:
            int: return the player's id who wins the round or -1 meaning the round has not ended
        '''
        raise NotImplementedError

    def judge_game(self, **kwargs):
        ''' Decide whether the game ends, and return the winner of the game

        Returns:
            int: return the player's id who wins the game or -1 meaning the game has not ended
        '''
        raise NotImplementedError


class Round(object):
    ''' Round stores the id the ongoing round and can call other Classes' functions to keep the game running
    '''

    def __init__(self):
        ''' When the game starts, round id should be 1
        '''

        raise NotImplementedError

    def proceed_round(self, **kwargs):
        ''' Call other Classes's functions to keep the game running
        '''
        raise NotImplementedError


class Game(object):
    ''' Game class. This class will interact with outer environment.
    '''

    def init_game(self):
        ''' Initialize all characters in the game and start round 1
        '''
        raise NotImplementedError

    def step(self, action):
        ''' Perform one draw of the game and return next player number, and the state for next player
        '''
        raise NotImplementedError

    def step_back(self):
        ''' Takes one step backward and restore to the last state
        '''
        raise NotImplementedError

    def get_player_num(self):
        ''' Retrun the number of players in the game
        '''
        raise NotImplementedError

    def get_action_num(self):
        ''' Return the number of possible actions in the game
        '''
        raise NotImplementedError

    def get_player_id(self):
        ''' Return the current player that will take actions soon
        '''
        raise NotImplementedError

    def is_over(self):
        ''' Return whether the current game is over
        '''
        raise NotImplementedError

