from rlcard.utils import *

class Env(object):
    '''
    The base Env class. For all the environments in RLCard,
    we should base on this class and implement as many functions
    as we can.
    '''
    def __init__(self, config):
        ''' Initialize the environment

        Args:
            config (dict): A config dictionary. All the fields are
                optional. Currently, the dictionary includes:
                'seed' (int) - A environment local random seed.
                'allow_step_back' (boolean) - True if allowing
                 step_back.
                There can be some game specific configurations, e.g., the
                number of players in the game. These fields should start with
                'game_', e.g., 'game_num_players' which specify the number of
                players in the game. Since these configurations may be game-specific,
                The default settings should be put in the Env class. For example,
                the default game configurations for Blackjack should be in
                'rlcard/envs/blackjack.py'
                TODO: Support more game configurations in the future.
        '''
        self.allow_step_back = self.game.allow_step_back = config['allow_step_back']
        self.action_recorder = []

        # Game specific configurations
        # Currently only support blackjack、limit-holdem、no-limit-holdem
        # TODO support game configurations for all the games
        supported_envs = ['blackjack', 'leduc-holdem', 'limit-holdem', 'no-limit-holdem']
        if self.name in supported_envs:
            _game_config = self.default_game_config.copy()
            for key in config:
                if key in _game_config:
                    _game_config[key] = config[key]
            self.game.configure(_game_config)

        # Get the number of players/actions in this game
        self.num_players = self.game.get_num_players()
        self.num_actions = self.game.get_num_actions()

        # A counter for the timesteps
        self.timestep = 0

        # Set random seed, default is None
        self.seed(config['seed'])


    def reset(self):
        ''' Start a new game

        Returns:
            (tuple): Tuple containing:

                (numpy.array): The begining state of the game
                (int): The begining player
        '''
        state, player_id = self.game.init_game()
        self.action_recorder = []
        return self._extract_state(state), player_id

    def step(self, action, raw_action=False):
        ''' Step forward

        Args:
            action (int): The action taken by the current player
            raw_action (boolean): True if the action is a raw action

        Returns:
            (tuple): Tuple containing:

                (dict): The next state
                (int): The ID of the next player
        '''
        if not raw_action:
            action = self._decode_action(action)

        self.timestep += 1
        # Record the action for human interface
        self.action_recorder.append((self.get_player_id(), action))
        next_state, player_id = self.game.step(action)

        return self._extract_state(next_state), player_id

    def step_back(self):
        ''' Take one step backward.

        Returns:
            (tuple): Tuple containing:

                (dict): The previous state
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

    def set_agents(self, agents):
        '''
        Set the agents that will interact with the environment.
        This function must be called before `run`.

        Args:
            agents (list): List of Agent classes
        '''
        self.agents = agents

    def run(self, is_training=False):
        '''
        Run a complete game, either for evaluation or training RL agent.

        Args:
            is_training (boolean): True if for training purpose.

        Returns:
            (tuple) Tuple containing:

                (list): A list of trajectories generated from the environment.
                (list): A list payoffs. Each entry corresponds to one player.

        Note: The trajectories are 3-dimension list. The first dimension is for different players.
              The second dimension is for different transitions. The third dimension is for the contents of each transiton
        '''
        trajectories = [[] for _ in range(self.num_players)]
        state, player_id = self.reset()

        # Loop to play the game
        trajectories[player_id].append(state)
        while not self.is_over():
            # Agent plays
            if not is_training:
                action, _ = self.agents[player_id].eval_step(state)
            else:
                action = self.agents[player_id].step(state)

            # Environment steps
            next_state, next_player_id = self.step(action, self.agents[player_id].use_raw)
            # Save action
            trajectories[player_id].append(action)

            # Set the state and player
            state = next_state
            player_id = next_player_id

            # Save state.
            if not self.game.is_over():
                trajectories[player_id].append(state)

        # Add a final state to all the players
        for player_id in range(self.num_players):
            state = self.get_state(player_id)
            trajectories[player_id].append(state)

        # Payoffs
        payoffs = self.get_payoffs()

        return trajectories, payoffs

    def is_over(self):
        ''' Check whether the curent game is over

        Returns:
            (boolean): True if current game is over
        '''
        return self.game.is_over()

    def get_player_id(self):
        ''' Get the current player id

        Returns:
            (int): The id of the current player
        '''
        return self.game.get_player_id()


    def get_state(self, player_id):
        ''' Get the state given player id

        Args:
            player_id (int): The player id

        Returns:
            (numpy.array): The observed state of the player
        '''
        return self._extract_state(self.game.get_state(player_id))

    def get_payoffs(self):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            (list): A list of payoffs for each player.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError

    def get_perfect_information(self):
        ''' Get the perfect information of the current state

        Returns:
            (dict): A dictionary of all the perfect information of the current state
        '''
        raise NotImplementedError

    def get_action_feature(self, action):
        ''' For some environments such as DouDizhu, we can have action features

        Returns:
            (numpy.array): The action features
        '''
        # By default we use one-hot encoding
        feature = np.zeros(self.num_actions, dtype=np.int8)
        feature[action] = 1
        return feature

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        self.game.np_random = self.np_random
        return seed

    def _extract_state(self, state):
        ''' Extract useful information from state for RL. Must be implemented in the child class.

        Args:
            state (dict): The raw state

        Returns:
            (numpy.array): The extracted state
        '''
        raise NotImplementedError

    def _decode_action(self, action_id):
        ''' Decode Action id to the action in the game.

        Args:
            action_id (int): The id of the action

        Returns:
            (string): The action that will be passed to the game engine.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError

    def _get_legal_actions(self):
        ''' Get all legal actions for current state.

        Returns:
            (list): A list of legal actions' id.

        Note: Must be implemented in the child class.
        '''
        raise NotImplementedError
