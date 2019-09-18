# Copyright 2019 DATA Lab at Texas A&M University All rights reserved.
# Copyright 2019 DeepMind Technologies Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Implements Deep CFR Algorithm.

The implementation is derived from:
    https://github.com/deepmind/open_spiel/blob/master/open_spiel/python/algorithms/deep_cfr.py

We modify the structure for single player game and rlcard package, and fix some bugs for loss calculation.

See https://arxiv.org/abs/1811.00164.

The algorithm defines an `advantage` and `strategy` networks that compute
advantages used to do regret matching across information sets and to approximate
the strategy profiles of the game.    To train these networks a fixed ring buffer
(other data structures may be used) memory is used to accumulate samples to
train the networks.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import math
import random
import numpy as np
import tensorflow as tf
import sonnet as snt
import rlcard
from rlcard.utils.utils import *

AdvantageMemory = collections.namedtuple(
    "AdvantageMemory", "info_state iteration advantage action")

StrategyMemory = collections.namedtuple(
    "StrategyMemory", "info_state iteration strategy_action_probs")

class FixedSizeRingBuffer(object):
    """ReplayBuffer of fixed size with a FIFO replacement policy.

    Stored transitions can be sampled uniformly.

    The underlying datastructure is a ring buffer, allowing 0(1) adding and
    sampling.
    """

    def __init__(self, replay_buffer_capacity):
        self._replay_buffer_capacity = replay_buffer_capacity
        self._data = []
        self._next_entry_index = 0

    def add(self, element):
        '''Adds `element` to the buffer.

        If the buffer is full, the oldest element will be replaced.

        Args:
            element: data to be added to the buffer.
        '''
        if len(self._data) < self._replay_buffer_capacity:
            self._data.append(element)
        else:
            self._next_entry_index = int(self._next_entry_index)
            self._data[self._next_entry_index] = element
            self._next_entry_index += 1
            self._next_entry_index %= self._replay_buffer_capacity

    def sample(self, num_samples):
        '''Returns `num_samples` uniformly sampled from the buffer.

        Args:
            num_samples (int): number of samples to draw.

        Returns:
            sample data (list): a list of random sampled elements of the buffer

        Raises:
            ValueError: If there are less than `num_samples` elements in the buffer
        '''
        if len(self._data) < num_samples:
            raise ValueError("{} elements could not be sampled from size {}".format(
                num_samples, len(self._data)))
        return random.sample(self._data, num_samples)

    def clear(self):
        self._data = []
        self._next_entry_index = 0

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)


class DeepCFR():
    '''Implements a solver for the Deep CFR Algorithm.

    See https://arxiv.org/abs/1811.00164.

    Define all networks and sampling buffers/memories.    Derive losses & learning
    steps. Initialize the game state and algorithmic variables.

    Note: batch sizes default to `None` implying that training over the full
        dataset in memory is done by default.    To sample from the memories you
        may set these values to something less than the full capacity of the
        memory.
    '''

    def __init__(self,
             session,
             env,
             policy_network_layers=(32, 32),
             advantage_network_layers=(32, 32),
             num_traversals=10,
             num_step=40,
             learning_rate=1e-4,
             batch_size_advantage=16,
             batch_size_strategy=16,
             memory_capacity=int(1e7)):
        ''' Initialize the Deep CFR

        Args:
            session (tf.Session): TensorFlow session
            env (rlcard.env): for training (traverse) 
            policy_network_layers (list[int]): Layer sizes of strategy net MLP
            advantage_network_layers (list[int]): Layer sizes of advantage net MLP
            num_traversals (int): Number of traversals per step 
            learning_rate (float): Learning rate
            batch_size_advantage (int or None): Batch size to sample from advantage
            memories
            batch_size_strategy (int or None): Batch size to sample from strategy
            memories
            memory_capacity (int): Number af samples that can be stored in memory
        '''
        all_players = list(range(env.player_num))
        self._env = env
        self._session = session
        self._batch_size_advantage = batch_size_advantage
        self._batch_size_strategy = batch_size_strategy
        self._num_players = env.player_num
        self._num_step = num_step
        self.advantage_losses = collections.defaultdict(list)

        # get initial state and players
        init_state, player = self._env.init_game()

        self._embedding_size = init_state.shape
        self._num_traversals = num_traversals
        self._num_actions = self._env.action_num
        self._iteration = 1
        self._traverse_count = 0

        info_state_shape = [None]
        info_state_shape.extend(self._embedding_size)
        # Create required TensorFlow placeholders to perform the Q-network updates.
        self._info_state_ph = tf.placeholder(
            #shape=[None, self._embedding_size],
            shape=info_state_shape,
            dtype=tf.float32,
            name="info_state_ph")
        self._info_state_ph = self._flatten_state(self._info_state_ph)
        self._action_probs_ph = tf.placeholder(
            shape=[None, self._num_actions],
            dtype=tf.float32,
            name="action_probs_ph")
        self._iter_ph = tf.placeholder(
            shape=[None, 1], dtype=tf.float32, name="iter_ph")
        self._advantage_ph = []
        for p in range(self._num_players):
            self._advantage_ph.append(
                tf.placeholder(
                    shape=[None, self._num_actions],
                    dtype=tf.float32,
                    name="advantage_ph_" + str(p)))

        # Define strategy network, loss & memory.
        self._strategy_memories = FixedSizeRingBuffer(memory_capacity)

        self._policy_network = snt.nets.MLP(
            list(policy_network_layers) + [self._num_actions])

        action_logits = self._policy_network(self._info_state_ph)

        # Illegal actions are handled in the traversal code where expected payoff
        # and sampled regret is computed from the advantage networks.
        self._action_probs = tf.nn.softmax(action_logits)
        self._loss_policy = tf.reduce_mean(
                tf.losses.mean_squared_error(
                labels=tf.math.sqrt(self._iter_ph) * self._action_probs_ph,
                predictions=tf.math.sqrt(self._iter_ph) * self._action_probs))
        self._optimizer_policy = tf.train.AdamOptimizer(learning_rate=learning_rate)
        self._learn_step_policy = self._optimizer_policy.minimize(self._loss_policy)

        # Define advantage network, loss & memory. (One per player)
        self._advantage_memories = [
            FixedSizeRingBuffer(memory_capacity) for _ in range(self._num_players)
        ]
        self._advantage_networks = [
            snt.nets.MLP(list(advantage_network_layers) + [self._num_actions])
            for _ in range(self._num_players)
        ]
        self._advantage_outputs = [
            self._advantage_networks[i](self._info_state_ph)
            for i in range(self._num_players)
        ]
        self._loss_advantages = []
        self._optimizer_advantages = []
        self._learn_step_advantages = []
        for p in range(self._num_players):
            self._loss_advantages.append(
                tf.reduce_mean(
                        tf.losses.mean_squared_error(
                        labels=tf.math.sqrt(self._iter_ph) * self._advantage_ph[p],
                        predictions=tf.math.sqrt(self._iter_ph) * self._advantage_outputs[p])))
            self._optimizer_advantages.append(
                        tf.train.AdamOptimizer(learning_rate=learning_rate))
            self._learn_step_advantages.append(self._optimizer_advantages[p].minimize(
                        self._loss_advantages[p]))
        # Initialize all parameters in tensorflow
        self._session.run(tf.global_variables_initializer())

    def reinitialize_advantage_networks(self):
        ''' Reinitialize the advantage networks
        '''
        for p in range(self._num_players):
            for key in self._advantage_networks[p].initializers:
                self._advantage_networks[p].initializers[key]()

    def step(self, state):
        ''' Predict the action for generating training data

        Args:
            state (dict): current state
        Returns:
            action (int): an action id
        '''
        action_prob = self.action_probabilities(state)
        action_prob /= action_prob.sum()
        action = np.random.choice(np.arange(len(action_prob)), p=action_prob)
        return action

    def train(self):
        ''' Perform tree traversal and train the network

        Returns:
            policy_network (tf.placeholder): the trained policy network
            average advantage loss (float): players average advantage loss
            policy loss (float): policy loss
        '''
        init_state, player = self._env.init_game()
        self._root_node = init_state.flatten()
        for p in range(self._num_players):
            for _ in range(self._num_traversals):
                self._traverse_game_tree(self._root_node, p)
            # Re-initialize advantage networks and train from scratch.
            self.reinitialize_advantage_networks()
            for i in range(self._num_step):
                self.advantage_losses[p].append(self._learn_advantage_network(p))
            self._iteration += 1

        # Train policy network.
        for i in range(self._num_step):
            policy_loss = self._learn_strategy_network()
        avg_adv_loss = sum([self.advantage_losses[p][-1] for p in self.advantage_losses.keys()]) / self._num_players / self._num_step
        return self._policy_network, avg_adv_loss, policy_loss

    def _traverse_game_tree(self, state, player, count = 0):
        '''Performs a traversal of the game tree.

        Over a traversal the advantage and strategy memories are populated with
        computed advantage values and matched regrets respectively.

        Args:
            state (dict): Current rlcard game state.
            player (int): Player index for this traversal.

        Returns:
            payoff (list): Recursively returns expected payoffs for each action.
        '''
        expected_payoff = collections.defaultdict(float)
        current_player = self._env.get_player_id()
        actions = self._env.get_legal_actions()

        if self._env.is_over():
            # Terminal state get returns.
            payoff = self._env.get_payoffs()
            prev_state, _ = self._env.step_back()
            return payoff 

        if current_player == player:
            sampled_regret = collections.defaultdict(float)
            # Update the policy over the info set & actions via regret matching.
            advantages, strategy = self._sample_action_from_advantage(state, player)
            for action in actions:
                child_state, _ = self._env.step(action)
                child_state = child_state.flatten()
                expected_payoff[action] = self._traverse_game_tree(child_state, player)
            self._env.step_back()

            for action in actions:
                sampled_regret[action] = expected_payoff[action][0]
                for a_ in actions:
                    sampled_regret[action] -= strategy[a_] * expected_payoff[a_][0]
                regret = np.array([sampled_regret[act] for act in actions])
                self._advantage_memories[player].add(AdvantageMemory(state, self._iteration, regret, action))
            if self._num_players == 1:
                self._strategy_memories.add(StrategyMemory(state, self._iteration, strategy))
            return max(expected_payoff.values())
        else:
            other_player = current_player
            _, strategy = self._sample_action_from_advantage(state, other_player)
            # Recompute distribution dor numerical errors.
            probs = np.array(strategy)
            probs /= probs.sum()
            sampled_action = np.random.choice(range(self._num_actions), p=probs)
            self._strategy_memories.add(
                StrategyMemory(
                    state,
                    self._iteration, strategy))
            return self._traverse_game_tree(self._env.get_child_state(action), player)

    def _sample_action_from_advantage(self, state, player):
        '''Returns an info state policy by applying regret-matching.

        Args:
            state (dict): Current state.
            player (int): Player index over which to compute regrets.

        Returns:
            1. (list) Advantage values for info state actions indexed by action.
            2. (list) Matched regrets, prob for actions indexed by action.
        '''
        info_state = state.flatten() 
        legal_actions = self._env.get_legal_actions() 
        advantages = self._session.run(
            self._advantage_outputs[player],
            feed_dict={self._info_state_ph: np.expand_dims(info_state, axis=0)})[0]
        advantages = [max(0., advantage) for advantage in advantages]
        cumulative_regret = np.sum([advantages[action] for action in legal_actions])
        matched_regrets = np.array([0.] * self._num_actions)
        for action in legal_actions:
            if cumulative_regret > 0.:
                matched_regrets[action] = advantages[action] / cumulative_regret
            else:
                matched_regrets[action] = 1 / self._num_actions
        return advantages, matched_regrets

    def action_advantage(self, state, player):
        state = state.flatten()
        advantages = self._session.run(
            self._advantage_outputs[player],
            feed_dict={self._info_state_ph: np.expand_dims(state, axis=0)})[0]
        advantages = np.array([max(0., advantage) for advantage in advantages])
        return advantages

    def _flatten_state(self, state):
        shape = state.get_shape().as_list()     
        dim = np.prod(shape[1:])            
        flattened = tf.reshape(state, [-1, dim])
        return flattened

    def action_probabilities(self, state):
        '''Returns action probabilites dict for a single batch.
        '''
        info_state_vector = state.flatten()

        if len(info_state_vector.shape) == 1:
            info_state_vector = np.expand_dims(info_state_vector, axis=0)

        probs = self._session.run(
            self._action_probs, feed_dict={self._info_state_ph: info_state_vector})

        return np.array([round(probs[0][i], 4) for i in range(self._num_actions)])

    def _learn_advantage_network(self, player):
        '''Compute the loss on sampled transitions and perform a Q-network update.

        If there are not enough elements in the buffer, no loss is computed and
        `None` is returned instead.

        Args:
            player (int): player id

        Returns:
            loss advantages (float): The average loss over the advantage network.
        '''
        if self._batch_size_advantage and self._batch_size_advantage < self._advantage_memories[player]._next_entry_index:
            samples = self._advantage_memories[player].sample(self._batch_size_advantage)
        else:
            samples = self._advantage_memories[player]
        info_states = []
        advantages = []
        iterations = []
        for s in samples:
            #print(s.info_state, s.action, s.advantage)
            info_states.append(s.info_state)
            advantages.append(s.advantage)
            iterations.append([s.iteration])

        if info_states == []:
            return None
        
        # Ensure some samples have been gathered.
        loss_advantages, _ = self._session.run(
            [self._loss_advantages[player], self._learn_step_advantages[player]],
            feed_dict={
                self._info_state_ph: np.array(info_states),
                self._advantage_ph[player]: np.array(advantages),
                self._iter_ph: np.array(iterations),
            })
        return loss_advantages

    def _learn_strategy_network(self):
        """Compute the loss over the strategy network.

        Returns:
            The average loss obtained on this batch of transitions or `None`.
        """
        if self._batch_size_strategy and self._batch_size_strategy < self._strategy_memories._next_entry_index:
            samples = self._strategy_memories.sample(self._batch_size_strategy)
        else:
            samples = self._strategy_memories
        info_states = []
        action_probs = []
        iterations = []
        for s in samples:
            info_states.append(s.info_state)
            action_probs.append(s.strategy_action_probs)
            iterations.append([s.iteration])
        if info_states == []:
            return None
        loss_strategy, _ = self._session.run(
            [self._loss_policy, self._learn_step_policy],
            feed_dict={
                self._info_state_ph: np.array(info_states),
                self._action_probs_ph: np.array(np.squeeze(action_probs)),
                self._iter_ph: np.array(iterations),
            })
        return loss_strategy
