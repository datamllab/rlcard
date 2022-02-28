


from rlcard.games.doudizhu.utils import cards2str


class BeloteRound:
    def __init__(self, np_random, played_cards):
        self.np_random = np_random
        self.played_cards = played_cards
        self.trace = []

        self.dealer = Dealer(self.np_random)
        self.deck_str = cards2str(self.dealer.deck)

    def initiate(self,players):
        ''' Call dealer to deal cards.

        Args:
            players (list): list of BelotePlayer objects
        '''
        
        for i in range (2) :
            deal_cards(players[i])
        
        # il reste a implémenter ici le choix de l'atout 

    def proceed_round(self,player,action):
        ''' Call other Classes's functions to keep one round running

        Args:
            player (object): object of DoudizhuPlayer
            action (str): string of legal specific action

        Returns:
            object of BelotePlayer: player who played current biggest cards.
        '''

        
