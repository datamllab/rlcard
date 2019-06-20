# Game-related and Env-related abstractions

class Card(object):
    """
    Card stores the suit and rank of a single card

    Note: 
        The suit variable in a standard card game should be one of [S, H, D, C, BJ, RJ] meaning [Spades, Hearts, Diamonds, Clubs, Black Joker, Red Joker]
        Similarly the rank variable should be one of [A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K]
    """

    suit = None
    rank = None
    valid_suit = ['S', 'H', 'D', 'C', 'BJ', 'RJ']
    valid_rank = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

    def __init__(self, suit, rank):
        """ Initialize the suit and rank of a card

        Args:
            suit: string, suit of the card, should be one of valid_suit
            rank: string, rank of the card, should be one of valid_rank
        """
        if(suit == 'BJ' or suit == 'RJ'):
            assert (rank == ''), "Rank should be empty when suit is 'BJ' or 'RJ'"
        else:
            assert (suit in self.valid_suit), "Invalid suit input"
            assert (rank in self.valid_rank), "Invalid rank input"
        self.suit = suit
        self.rank = rank

    def get_index(self):
        """Get index of a card. 

        Return:
            string: the combination of suit and rank of a card. Eg: 1S, 2H, AD, BJ, RJ...
        """
        return self.suit+self.rank


class Dealer(object):
    """
    Dealer stores a deck of playing cards, remained cards holded by dealer, and can deal cards to players

    Note: deck variable means all the cards in a single game, and should be a list of Card objects.
    """

    deck = []
    remained_cards = []

    def __init__(self):
        """The dealer should have all the cards at the beginning of a game
        """

    def shuffle(self):
        """Shuffle the cards holded by dealer(remained_cards)
        """

    def deal_cards(self, player_id, num):
        """Deal specific number of cards to a specific player

        Args:
            player_id: the id of the player to be dealt cards
            num: number of cards to be dealt
        """



class Player(object):
    """
    Player stores cards in the player's hand, and can determine the actions can be made according to the rules
    """

    player_id = None
    hand = []

    def __init__(self):
        """Every player should have a unique player id
        """

    def available_order(self):
        """Get the actions can be made based on the rules

        Return:
            list: a list of available orders
        """

    def play(self):
        """player's actual action in the round
        """


class Judger(object):
    """
    Judger decides whether the round/game ends and return the winner of the round/game
    """

    def judge_round(self):
        """decide whether the round ends, and return the winner of the round

        Return:
            int: return the player's id who wins the round or -1 meaning the round has not ended
        """

    def judge_game(self):
        """decide whether the game ends, and return the winner of the game

        Return:
            int: return the player's id who wins the game or -1 meaning the game has not ended
        """


class Round(object):
    """
    Round stores the id the ongoing round and can call other Classes' functions to keep the game running
    """

    round_id = None

    def __init__(self):
        """When the game starts, round id should be 1
        """

    def proceed_round(self):
        """Call other Classes's functions to keep the game running
        """


class Game(object):
    """
    Start the card game
    """
    
    def start_game(self):
        """Initialize all characters in the game and start round 1
        """

    def step(self, current_action):
        """Perform one draw of the game and return next player number, and the state for next player
        """
        return next_player, next_state


class Monitor(object):
    """
    Monitor records useful information in the game
    """

    last_played = []
    all_played = []
