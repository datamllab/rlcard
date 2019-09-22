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

"""Neural Fictitious Self-Play (NFSP) agent implemented in TensorFlow.

See the paper https://arxiv.org/abs/1603.01121 for more details.
"""

import collections
import random
import enum
import numpy as np
import sonnet as snt
import tensorflow as tf

from rlcard.agents.dqn_agent import DQNAgent

Transition = collections.namedtuple("Transition", "info_state action_probs")

MODE = enum.Enum("mode", "best_response average_policy")

class NFSPAgent(object):
    """NFSP Agent implementation in TensorFlow.

    See open_spiel/python/examples/nfsp.py for an usage example.
    """

    def __init__(self,
                 sess,
                 action_num=4,
                 state_shape=[52],
                 hidden_layers_sizes=None,
                 reservoir_buffer_capacity=int(3e7),
                 anticipatory_param=0.1,
                 batch_size=256,
                 rl_learning_rate=0.01,
                 sl_learning_rate=0.01,
                 min_buffer_size_to_learn=1000,
                 optimizer_str="adam",
                 q_replay_memory_size=int(2e6),
                 q_replay_memory_init_size=1000,
                 q_update_target_estimator_every=1000,
                 q_discount_factor=1.0,
                 q_epsilon_start=0.08,
                 q_epsilon_end=0.0,
                 q_epsilon_decay_steps=int(1e7),
                 q_batch_size=256,
                 q_norm_step=100,
                 q_mlp_layers=None):
        ''' Initialize the NFSP agent.
        '''

        self._sess = sess
        self._action_num = action_num
        self._state_shape = state_shape
        self._layer_sizes = hidden_layers_sizes + [action_num]
        self._batch_size = batch_size
        self._sl_learning_rate = sl_learning_rate
        self._anticipatory_param = anticipatory_param
        self._min_buffer_size_to_learn = min_buffer_size_to_learn
        self._optimizer_str = optimizer_str

        self._reservoir_buffer = ReservoirBuffer(reservoir_buffer_capacity)
        self._prev_timestep = None
        self._prev_action = None

        # Step counter to keep track of learning.
        self._step_counter = 0

        # Inner RL agent
        self._rl_agent = DQNAgent(sess, q_replay_memory_size, q_replay_memory_init_size, q_update_target_estimator_every, q_discount_factor, q_epsilon_start, q_epsilon_end, q_epsilon_decay_steps, q_batch_size, action_num, state_shape, q_norm_step, q_mlp_layers, rl_learning_rate)

        # Build supervised model
        self.build_model()
        self.sample_episode_policy()

        sess.run(tf.global_variables_initializer())


    def build_model(self):
        ''' build the model for supervised learning
        '''

        # Placeholders.
        input_shape = [None]
        input_shape.extend(self._state_shape)
        self._info_state_ph = tf.placeholder(
                shape=input_shape,
                dtype=tf.float32,
                name="info_state_ph")

        self._action_probs_ph = tf.placeholder(
                shape=[None, self._action_num], dtype=tf.float32, name="action_probs_ph")

        # Average policy network.
        self._avg_network = snt.nets.MLP(output_sizes=self._layer_sizes)
        self._avg_policy = self._avg_network(self._info_state_ph)
        self._avg_policy_probs = tf.nn.softmax(self._avg_policy)

        # Loss
        self._loss = tf.reduce_mean(
                tf.nn.softmax_cross_entropy_with_logits_v2(
                        labels=tf.stop_gradient(self._action_probs_ph),
                        logits=self._avg_policy))

        if self._optimizer_str == "adam":
            optimizer = tf.train.AdamOptimizer(learning_rate=self._sl_learning_rate)
        elif self._optimizer_str == "sgd":
            optimizer = tf.train.GradientDescentOptimizer(
                    learning_rate=self._sl_learning_rate)
        else:
            raise ValueError("Not implemented. Choose from ['adam', 'sgd'].")

        self._learn_step = optimizer.minimize(self._loss)


    def feed(self, ts):
        self._rl_agent.feed(ts)


    def step(self, state):
        """Returns the action to be taken.

        Args:
            state (dict): the current state

        Returns:
            action (int): an action id
        """

        obs = state['obs']
        legal_actions = state['legal_actions']
        if self._mode == MODE.best_response:
            probs = self._rl_agent.predict(obs)
            self._add_transition(obs, probs)

        elif self._mode == MODE.average_policy:
            probs = self._act(obs, legal_actions)

        probs = self._remove_illegal(probs, legal_actions)
        action = np.random.choice(len(probs), p=probs)

        return action

    def eval_step(self, state):
        ''' Use the average policy for evaluation purpose
        '''

        previous_mode = self._mode
        self._mode = MODE.average_policy
        action = self.step(state)
        self._mode = previous_mode

        return action

    def sample_episode_policy(self):
        if np.random.rand() < self._anticipatory_param:
            self._mode = MODE.best_response
        else:
            self._mode = MODE.average_policy

    def _act(self, info_state, legal_actions):
        info_state = np.reshape(info_state, [1, -1])
        action_probs = self._sess.run(
                self._avg_policy_probs,
                feed_dict={self._info_state_ph: info_state})[0]

        return action_probs

    def _remove_illegal(self,action_probs, legal_actions):
        probs = np.zeros(self._action_num)
        probs[legal_actions] = action_probs[legal_actions]
        probs /= sum(probs)
        return probs

    @property
    def mode(self):
        return self._mode

    @property
    def loss(self):
        return (self._last_sl_loss_value, self._last_rl_loss_value())


    def _add_transition(self, state, probs):
        """Adds the new transition using `time_step` to the reservoir buffer.

        Transitions are in the form (time_step, agent_output.probs, legal_mask).

        Args:
            time_step: an instance of rl_environment.TimeStep.
            agent_output: an instance of rl_agent.StepOutput.
        """
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
            The average loss obtained on this batch of transitions or `None`.
        '''

        if (len(self._reservoir_buffer) < self._batch_size or
                len(self._reservoir_buffer) < self._min_buffer_size_to_learn):
            #print(len(self._reservoir_buffer))
            return None

        transitions = self._reservoir_buffer.sample(self._batch_size)
        info_states = [t.info_state for t in transitions]
        action_probs = [t.action_probs for t in transitions]

        #print(info_states, action_probs)

        loss, _ = self._sess.run(
                [self._loss, self._learn_step],
                feed_dict={
                        self._info_state_ph: info_states,
                        self._action_probs_ph: action_probs,
                })

        #print(loss)
        return loss


class ReservoirBuffer(object):
    """Allows uniform sampling over a stream of data.

    This class supports the storage of arbitrary elements, such as observation
    tensors, integer actions, etc.

    See https://en.wikipedia.org/wiki/Reservoir_sampling for more details.
    """

    def __init__(self, reservoir_buffer_capacity):
        self._reservoir_buffer_capacity = reservoir_buffer_capacity
        self._data = []
        self._add_calls = 0

    def add(self, element):
        """Potentially adds `element` to the reservoir buffer.

        Args:
            element: data to be added to the reservoir buffer.
        """
        if len(self._data) < self._reservoir_buffer_capacity:
            self._data.append(element)
        else:
            idx = np.random.randint(0, self._add_calls + 1)
            if idx < self._reservoir_buffer_capacity:
                self._data[idx] = element
        self._add_calls += 1

    def sample(self, num_samples):
        """Returns `num_samples` uniformly sampled from the buffer.

        Args:
            num_samples: `int`, number of samples to draw.

        Returns:
            An iterable over `num_samples` random elements of the buffer.

        Raises:
            ValueError: If there are less than `num_samples` elements in the buffer
        """
        if len(self._data) < num_samples:
            raise ValueError("{} elements could not be sampled from size {}".format(
                    num_samples, len(self._data)))
        return random.sample(self._data, num_samples)

    def clear(self):
        self._data = []
        self._add_calls = 0

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)
