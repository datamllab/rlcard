import random
import numpy as np
import json
from rlcard.games.doudizhu import *
from rlcard.envs.env import Env
from rlcard.games.doudizhu.game import DoudizhuGame as Game
from rlcard.utils.utils import *
with open('rlcard/games/doudizhu/specific_map.json', 'r') as file:
    SPECIFIC_MAP = json.load(file)
with open('rlcard/games/doudizhu/action_space.json', 'r') as file:
    ACTION_SPACE = list(json.load(file).keys())


class DoudizhuEnv(Env):
    """
    Doudizhu Environment
    """

    def __init__(self):
        super().__init__(Game())

    def extract_state(self, state):
        """Encode state

        Args:
            state (dict): dict of original state

        Returns:
            numpy array: 6×60 array
                         60: 4 suits cards of 15 ranks from 3 to red joker
                         6 : current player's cards
                             union other players' cards
                             recent three actions
                             union of played cards
        """

        def add_cards(array, cards):
            suit = 0
            for index, card in enumerate(cards):
                if index != 0 and card == cards[index-1]:
                    suit += 1
                else:
                    suit = 0
                rank = Game.card_rank.index(card)
                array[rank+suit*15] += 1

        encoded_state = np.zeros((6, 60), dtype=int)
        add_cards(encoded_state[0], state['remaining'])
        add_cards(encoded_state[1], state['cards_others'])
        for i, action in enumerate(state['trace'][-3:]):
            if action[1] != 'pass':
                add_cards(encoded_state[4-i], action[1])
        if state['cards_played'] is not None:
            add_cards(encoded_state[5], state['cards_played'])
        return encoded_state

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
                action = self.agents[0].eval_step(state)
            else:
                action = self.agents[0].step(state)

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

    def reorganize(self, trajectories):
        """
                A simple function to add reward to the trajectories.
                The reward is only given in the end of a game,
                i.e. 1 if winning and 0 otherwise
        """
        # the wiiner of the game
        player_wins = [self.game.is_winner(p) for p in range(self.player_num)]
        # print('######## ', player_wins)
        new_trajectories = [[] for _ in range(self.player_num)]

        for player in range(self.player_num):
            for i in range(0, len(trajectories[player])-2, 2):
                transition = trajectories[player][i:i+3].copy()\

                # Reward. Here, I simply reward at the end of the game
                # TODO: use better rewarder later
                # if i < len(trajectories[player]) - 3:
                #	reward = self.rewarder.get_reward(0)
                # else:
                #	reward = self.rewarder.get_reward(player_wins[player])

                # transition.append(reward)
                new_trajectories[player].append(transition)
        return new_trajectories

    def get_payoffs(self):
        return self.game.game_result

    def decode_action(self, action_id):
        abstract_action = ACTION_SPACE[action_id]
        legal_actions = self.game.state['actions']
        specific_actions = []
        for legal_action in legal_actions:
            for abstract in SPECIFIC_MAP[legal_action]:
                if abstract == abstract_action:
                    specific_actions.append(legal_action)
        if len(specific_actions) > 0:
            return random.choice(specific_actions)
        return random.choice(legal_actions)
