from rlcard.games.limitholdem.utils import compare_hands
import numpy as np


class LimitHoldemJudger:
    """The Judger class for limit texas holdem"""

    def __init__(self, np_random):
        self.np_random = np_random

    def judge_game(self, players, hands):
        """
        Judge the winner of the game.

        Args:
            players (list): The list of players who play the game
            hands (list): The list of hands that from the players

        Returns:
            (list): Each entry of the list corresponds to one entry of the
        """
        # Convert the hands into card indexes
        hands = [[card.get_index() for card in hand] if hand is not None else None for hand in hands]
        
        in_chips = [p.in_chips for p in players]
        remaining = sum(in_chips)
        payoffs = [0] * len(hands)
        while remaining > 0:
            winners = compare_hands(hands)
            each_win = self.split_pots_among_players(in_chips, winners)
            
            for i in range(len(players)):
                if winners[i]:
                    remaining -= each_win[i]
                    payoffs[i] += each_win[i] - in_chips[i]
                    hands[i] = None
                    in_chips[i] = 0
                elif in_chips[i] > 0:
                    payoffs[i] += each_win[i] - in_chips[i]
                    in_chips[i] = each_win[i]
                    
        assert sum(payoffs) == 0
        return payoffs

    def split_pot_among_players(self, in_chips, winners):
        """
        Splits the next (side) pot among players.
        Function is called in loop by distribute_pots_among_players until all chips are allocated.

        Args:
            in_chips (list): List with number of chips bet not yet distributed for each player
            winners (list): List with 1 if the player is among winners else 0

        Returns:
            (list): Of how much chips each player get after this pot has been split and list of chips left to distribute
        """
        nb_winners_in_pot = sum((winners[i] and in_chips[i] > 0) for i in range(len(in_chips)))
        nb_players_in_pot = sum(in_chips[i] > 0 for i in range(len(in_chips)))
        if nb_winners_in_pot == 0 or nb_winners_in_pot == nb_players_in_pot:
            # no winner or all winners for this pot
            allocated = list(in_chips)  # we give back their chips to each players in this pot
            in_chips_after = len(in_chips) * [0]  # no more chips to distribute
        else:
            amount_in_pot_by_player = min(v for v in in_chips if v > 0)
            how_much_one_win, remaining = divmod(amount_in_pot_by_player * nb_players_in_pot, nb_winners_in_pot)
            '''
            In the event of a split pot that cannot be divided equally for every winner, the winner who is sitting 
            closest to the left of the dealer receives the remaining differential in chips cf 
            https://www.betclic.fr/poker/house-rules--play-safely--betclic-poker-cpok_rules to simplify and as this 
            case is very rare, we will give the remaining differential in chips to a random winner
            '''
            allocated = len(in_chips) * [0]
            in_chips_after = list(in_chips)
            for i in range(len(in_chips)):  # iterate on all players
                if in_chips[i] == 0:  # player not in pot
                    continue
                if winners[i]:
                    allocated[i] += how_much_one_win
                in_chips_after[i] -= amount_in_pot_by_player
            if remaining > 0:
                random_winning_player = self.np_random.choice(
                    [i for i in range(len(winners)) if winners[i] and in_chips[i] > 0])
                allocated[random_winning_player] += remaining
        assert sum(in_chips[i] - in_chips_after[i] for i in range(len(in_chips))) == sum(allocated)
        return allocated, in_chips_after

    def split_pots_among_players(self, in_chips_initial, winners):
        """
        Splits main pot and side pots among players (to handle special case of all-in players).

        Args:
            in_chips_initial (list): List with number of chips bet for each player
            winners (list): List with 1 if the player is among winners else 0

        Returns:
            (list): List of how much chips each player get back after all pots have been split
        """
        in_chips = list(in_chips_initial)
        assert len(in_chips) == len(winners)
        assert all(v == 0 or v == 1 for v in winners)
        assert sum(winners) >= 1  # there must be at least one winner
        allocated = np.zeros(len(in_chips), dtype=int)
        while any(v > 0 for v in in_chips):  # while there are still chips to allocate
            allocated_current_pot, in_chips = self.split_pot_among_players(in_chips, winners)
            allocated += allocated_current_pot  # element-wise addition
        assert all(chips >= 0 for chips in allocated)  # check that all players got a non negative amount of chips
        assert sum(in_chips_initial) == sum(allocated)  # check that all chips bet have been allocated
        return list(allocated)
