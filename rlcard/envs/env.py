from rlcard.utils.utils import *
import numpy as np

class Env(object):
    """ The main Env class
    """
    def __init__(self, game):
        self.game = game

        # get number of players in this game
        self.player_num = game.get_player_num()
        self.action_num = game.get_action_num()
        
        self.step_back = self.game.step_back
        self.get_player_id = self.game.get_player_id
        self.is_over = self.game.is_over
    
    def init_game(self):
        """ Initilize a new game
        Returns:
            state: the begining state of the game
            player_id: the begining player
        """
        state, player_id = self.game.init_game()
        return self.extract_state(state), player_id

    def step(self, action):
        """ Step froward
        Args:
            action: the action taken by the current player
        Returns:
            next_state: the next state
            player_id: the ID of the next player
        """
        next_state, player_id = self.game.step(self.decode_action(action))
        return self.extract_state(next_state), player_id

    def step_back():
        """ Step back
        Returns:
            next_state: the previous state
            player_id: the ID of the previous player
        """
        state, player_id = self.game.step_back()
        return state, player_id

    def get_state(self, player_id):
        """ Get the state given player id
        Args:
            player_id: the player id
        Returns:
            state
        """
        return self.extract_state(self.game.get_state(player_id))

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

    def run(self, is_training=False):
        """ Run a complete game for training reinforcement learning.
        Args:
            is_training: True if for training purpose
        Returns:
            trajectories: 1d -> player; 2d -> transition;
            3d -> state, action, reward, next_state, done
        """

        trajectories = [[] for _ in range(self.player_num)]
        state, player_id = self.init_game()
        
        # Loop to play the game
        trajectories[player_id].append(state)
        while not self.is_over():
            # Agent plays
            if not is_training:
                action = self.agents[player_id].eval_step(state)
            else:
                action = self.agents[player_id].step(state)

            # Environment steps
            next_state, next_player_id = self.step(action)

            # Save action
            trajectories[player_id].append(action)

            # Set the state and player
            state = next_state
            player_id = next_player_id
            
            # Save state.
            if not self.game.is_over():
                trajectories[player_id].append(state)

        # Add a final state to all the players
        for player_id in range(self.player_num):
            state = self.get_state(player_id)
            trajectories[player_id].append(state)

        # Payoffs
        payoffs = self.get_payoffs()

        # Reorganize the trajectories
        trajectories = reorganize(trajectories, payoffs)

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

    def decode_action(self, action_id):
        """ Action id -> the action in the game
        Args:
            action_id: the id of the action
        Returns:
            action
        """
        pass
            
