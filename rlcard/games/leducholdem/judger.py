from rlcard.utils.utils import rank2int

class LeducholdemJudger:
    ''' The Judger class for Leduc Hold'em
    '''
    def __init__(self, np_random):
        ''' Initialize a judger class
        '''
        self.np_random = np_random

    @staticmethod
    def judge_game(players, public_card):
        ''' Judge the winner of the game.

        Args:
            players (list): The list of players who play the game
            public_card (object): The public card that seen by all the players

        Returns:
            (list): Each entry of the list corresponds to one entry of the
        '''
        # Judge who are the winners
        winners = [0] * len(players)
        fold_count = 0
        ranks = []
        # If every player folds except one, the alive player is the winner
        for idx, player in enumerate(players):
            ranks.append(rank2int(player.hand.rank))
            if player.status == 'folded':
               fold_count += 1
            elif player.status == 'alive':
                alive_idx = idx
        if fold_count == (len(players) - 1):
            winners[alive_idx] = 1
        
        # If any of the players matches the public card wins
        if sum(winners) < 1:
            for idx, player in enumerate(players):
                if player.hand.rank == public_card.rank:
                    winners[idx] = 1
                    break
        
        # If non of the above conditions, the winner player is the one with the highest card rank
        if sum(winners) < 1:
            max_rank = max(ranks)
            max_index = [i for i, j in enumerate(ranks) if j == max_rank]
            for idx in max_index:
                winners[idx] = 1

        # Compute the total chips
        total = 0
        for p in players:
            total += p.in_chips

        each_win = float(total) / sum(winners)

        payoffs = []
        for i, _ in enumerate(players):
            if winners[i] == 1:
                payoffs.append(each_win - players[i].in_chips)
            else:
                payoffs.append(float(-players[i].in_chips))

        return payoffs
