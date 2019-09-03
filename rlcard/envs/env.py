from rlcard.utils.utils import *
import numpy as np

class Env(object):
    """ The main Env class
    """
    def __init__(self, game):
        self.game = game
        self.player_num = game.get_player_num()
        
        self.init_game = self.game.init_game
        self.step = self.game.step
        self.step_back = self.game.step_back
        self.get_state = self.game.get_state
        self.get_player_id = self.game.get_player_id
        self.end = self.game.end

    def set_agents(self, agents):
        """ Set the agents that will interact with the environment

        Args:
            agents: list of Agent classes; [agents]
        """

        self.agents = agents

    def set_seed(self, seed):
        """ Set the seed 
        Args:
            seed: integer
        """
        random.seed(seed)
        np.random.seed(seed)
        self.game.set_seed(seed)

    def run(self):
        """ Run a complete game

        Returns:
            trajectories
            payoffs
        """
        self.game.init_game()
        trajectories = [[] for _ in range(self.player_num)]

        # Loop to play the game
        player = self.game.get_player_id() # get the current player id
        state = self.game.get_state(player) # get the state of the first player
        trajectories[player].append(self.extract_state(state))
        while not self.game.end():
            # First, agent plays
            action = self.agents[player].step(state)

            # Second, environment steps
            next_state, next_player = self.game.step(action)

            # Third, save action
            trajectories[player].append(action)

            # Set the state and player
            state = next_state
            player = next_player
            
            # Save state.
            if not self.game.end():
                trajectories[player].append(self.extract_state(state))

        ## add a final state to all the players
        for player in range(self.player_num):
            state = self.game.get_state(player)
            trajectories[player].append(self.extract_state(state))

        # Reorganize the trajectories
        trajectories = reorganize(trajectories)
        payoffs = self.get_payoffs()


        return trajectories, payoffs


    def extract_state(self, state):
        """ Extract useful information from state for RL
        Args:
            state
        Returns:
            extracted state
        """
        pass

    def get_payoffs(self):
        """ Get the payoffs of players
        Returns:
            payoffs: a list of payoffs for each player
        """
        pass


