import numpy as np
import random

from rlcard.utils.utils import *

class Env(object):
    ''' The base Env class
    '''

    def __init__(self, game, allow_step_back=False):
        ''' Initialize

        Args:
            game (Game): The Game class
            allow_step_back (boolean): True if allowing step_back
        '''
        self.name = None
        self.game = game
        self.allow_step_back = allow_step_back

        # Get number of players/actions in this game
        self.player_num = game.get_player_num()
        self.action_num = game.get_action_num()

        # A counter for the timesteps
        self.timestep = 0

        # MODES
        self.single_agent_mode = False
        self.active_player = None
        self.human_mode = False


    def init_game(self):
        ''' Start a new game

        Returns:
            (tuple): Tuple containing:

                (numpy.array): The begining state of the game
                (int): The begining player
        '''
        state, player_id = self.game.init_game()
        return self.extract_state(state), player_id

    def step(self, action):
        ''' Step forward

        Args:
            action (int): the action taken by the current player

        Returns:
            (tuple): Tuple containing:

                (numpy.array): The next state
                (int): The ID of the next player
        '''
        if self.single_agent_mode or self.human_mode:
            return self.single_agent_step(action)

        self.timestep += 1
        next_state, player_id = self.game.step(self.decode_action(action))
        
        return self.extract_state(next_state), player_id

    def single_agent_step(self, action):
        ''' Step forward for human/single agent

        Args:
            action (int): the action takem by the current player

        Returns:
            next_state (numpy.array): The next state
        '''
        reward = 0.
        done = False
        self.timestep += 1
        state, player_id = self.game.step(self.decode_action(action))
        while not self.game.is_over() and not player_id == self.active_player:
            self.timestep += 1
            if self.model.use_raw:
                action = self.model.agents[player_id].eval_step(state)
            else:
                action = self.model.agents[player_id].eval_step(self.extract_state(state))
                action = self.decode_action(action) 
            if self.human_mode:
                print('>> Agent {} plays {}'.format(player_id, action))
            state, player_id = self.game.step(action)

        if self.game.is_over():
            reward = self.get_payoffs()[self.active_player]
            done = True
            if self.human_mode:
                self.print_result(self.active_player)
            self.reset()

        elif self.human_mode:
            self.print_state(self.active_player)

        return self.extract_state(state), reward, done

    def reset(self):
        ''' Reset environment in single-agent mode
        '''
        if not self.single_agent_mode and not self.human_mode:
            raise ValueError('Reset can only be used in single-agent mode or human mode')

        if self.human_mode:
            history = []
        while True:
            state, player_id = self.game.init_game()
            while not player_id == self.active_player:
                self.timestep += 1
                if self.model.use_raw:
                    action = self.model.agents[player_id].eval_step(state)
                else:
                    action = self.model.agents[player_id].eval_step(self.extract_state(state))
                    action = self.decode_action(action) 
                if self.human_mode:
                    history.append((player_id, action))
                state, player_id = self.game.step(action)

            if not self.game.is_over():
                if self.human_mode:
                    print('\n>> Starting a new game!')
                    for player_id, action in history:
                        print('>> Agent {} plays {}'.format(player_id, action))
                    self.print_state(self.active_player)
                break
            else:
                if self.human_mode:
                    history.clear()

        return self.extract_state(state)

    def step_back(self):
        ''' Take one step backward.

        Returns:
            (tuple): Tuple containing:

                (numpy.array): The previous state
                (int): The ID of the previous player

        Note: Error will be raised if step back from the root node.
        '''
        if not self.allow_step_back:
            raise Exception('Step back is off. To use step_back, please set allow_step_back=True in rlcard.make')

        if not self.game.step_back():
            return False

        player_id = self.get_player_id()
        state = self.get_state(player_id)

        return state, player_id


    def get_player_id(self):
        ''' Get the current player id

        Returns:
            (int): the id of the current player
        '''
        return self.game.get_player_id()

    def is_over(self):
        ''' Check whether the curent game is over

        Returns:
            (boolean): True is current game is over
        '''
        return self.game.is_over()

    def get_state(self, player_id):
        ''' Get the state given player id

        Args:
            player_id (int): The player id

        Returns:
            (numpy.array): The observed state of the player
        '''
        return self.extract_state(self.game.get_state(player_id))

    def set_agents(self, agents):
        ''' Set the agents that will interact with the environment

        Args:
            agents (list): List of Agent classes
        '''
        if self.single_agent_mode or self.human_mode:
            raise ValueError('Setting agent in single agent mode or human mode is not allowed.')

        self.agents = agents

    def run(self, is_training=False, seed=None):
        ''' Run a complete game, either for evaluation or training RL agent.

        Args:
            is_training (boolean): True if for training purpose.
            seed (int): A seed for running the game. For single-process program,
              the seed should be set to None. For multi-process program, the
              seed should be asigned for reproducibility.

        Returns:
            (tuple) Tuple containing:

                (list): A list of trajectories generated from the environment.
                (list): A list payoffs. Each entry corresponds to one player.

        Note: The trajectories are 3-dimension list. The first dimension is for different players.
              The second dimension is for different transitions. The third dimension is for the contents of each transiton
        '''
        if self.single_agent_mode or self.human_mode:
            raise ValueError('Run in single agent mode or human mode is not allowed.')

        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

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

    def run_multi(self, task_num, result, is_training=False, seed=None):
        if seed is not None:
            np.random.seed(seed)
        for _ in range(task_num):
            result.append(self.run(is_training=is_training))

    def set_mode(self, active_player=0, single_agent_mode=False, human_mode=False):
        ''' Turn on the single-agent-mode. Pretrained models will
            be loaded to simulate other agents

        Args:
            active_player (int): The player that does not use pretrained models
        '''
        if not isinstance(active_player, int) or active_player < 0 or active_player >= self.player_num:
            raise ValueError('Active player should be a positiv integer less than the player number')

        if not single_agent_mode and not human_mode:
            raise ValueError('You must set single_agent_mode=True, or human_mode=True')

        if single_agent_mode and human_mode:
            raise ValueError('You can not set single_agentmode=True and human_mode=True together/')

        self.model = self.load_model()
        self.active_player = active_player
        self.single_agent_mode = single_agent_mode
        self.human_mode = human_mode

    def print_state(self, player):
        ''' Print out the state of a given player

        Args:
            player (int): Player id
        '''
        raise NotImplementedError

    def print_result(self, player):
        ''' Print the game result when the game is over

        Args:
            player (int): The human player id
        '''
        payoffs = self.get_payoffs()
        hands = [self.game.players[i].hand.get_index() for i in range(self.player_num)]
        public_card = self.game.public_card.get_index() if self.game.public_card else ''

        for i in range(self.player_num):
            print('>> Player {}: {} {}'.format(i, hands[i], public_card))

        if payoffs[player] > 0:
            print('>> You win {}!'.format(payoffs[player]))
        elif payoffs[player] == 0:
            print('>> You do not win/lose')
        else:
            print('>> You lose {}!'.format(-payoffs[player]))

    def load_model(self):
        ''' Load pretrained/rule model

        Returns:
            model (Model): A Model object
        '''
        raise NotImplementedError

    def extract_state(self, state):
        ''' Extract useful information from state for RL. Must be implemented in the child class.

        Args:
            state (dict): the raw state

        Returns:
            (numpy.array): the extracted state
        '''
        raise NotImplementedError

    def get_payoffs(self):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            (list): A list of payoffs for each player.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError

    def decode_action(self, action_id):
        ''' Decode Action id to the action in the game.

        Args:
            action_id (int): The id of the action

        Returns:
            (string): The action that will be passed to the game engine.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError

    def get_legal_actions(self):
        ''' Get all legal actions for current state.

        Returns:
            (list): A list of legal actions' id.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError
