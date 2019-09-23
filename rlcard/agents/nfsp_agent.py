# Copyright 2019 DATA Lab at Texas A&M University. All rights reserved.
# Copyright 2019 DeepMind Technologies Ltd. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

''' Neural Fictitious Self-Play (NFSP) agent implemented in TensorFlow.

See the paper https://arxiv.org/abs/1603.01121 for more details.
'''

import collections
import random
import enum
import numpy as np
import sonnet as snt
import tensorflow as tf

from rlcard.agents.dqn_agent import DQNAgent
from rlcard.utils.utils import *

Transition = collections.namedtuple('Transition', 'info_state action_probs')

MODE = enum.Enum('mode', 'best_response average_policy')

class NFSPAgent(object):
    ''' NFSP Agent implementation in TensorFlow.
    '''

    def __init__(self,
                 sess,
                 scope,
                 action_num=4,
                 state_shape=[52],
                 hidden_layers_sizes=None,
                 reservoir_buffer_capacity=int(1e6),
                 anticipatory_param=0.5,
                 batch_size=256,
                 rl_learning_rate=0.0001,
                 sl_learning_rate=0.00001,
                 min_buffer_size_to_learn=1000,
                 q_replay_memory_size=30000,
                 q_replay_memory_init_size=1000,
                 q_update_target_estimator_every=1000,
                 q_discount_factor=0.99,
                 q_epsilon_start=1,
                 q_epsilon_end=0.1,
                 q_epsilon_decay_steps=int(1e6),
                 q_batch_size=256,
                 q_norm_step=1000,
                 q_mlp_layers=None):
        ''' Initialize the NFSP agent.

        Args:
            sess (tf.Session): Tensorflow session object.
            scope (string): The name scope of NFSPAgent.
            action_num (int): The number of actions.
            state_shape (list): The shape of the state space.
            hidden_layers_sizes (list): The hidden layers sizes for the layers of 
              the average policy.
            reservoir_buffer_capacity (int): The size of the buffer for average policy.
            anticipatory_param (float): The hyper-parameter that balances rl/avarage policy.
            batch_size (int): The batch_size for training average policy.
            rl_learning_rate (float): The learning rate of the RL agent.
            sl_learning_rate (float): the learning rate of the average policy.
            min_buffer_size_to_learn (int): The minimum buffer size to learn for average policy.
            q_replay_memory_size (int): The memory size of inner DQN agent.
            q_replay_memory_init_size (int): The initial memory size of inner DQN agent.
            q_update_target_estimator_every (int): The frequency of updating target network for
              inner DQN agent.
            q_discount_factor (float): The discount factor of inner DQN agent.
            q_epsilon_start (float): The starting epsilon of inner DQN agent.
            q_epsilon_end (float): the end epsilon of inner DQN agent.
            q_epsilon_decay_steps (int): The decay steps of inner DQN agent.
            q_batch_size (int): The batch size of inner DQN agent.
            q_norm_step (int): The normalization steps of inner DQN agent.
            q_mlp_layers (list): The layer sizes of inner DQN agent.

        '''

        self._sess = sess
        self._action_num = action_num
        self._state_shape = state_shape
        self._layer_sizes = hidden_layers_sizes + [action_num]
        self._batch_size = batch_size
        self._sl_learning_rate = sl_learning_rate
        self._anticipatory_param = anticipatory_param
        self._min_buffer_size_to_learn = min_buffer_size_to_learn

        self._reservoir_buffer = ReservoirBuffer(reservoir_buffer_capacity)
        self._prev_timestep = None
        self._prev_action = None

        # Step counter to keep track of learning.
        self._step_counter = 0

        with tf.variable_scope(scope):
            # Inner RL agent
            self._rl_agent = DQNAgent(sess, 'dqn', q_replay_memory_size, q_replay_memory_init_size, q_update_target_estimator_every, q_discount_factor, q_epsilon_start, q_epsilon_end, q_epsilon_decay_steps, q_batch_size, action_num, state_shape, q_norm_step, q_mlp_layers, rl_learning_rate)

            # Build supervised model
            self._build_model()

        self.sample_episode_policy()

    def _build_model(self):
        ''' build the model for supervised learning
        '''

        # Placeholders.
        input_shape = [None]
        input_shape.extend(self._state_shape)
        self._info_state_ph = tf.placeholder(
                shape=input_shape,
                dtype=tf.float32)

        self._X = tf.contrib.layers.flatten(self._info_state_ph)

        self._action_probs_ph = tf.placeholder(
                shape=[None, self._action_num], dtype=tf.float32)

        # Average policy network.
        self._avg_network = snt.nets.MLP(output_sizes=self._layer_sizes)
        self._avg_policy = self._avg_network(self._X)
        self._avg_policy_probs = tf.nn.softmax(self._avg_policy)

        # Loss
        self._loss = tf.reduce_mean(
                tf.nn.softmax_cross_entropy_with_logits_v2(
                        labels=tf.stop_gradient(self._action_probs_ph),
                        logits=self._avg_policy))

        optimizer = tf.train.AdamOptimizer(learning_rate=self._sl_learning_rate)

        self._learn_step = optimizer.minimize(self._loss)


    def feed(self, ts):
        ''' Feed data to inner RL agent

        Args:
            ts (list): A list of 5 elements that represent the transition.
        '''

        self._rl_agent.feed(ts)

    def step(self, state):
        ''' Returns the action to be taken.

        Args:
            state (dict): The current state

        Returns:
            action (int): An action id
        '''

        obs = state['obs']
        legal_actions = state['legal_actions']
        if self._mode == MODE.best_response:
            probs = self._rl_agent.predict(obs)
            self._add_transition(obs, probs)

        elif self._mode == MODE.average_policy:
            probs = self._act(obs)

        probs = remove_illegal(probs, legal_actions)
        action = np.random.choice(len(probs), p=probs)

        return action

    def eval_step(self, state):
        ''' Use the average policy for evaluation purpose

        Args:
            state (dict): The current state.

        Returns:
            action (int): An action id.
        '''

        action = self._rl_agent.eval_step(state)

        return action

    def sample_episode_policy(self):
        ''' Sample average/best_response policy
        '''

        if np.random.rand() < self._anticipatory_param:
            self._mode = MODE.best_response
        else:
            self._mode = MODE.average_policy

    def _act(self, info_state):
        ''' Predict action probability givin the observation and legal actions

        Args:
            info_state (numpy.array): An obervation.

        Returns:
            action_probs (numpy.array): The predicted action probability.
        '''

        info_state = np.expand_dims(info_state, axis=0)
        action_probs = self._sess.run(
                self._avg_policy_probs,
                feed_dict={self._info_state_ph: info_state})[0]

        return action_probs

    def _add_transition(self, state, probs):
        ''' Adds the new transition to the reservoir buffer.

        Transitions are in the form (state, probs).

        Args:
            state (numpy.array): The state.
            probs (numpy.array): The probabilities of each action.
        '''

        #print(len(self._reservoir_buffer))
        transition = Transition(
                info_state=state,
                action_probs=probs)
        self._reservoir_buffer.add(transition)

    def train_rl(self):
        ''' Update the inner RL agent
        '''

        return self._rl_agent.train()

    def train_sl(self):
        ''' Compute the loss on sampled transitions and perform a avg-network update.

        If there are not enough elements in the buffer, no loss is computed and
        `None` is returned instead.

        Returns:
            loss (float): The average loss obtained on this batch of transitions or `None`.
        '''

        if (len(self._reservoir_buffer) < self._batch_size or
                len(self._reservoir_buffer) < self._min_buffer_size_to_learn):
            return None

        transitions = self._reservoir_buffer.sample(self._batch_size)
        info_states = [t.info_state for t in transitions]
        action_probs = [t.action_probs for t in transitions]

        loss, _ = self._sess.run(
                [self._loss, self._learn_step],
                feed_dict={
                        self._info_state_ph: info_states,
                        self._action_probs_ph: action_probs,
                })

        return loss

class ReservoirBuffer(object):
    ''' Allows uniform sampling over a stream of data.

    This class supports the storage of arbitrary elements, such as observation
    tensors, integer actions, etc.

    See https://en.wikipedia.org/wiki/Reservoir_sampling for more details.
    '''

    def __init__(self, reservoir_buffer_capacity):
        ''' Initialize the buffer.
        '''

        self._reservoir_buffer_capacity = reservoir_buffer_capacity
        self._data = []
        self._add_calls = 0

    def add(self, element):
        ''' Potentially adds `element` to the reservoir buffer.

        Args:
            element (object): data to be added to the reservoir buffer.
        '''

        if len(self._data) < self._reservoir_buffer_capacity:
            self._data.append(element)
        else:
            idx = np.random.randint(0, self._add_calls + 1)
            if idx < self._reservoir_buffer_capacity:
                self._data[idx] = element
        self._add_calls += 1

    def sample(self, num_samples):
        ''' Returns `num_samples` uniformly sampled from the buffer.

        Args:
            num_samples (int): The number of samples to draw.

        Returns:
            An iterable over `num_samples` random elements of the buffer.

        Raises:
            ValueError: If there are less than `num_samples` elements in the buffer
        '''

        if len(self._data) < num_samples:
            raise ValueError("{} elements could not be sampled from size {}".format(
                    num_samples, len(self._data)))
        return random.sample(self._data, num_samples)

    def clear(self):
        ''' Clear the buffer
        '''

        self._data = []
        self._add_calls = 0

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)
