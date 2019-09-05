import numpy as np
import random
import tensorflow as tf
from collections import namedtuple
import rlcard
from rlcard.utils.utils import *

Transition = namedtuple("Transition", ["state", "action", "reward", "next_state", "done"])

class DQNAgent(object):
    """
        DQN agent
    """

    def __init__(self,
                 sess,
                 replay_memory_size=20000,
                 replay_memory_init_size=20000,
                 update_target_estimator_every=1000,
                 discount_factor=0.99,
                 epsilon_start=1.0,
                 epsilon_end=0.1,
                 epsilon_decay_steps=20000,
                 batch_size=32,
                 action_size=2,
                 state_shape=[2],
                 norm_step=1000):
        """
        Q-Learning algorithm for off-policy TD control using Function Approximation.
        Finds the optimal greedy policy while following an epsilon-greedy policy.

        Args:
            sess: Tensorflow Session object
            replay_memory_size: Size of the replay memory
            replay_memory_init_size: Number of random experiences to sampel when initializing 
              the reply memory.
            update_target_estimator_every: Copy parameters from the Q estimator to the 
              target estimator every N steps
            discount_factor: Gamma discount factor
            epsilon_start: Chance to sample a random action when taking an action.
              Epsilon is decayed over time and this is the start value
            epsilon_end: The final minimum value of epsilon after decaying is done
            epsilon_decay_steps: Number of steps to decay epsilon over
            batch_size: Size of batches to sample from the replay memory
            evaluate_every: Evaluate every N steps
            action_size: the number of the actions
            state_space: the space of the state vector
            norm_step: the number of the step used form noramlize state
        """

        self.sess = sess
        self.replay_memory_init_size = replay_memory_init_size
        self.update_target_estimator_every = update_target_estimator_every
        self.discount_factor = discount_factor
        self.epsilon_decay_steps = epsilon_decay_steps
        self.batch_size = batch_size
        self.action_size = action_size
        self.norm_step = norm_step


        # Total timesteps
        self.total_t = 0

        # Total training step
        self.train_t = 0

        # The epsilon decay scheduler
        self.epsilons = np.linspace(epsilon_start, epsilon_end, epsilon_decay_steps)

        # Create estimators
        self.q_estimator = Estimator(scope="q", action_size=action_size, state_shape=state_shape)
        self.target_estimator = Estimator(scope="target_q", action_size=action_size, state_shape=state_shape)

        self.sess.run(tf.global_variables_initializer())

        # Create normalizer
        self.normalizer = Normalizer()

        # Create replay memory
        self.memory = Memory(replay_memory_size, batch_size)

    def feed(self, ts):
        """ Store data and train
            Stage 1: populate the Normalizer that does normalization
            Stage 2: popolate memory
            Stage 3: training
        Returns:
            is_training: whether the models start training
        """
        (state, action, reward, next_state, done) = tuple(ts)
        if self.total_t < self.norm_step:
            self.feed_norm(state)
            is_training = False
        else:
            self.feed_memory(state, action, reward, next_state, done)
            if self.total_t >= self.norm_step + self.replay_memory_init_size:
                if self.total_t == self.norm_step + self.replay_memory_init_size:
                    print('\n')
                self.train()
                is_training = True
            else:
                print("\rINFO - Populating replay memory...", end = '')
                is_training = False
        self.total_t += 1
        return is_training

    def step(self, state):
        """ Predict the action for genrating training data
        Args:
            state: current state
        Returns:
            action: an action id
        """
        epsilon = self.epsilons[min(self.total_t, self.epsilon_decay_steps-1)]     
        A = np.ones(self.action_size, dtype=float) * epsilon / self.action_size
        q_values = self.q_estimator.predict(self.sess, np.expand_dims(self.normalizer.normalize(state), 0))[0]
        best_action = np.argmax(q_values)
        A[best_action] += (1.0 - epsilon)
        action = np.random.choice(np.arange(len(A)), p=A)
        return action

    def eval_step(self, state):
        """ Predict the action for evaluation purpose
        Args:
            state: current state
        Returns:
            action: an action id
        """
        q_values = self.q_estimator.predict(self.sess, np.expand_dims(self.normalizer.normalize(state), 0))[0]
        best_action = np.argmax(q_values)
        return best_action

    def train(self):
        """ Train the network
        """
        state_batch, action_batch, reward_batch, next_state_batch, done_batch = self.memory.sample()
        # Calculate q values and targets (Double DQN)
        q_values_next = self.q_estimator.predict(self.sess, next_state_batch)
        best_actions = np.argmax(q_values_next, axis=1)
        q_values_next_target = self.target_estimator.predict(self.sess, next_state_batch)
        target_batch = reward_batch + np.invert(done_batch).astype(np.float32) * \
            self.discount_factor * q_values_next_target[np.arange(self.batch_size), best_actions]

        # Perform gradient descent update
        state_batch = np.array(state_batch)

        loss = self.q_estimator.update(self.sess, state_batch, action_batch, target_batch)
        print("\rINFO - Step {} loss: {}".format(
                self.train_t, loss), end="")

        # Update the target estimator
        if self.train_t % self.update_target_estimator_every == 0:
            copy_model_parameters(self.sess, self.q_estimator, self.target_estimator)
            print("\nINFO - Copied model parameters to target network.")

        self.train_t += 1

    def set_seed(self,seed):
        """ Seed the agent
        """
        pass

    def feed_norm(self, state):
        """ Feed state to normalizer to collect statistics
        Args:
            state: the state that will be feed into normalizer
        """
        self.normalizer.append(state)

    def feed_memory(self, state, action, reward, next_state, done):
        """ Feed transition to memory
        """
        self.memory.save(self.normalizer.normalize(state), action, reward, self.normalizer.normalize(next_state), done)


class Normalizer(object):
    """ Track the running statistics for normlization
    """
    def __init__(self):
        self.mean = None
        self.std = None
        self.state_memory = []
        self.max_size = 1000
        self.length = 0


    def normalize(self, s):
        """ Normalize the state with the running mean and std
        Args:
            s: 1d list
        Return:
            1d numpy array of normalized state
        """
        self.append(s)
        return (s - self.mean) / (self.std)

    def append(self, s):
        """ Append a new state and update the running statistics
        Args:
            s: 1d list
        """
        if len(self.state_memory) > 1000:
            self.state_memory.pop(0)
        self.state_memory.append(s)
        self.mean = np.mean(self.state_memory, axis=0)
        self.std = np.mean(self.state_memory, axis=0)
        self.length = len(self.state_memory)


class Estimator():
    """Q-Value Estimator neural network.

    This network is used for both the Q-Network and the Target Network.
    """

    def __init__(self, scope="estimator", action_size=2, state_shape=[2]):
        self.scope = scope
        self.action_size = action_size
        self.state_shape = state_shape

        # Create a glboal step variable
        self.global_step = tf.Variable(0, name='global_step', trainable=False)

        with tf.variable_scope(scope):
            # Build the graph
            self._build_model()

    def _build_model(self):
        """
        MLP model
        """

        # Placeholders for our input
        # Our input are 4 RGB frames of shape 160, 160 each
        input_shape = [None]
        input_shape.extend(self.state_shape)
        self.X_pl = tf.placeholder(shape=input_shape, dtype=tf.float32, name="X")
        # The TD target value
        self.y_pl = tf.placeholder(shape=[None], dtype=tf.float32, name="y")
        # Integer id of which action was selected
        self.actions_pl = tf.placeholder(shape=[None], dtype=tf.int32, name="actions")

        batch_size = tf.shape(self.X_pl)[0]

        # Fully connected layers
        fc1 = tf.contrib.layers.fully_connected(self.X_pl, 10, activation_fn=tf.tanh)
        fc2 = tf.contrib.layers.fully_connected(fc1, 10, activation_fn=tf.tanh)
        self.predictions = tf.contrib.layers.fully_connected(fc2, self.action_size, activation_fn=None)

        # Get the predictions for the chosen actions only
        gather_indices = tf.range(batch_size) * tf.shape(self.predictions)[1] + self.actions_pl
        self.action_predictions = tf.gather(tf.reshape(self.predictions, [-1]), gather_indices)

        # Calculate the loss
        self.losses = tf.squared_difference(self.y_pl, self.action_predictions)
        self.loss = tf.reduce_mean(self.losses)

        # Optimizer Parameters from original paper
        self.optimizer = tf.train.AdamOptimizer(learning_rate=0.00005)

        self.train_op = self.optimizer.minimize(self.loss, global_step=tf.contrib.framework.get_global_step())

    def predict(self, sess, s):
        """
        Predicts action values.

        Args:
          sess: Tensorflow session
          s: State input of shape [batch_size, 4, 160, 160, 3]

        Returns:
          Tensor of shape [batch_size, NUM_VALID_ACTIONS] containing the estimated 
          action values.
        """
 
        return sess.run(self.predictions, { self.X_pl: s })

    def update(self, sess, s, a, y):
        """
        Updates the estimator towards the given targets.

        Args:
          sess: Tensorflow session object
          s: State input of shape [batch_size, 4, 160, 160, 3]
          a: Chosen actions of shape [batch_size]
          y: Targets of shape [batch_size]

        Returns:
          The calculated loss on the batch.
        """
        feed_dict = { self.X_pl: s, self.y_pl: y, self.actions_pl: a }
        global_step, _, loss = sess.run(
                [tf.contrib.framework.get_global_step(), self.train_op, self.loss],
                    feed_dict)
        return loss

class Memory(object):
    """ Memory for saving transitions
    """
    def __init__(self, memory_size, batch_size):
        """
        Args:
            memory_size: the size of the memroy buffer
        """
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.memory = []

    def save(self, state, action, reward, next_state, done):
        """
        Args:
            state: current state
            action: action taken
            reward: reward received
            next_state: the next state observed
            done: whether it is finished
        """
        if len(self.memory) == self.memory_size:
            self.memory.pop(0)
        transition = Transition(state, action, reward, next_state, done)
        self.memory.append(transition)

    def sample(self):
        """ Sample a minibatch from the replay memory
        Returns:
            state_batch: a batch of states
            action_batch: a batch of actions
            reward_batch: a batch of rewards
            next_state_batch: a batch of states
            done_batch: a batch of dones
        """
        samples = random.sample(self.memory, self.batch_size)
        return map(np.array, zip(*samples))

        
def copy_model_parameters(sess, estimator1, estimator2):
    """
    Copies the model parameters of one estimator to another.

    Args:
      sess: Tensorflow session instance
      estimator1: Estimator to copy the paramters from
      estimator2: Estimator to copy the parameters to
    """
    e1_params = [t for t in tf.trainable_variables() if t.name.startswith(estimator1.scope)]
    e1_params = sorted(e1_params, key=lambda v: v.name)
    e2_params = [t for t in tf.trainable_variables() if t.name.startswith(estimator2.scope)]
    e2_params = sorted(e2_params, key=lambda v: v.name)

    update_ops = []
    for e1_v, e2_v in zip(e1_params, e2_params):
        op = e2_v.assign(e1_v)
        update_ops.append(op)

    sess.run(update_ops)

