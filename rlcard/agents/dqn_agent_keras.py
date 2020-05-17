from tensorflow import keras
from tensorflow.keras.layers import Dense, Dropout, Conv2D, MaxPooling2D, Flatten, BatchNormalization
from tensorflow.keras.layers import Activation
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.layers import Activation
from tensorflow.keras import Sequential


import random
import numpy as np
import tensorflow as tf
from collections import namedtuple
from copy import deepcopy

from rlcard.utils.utils import remove_illegal

Transition = namedtuple('Transition', ['state', 'action', 'reward', 'next_state', 'done'])


class DQNAgent(object):

    def __init__(self,
                 scope,
                 replay_memory_size=20000,
                 replay_memory_init_size=100,
                 update_target_estimator_every=1000,
                 discount_factor=0.99,
                 epsilon_start=1.0,
                 epsilon_end=0.1,
                 epsilon_decay_steps=20000,
                 batch_size=32,
                 action_num=2,
                 state_shape=None,
                 train_every=1,
                 mlp_layers=None,
                 learning_rate=0.00005):

        '''
        Q-Learning algorithm for off-policy TD control using Function Approximation.
        Finds the optimal greedy policy while following an epsilon-greedy policy.

        Args:
            sess (tf.Session): Tensorflow Session object.
            scope (string): The name scope of the DQN agent.
            replay_memory_size (int): Size of the replay memory
            replay_memory_init_size (int): Number of random experiences to sampel when initializing
              the reply memory.
            train_every (int): Train the agent every X steps.
            update_target_estimator_every (int): Copy parameters from the Q estimator to the
              target estimator every N steps
            discount_factor (float): Gamma discount factor
            epsilon_start (int): Chance to sample a random action when taking an action.
              Epsilon is decayed over time and this is the start value
            epsilon_end (int): The final minimum value of epsilon after decaying is done
            epsilon_decay_steps (int): Number of steps to decay epsilon over
            batch_size (int): Size of batches to sample from the replay memory
            evaluate_every (int): Evaluate every N steps
            action_num (int): The number of the actions
            state_space (list): The space of the state vector
            train_every (int): Train the network every X steps.
            mlp_layers (list): The layer number and the dimension of each layer in MLP
            learning_rate (float): The learning rate of the DQN agent.
        '''
        self.use_raw = False
        self.scope = scope
        self.replay_memory_init_size = replay_memory_init_size
        self.update_target_estimator_every = update_target_estimator_every
        self.discount_factor = discount_factor
        self.epsilon_decay_steps = epsilon_decay_steps
        self.batch_size = batch_size
        self.action_num = action_num
        self.train_every = train_every

        # Total timesteps
        self.total_t = 0

        # Total training step
        self.train_t = 0

        # The epsilon decay scheduler
        self.epsilons = np.linspace(epsilon_start, epsilon_end, epsilon_decay_steps)

        # Create estimators
        self.q_estimator = Estimator(scope=self.scope+"_q", action_num=action_num, learning_rate=learning_rate, state_shape=state_shape, mlp_layers=mlp_layers)
        self.target_estimator = Estimator(scope=self.scope+"_target_q", action_num=action_num, learning_rate=learning_rate, state_shape=state_shape, mlp_layers=mlp_layers)

        # Create replay memory
        self.memory = Memory(replay_memory_size, batch_size)

    def feed(self, ts):
        ''' Store data in to replay buffer and train the agent. There are two stages.
            In stage 1, populate the memory without training
            In stage 2, train the agent every several timesteps

        Args:
            ts (list): a list of 5 elements that represent the transition
        '''

        (state, action, reward, next_state, done) = tuple(ts)
        self.feed_memory(state['obs'], action, reward, next_state['obs'], done)
        self.total_t += 1
        tmp = self.total_t - self.replay_memory_init_size
        if tmp>=0 and tmp%self.train_every == 0:
            loss = self.train()

    def step(self, state):
        ''' Predict the action for genrating training data

        Args:
            state (numpy.array): current state

        Returns:
            action (int): an action id
        '''

        A = self.predict(state['obs'])
        A = remove_illegal(A, state['legal_actions'])
        action = np.random.choice(np.arange(len(A)), p=A)
        return action

    def eval_step(self, state):
        ''' Predict the action for evaluation purpose.

        Args:
            state (numpy.array): current state

        Returns:
            action (int): an action id
            probs (list): a list of probabilies
        '''

        q_values = self.q_estimator.predict( np.expand_dims(state['obs'], 0))[0]
        probs = remove_illegal(np.exp(q_values), state['legal_actions'])
        best_action = np.argmax(probs)
        return best_action, probs

    def predict(self, state):
        ''' Predict the action probabilities

        Args:
            state (numpy.array): current state

        Returns:
            q_values (numpy.array): a 1-d array where each entry represents a Q value
        '''

        epsilon = self.epsilons[min(self.total_t, self.epsilon_decay_steps-1)]
        A = np.ones(self.action_num, dtype=float) * epsilon / self.action_num
        q_values = self.q_estimator.predict(np.expand_dims(state, 0))[0]
        best_action = np.argmax(q_values)
        A[best_action] += (1.0 - epsilon)
        return A

    def train(self):
        ''' Train the network

        Returns:
            loss (float): The loss of the current batch.
        '''
        state_batch, action_batch, reward_batch, next_state_batch, done_batch = self.memory.sample()
        # Calculate q values and targets (Double DQN)
        q_values_next = self.q_estimator.predict(next_state_batch)
        best_actions = np.argmax(q_values_next, axis=1)

        #Evaluate best next actions using Target-network (Double DQN)
        q_values_next_target = self.target_estimator.predict(next_state_batch)
        target_batch = reward_batch + np.invert(done_batch).astype(np.float32) * \
            self.discount_factor * q_values_next_target[np.arange(self.batch_size), best_actions]

        # Perform gradient descent update
        state_batch = np.array(state_batch)

        loss = self.q_estimator.update(state_batch, action_batch, target_batch)
        print('\rINFO - Agent {}, step {}, rl-loss: {}'.format(self.scope, self.total_t, loss), end='')


        # Update the target estimator
        if self.train_t % self.update_target_estimator_every == 0:
            #copy_model_parameters(self.sess, self.q_estimator, self.target_estimator)
            #self.target_estimator = deepcopy(self.q_estimator)
            self.target_estimator.qnet.set_weights(self.q_estimator.qnet.get_weights())
            print("\nINFO - Copied model parameters to target network.")


        self.train_t += 1

    def feed_memory(self, state, action, reward, next_state, done):
        ''' Feed transition to memory

        Args:
            state (numpy.array): the current state
            action (int): the performed action ID
            reward (float): the reward received
            next_state (numpy.array): the next state after performing the action
            done (boolean): whether the episode is finished
        '''
        self.memory.save(state, action, reward, next_state, done)

    def save_model(self, model_path):
        self.q_estimator.qnet.save(model_path)

class Estimator():
    ''' Q-Value Estimator neural network.
        This network is used for both the Q-Network and the Target Network.
    '''

    def __init__(self, scope="estimator", action_num=2, learning_rate=0.001, state_shape=None, mlp_layers=None):
        ''' Initilalize an Estimator object.

        Args:
            action_num (int): the number output actions
            state_shap (list): the shape of the state space
        '''
        self.scope = scope
        self.action_num = action_num
        self.learning_rate=learning_rate
        self.state_shape = state_shape
        self.mlp_layers = mlp_layers

        #build the model
        qnet = self._build_model(action_num, state_shape, mlp_layers)
        self.qnet = qnet


        # Optimizer Parameters from original paper
        self.optimizer = tf.train.AdamOptimizer(learning_rate=self.learning_rate, name='dqn_adam')

    def _build_model(self, action_num, state_shape, mlp_layers):
            ''' Build an MLP model.
            '''
            # Placeholders for our input
            # Our input are 4 RGB frames of shape 160, 160 each     *[4,160,160,3]
                # Neural Net for Deep-Q learning Model
            input_shape = []
            input_shape.extend(self.state_shape)
            model = Sequential()
            model.add(BatchNormalization(input_shape = input_shape))
            model.add(Flatten())
            for dim in self.state_shape:
                model.add(Dense(dim, activation = 'tanh'))
            model.add(Dense(self.action_num, activation= 'linear'))
            model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate), metrics=['accuracy'])
            model.summary()
            return model

    def predict(self, s):
        ''' Predicts action values.

        Args:
          sess (tf.Session): Tensorflow Session object
          s (numpy.array): State input of shape [batch_size, 4, 160, 160, 3]
          is_train (boolean): True if is training

        Returns:
          Tensor of shape [batch_size, NUM_VALID_ACTIONS] containing the estimated
          action values.
        '''

        action_mask = np.ones((len(s,), self.action_num))
        return self.qnet.predict(x=[s, action_mask])

    #encode the actions
    def one_hot_encode(self, n, action):
        one_hot = np.zeros(n)
        one_hot[int(action)] = 1
        return one_hot

    def update(self, s, a, y):
        ''' Updates the estimator towards the given targets.

        Args:
          sess (tf.Session): Tensorflow Session object
          s (list): State input of shape [batch_size, 4, 160, 160, 3]   //state_batch
          a (list): Chosen actions of shape [batch_size]    //action_batch
          y (list): Targets of shape [batch_size]           //target_batch

        Returns:
          The calculated loss on the batch.
        '''

        y = np.array(y)
        one_hot_actions = np.array([self.one_hot_encode(self.action_num, action) for action in a])
        history = self.qnet.fit(x = [s, one_hot_actions], y = one_hot_actions*y[:,None], batch_size = 32, verbose = 0)
        return history.history['loss'][0]

class Memory(object):
    ''' Memory for saving transitions
    '''

    def __init__(self, memory_size, batch_size):
        ''' Initialize
        Args:
            memory_size (int): the size of the memroy buffer
        '''
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.memory = []

    def save(self, state, action, reward, next_state, done):
        ''' Save transition into memory

        Args:
            state (numpy.array): the current state
            action (int): the performed action ID
            reward (float): the reward received
            next_state (numpy.array): the next state after performing the action
            done (boolean): whether the episode is finished
        '''
        if len(self.memory) == self.memory_size:
            self.memory.pop(0)
        transition = Transition(state, action, reward, next_state, done)
        self.memory.append(transition)

    def sample(self):
        ''' Sample a minibatch from the replay memory

        Returns:
            state_batch (list): a batch of states
            action_batch (list): a batch of actions
            reward_batch (list): a batch of rewards
            next_state_batch (list): a batch of states
            done_batch (list): a batch of dones
        '''
        samples = random.sample(self.memory, self.batch_size)
        return map(np.array, zip(*samples))
