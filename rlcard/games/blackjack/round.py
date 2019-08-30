
from rlcard.core import Round

class BlackjackRound(Round):

    def __init__(self, players):
        pass

    def proceed_round(self, players, action):
        for player in players:
            player_status = player.play(action)
            if player_status == 'bust':
                players.pop(players.indexof(player))
        return players
