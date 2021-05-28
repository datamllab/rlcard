# Copyright 2019 Matthew Judell. All rights reserved.
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

import random
import collections
import enum
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from rlcard.agents.dqn_agent import DQNAgent
from rlcard.utils.utils import remove_illegal

Transition = collections.namedtuple('Transition', 'info_state action_probs')

class NFSPAgent(object):
    ''' An approximate clone of rlcard.agents.nfsp_agent that uses
    pytorch instead of tensorflow.  Note that this implementation
    differs from Henrich and Silver (2016) in that the supervised
    training minimizes cross-entropy with respect to the stored
    action probabilities rather than the realized actions.
    '''

    def __init__(self,
                 num_actions=4,
                 state_shape=None,
                 hidden_layers_sizes=None,
                 reservoir_buffer_capacity=20000,
                 anticipatory_param=0.1,
                 batch_size=256,
                 train_every=1,
                 rl_learning_rate=0.1,
                 sl_learning_rate=0.005,
                 min_buffer_size_to_learn=100,
                 q_replay_memory_size=20000,
                 q_replay_memory_init_size=100,
                 q_update_target_estimator_every=1000,
                 q_discount_factor=0.99,
                 q_epsilon_start=0.06,
                 q_epsilon_end=0,
                 q_epsilon_decay_steps=int(1e6),
                 q_batch_size=32,
                 q_train_every=1,
                 q_mlp_layers=None,
                 evaluate_with='average_policy',
                 device=None):
        ''' Initialize the NFSP agent.

        Args:
            num_actions (int): The number of actions.
            state_shape (list): The shape of the state space.
            hidden_layers_sizes (list): The hidden layers sizes for the layers of
              the average policy.
            reservoir_buffer_capacity (int): The size of the buffer for average policy.
            anticipatory_param (float): The hyper-parameter that balances rl/avarage policy.
            batch_size (int): The batch_size for training average policy.
            train_every (int): Train the SL policy every X steps.
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
            q_train_step (int): Train the model every X steps.
            q_mlp_layers (list): The layer sizes of inner DQN agent.
            device (torch.device): Whether to use the cpu or gpu
        '''
        self.use_raw = False
        self._num_actions = num_actions
        self._state_shape = state_shape
        self._layer_sizes = hidden_layers_sizes + [num_actions]
        self._batch_size = batch_size
        self._train_every = train_every
        self._sl_learning_rate = sl_learning_rate
        self._anticipatory_param = anticipatory_param
        self._min_buffer_size_to_learn = min_buffer_size_to_learn

        self._reservoir_buffer = ReservoirBuffer(reservoir_buffer_capacity)
        self._prev_timestep = None
        self._prev_action = None
        self.evaluate_with = evaluate_with

        if device is None:
            self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = device

        # Total timesteps
        self.total_t = 0

        # Step counter to keep track of learning.
        self._step_counter = 0

        # Build the action-value network
        self._rl_agent = DQNAgent(q_replay_memory_size, q_replay_memory_init_size, \
            q_update_target_estimator_every, q_discount_factor, q_epsilon_start, q_epsilon_end, \
            q_epsilon_decay_steps, q_batch_size, num_actions, state_shape, q_train_every, q_mlp_layers, \
            rl_learning_rate, device)

        # Build the average policy supervised model
        self._build_model()

        self.sample_episode_policy()

    def _build_model(self):
        ''' Build the average policy network
        '''

        # configure the average policy network
        policy_network = AveragePolicyNetwork(self._num_actions, self._state_shape, self._layer_sizes)
        policy_network = policy_network.to(self.device)
        self.policy_network = policy_network
        self.policy_network.eval()

        # xavier init
        for p in self.policy_network.parameters():
            if len(p.data.shape) > 1:
                nn.init.xavier_uniform_(p.data)

        # configure optimizer
        self.policy_network_optimizer = torch.optim.Adam(self.policy_network.parameters(), lr=self._sl_learning_rate)

    def feed(self, ts):
        ''' Feed data to inner RL agent

        Args:
            ts (list): A list of 5 elements that represent the transition.
        '''
        self._rl_agent.feed(ts)
        self.total_t += 1
        if self.total_t>0 and len(self._reservoir_buffer) >= self._min_buffer_size_to_learn and self.total_t%self._train_every == 0:
            sl_loss  = self.train_sl()
            print('\rINFO - Step {}, sl-loss: {}'.format(self.total_t, sl_loss), end='')

    def step(self, state):
        ''' Returns the action to be taken.

        Args:
            state (dict): The current state

        Returns:
            action (int): An action id
        '''
        obs = state['obs']
        legal_actions = list(state['legal_actions'].keys())
        if self._mode == 'best_response':
            action = self._rl_agent.step(state)
            one_hot = np.zeros(self._num_actions)
            one_hot[action] = 1
            self._add_transition(obs, one_hot)

        elif self._mode == 'average_policy':
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
            info (dict): A dictionary containing information
        '''
        if self.evaluate_with == 'best_response':
            action, info = self._rl_agent.eval_step(state)
        elif self.evaluate_with == 'average_policy':
            obs = state['obs']
            legal_actions = list(state['legal_actions'].keys())
            probs = self._act(obs)
            probs = remove_illegal(probs, legal_actions)
            action = np.random.choice(len(probs), p=probs)
            info = {}
            info['probs'] = {state['raw_legal_actions'][i]: float(probs[list(state['legal_actions'].keys())[i]]) for i in range(len(state['legal_actions']))}
        else:
            raise ValueError("'evaluate_with' should be either 'average_policy' or 'best_response'.")
        return action, info

    def sample_episode_policy(self):
        ''' Sample average/best_response policy
        '''
        if np.random.rand() < self._anticipatory_param:
            self._mode = 'best_response'
        else:
            self._mode = 'average_policy'

    def _act(self, info_state):
        ''' Predict action probability givin the observation and legal actions
            Not connected to computation graph
        Args:
            info_state (numpy.array): An obervation.

        Returns:
            action_probs (numpy.array): The predicted action probability.
        '''
        info_state = np.expand_dims(info_state, axis=0)
        info_state = torch.from_numpy(info_state).float().to(self.device)

        with torch.no_grad():
            log_action_probs = self.policy_network(info_state).cpu().numpy()

        action_probs = np.exp(log_action_probs)[0]

        return action_probs

    def _add_transition(self, state, probs):
        ''' Adds the new transition to the reservoir buffer.

        Transitions are in the form (state, probs).

        Args:
            state (numpy.array): The state.
            probs (numpy.array): The probabilities of each action.
        '''
        transition = Transition(
                info_state=state,
                action_probs=probs)
        self._reservoir_buffer.add(transition)

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

        self.policy_network_optimizer.zero_grad()
        self.policy_network.train()

        # (batch, state_size)
        info_states = torch.from_numpy(np.array(info_states)).float().to(self.device)

        # (batch, num_actions)
        eval_action_probs = torch.from_numpy(np.array(action_probs)).float().to(self.device)

        # (batch, num_actions)
        log_forecast_action_probs = self.policy_network(info_states)

        ce_loss = - (eval_action_probs * log_forecast_action_probs).sum(dim=-1).mean()
        ce_loss.backward()

        self.policy_network_optimizer.step()
        ce_loss = ce_loss.item()
        self.policy_network.eval()

        return ce_loss

    def set_device(self, device):
        self.device = device
        self._rl_agent.set_device(device)

class AveragePolicyNetwork(nn.Module):
    '''
    Approximates the history of action probabilities
    given state (average policy). Forward pass returns
    log probabilities of actions.
    '''

    def __init__(self, num_actions=2, state_shape=None, mlp_layers=None):
        ''' Initialize the policy network.  It's just a bunch of ReLU
        layers with no activation on the final one, initialized with
        Xavier (sonnet.nets.MLP and tensorflow defaults)

        Args:
            num_actions (int): number of output actions
            state_shape (list): shape of state tensor for each sample
            mlp_laters (list): output size of each mlp layer including final
        '''
        super(AveragePolicyNetwork, self).__init__()

        self.num_actions = num_actions
        self.state_shape = state_shape
        self.mlp_layers = mlp_layers

        # set up mlp w/ relu activations
        layer_dims = [np.prod(self.state_shape)] + self.mlp_layers
        mlp = [nn.Flatten()]
        mlp.append(nn.BatchNorm1d(layer_dims[0]))
        for i in range(len(layer_dims)-1):
            mlp.append(nn.Linear(layer_dims[i], layer_dims[i+1]))
            if i != len(layer_dims) - 2: # all but final have relu
                mlp.append(nn.ReLU())
        self.mlp = nn.Sequential(*mlp)

    def forward(self, s):
        ''' Log action probabilities of each action from state

        Args:
            s (Tensor): (batch, state_shape) state tensor

        Returns:
            log_action_probs (Tensor): (batch, num_actions)
        '''
        logits = self.mlp(s)
        log_action_probs = F.log_softmax(logits, dim=-1)
        return log_action_probs

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

