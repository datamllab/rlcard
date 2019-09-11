
from rlcard.core import Round

class LimitHoldemRound(Round):

    def __init__(self, players):
        pass

    def proceed_round(self, players, action):
        for player in players:
            player_status = player.play(action)
            if player_status == 'folded':
                players.pop(players.indexof(player))
        return players
