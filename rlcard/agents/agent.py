from __future__ import print_function
import os
import time
import random
import numpy as np
#from tqdm import tqdm
import tensorflow as tf

#from .ops import linear, conv2d, clipped_error
#from .utils import get_time, save_pkl, load_pkl

class DQNAgent(object):
    """ 
    An example DQN agent for card games
    """

    def __init__(self, config, sess):
        self._saver = None
        self.config = config

        #try:
        #    self._attrs = config.__dict__['__flags']
        #except:
        #    self._attrs = class_vars(config)
        #    pp(self._attrs)

        #    self.config = config

        #for attr in self._attrs:
        #    name = attr if not attr.startswith('_') else attr[1:]
        #    setattr(self, name, getattr(self.config, attr))


        self.sess = sess
        self.weight_dir = 'weights'

        self.history = History(self.config)
        self.memory = ReplayMemory(self.config, self.model_dir)

        with tf.variable_scope('step'):
            self.step_op = tf.Variable(0, trainable=False, name='step')
            self.step_input = tf.placeholder('int32', None, name='step_input')
            self.step_assign_op = self.step_op.assign(self.step_input)

        #self.build_dqn()

    def set_seed(self, seed):
        """ Set seed
        """
        random.seed(seed)

    def step(self, state):
        """ Randomly choose an action from the legal actions
        """
        actions = state['actions']
        return random.choice(actions)

    def save_model(self, step=None):
        print(" [*] Saving checkpoints...")
        model_name = type(self).__name__

        if not os.path.exists(self.checkpoint_dir):
            os.makedirs(self.checkpoint_dir)
        self.saver.save(self.sess, self.checkpoint_dir, global_step=step)

    def load_model(self):
        print(" [*] Loading checkpoints...")

        ckpt = tf.train.get_checkpoint_state(self.checkpoint_dir)
        if ckpt and ckpt.model_checkpoint_path:
            ckpt_name = os.path.basename(ckpt.model_checkpoint_path)
            fname = os.path.join(self.checkpoint_dir, ckpt_name)
            self.saver.restore(self.sess, fname)
            print(" [*] Load SUCCESS: %s" % fname)
            return True
        else:
            print(" [!] Load FAILED: %s" % self.checkpoint_dir)
            return False

    @property
    def checkpoint_dir(self):
        return os.path.join('checkpoints', self.model_dir)

    @property
    def model_dir(self):
        model_dir = self.config.env_name
        for k, v in self._attrs.items():
            if not k.startswith('_') and k not in ['display']:
                model_dir += "/%s-%s" % (k, ",".join([str(i) for i in v])
                    if type(v) == list else v)
        return model_dir + '/'

    @property
    def saver(self):
        if self._saver == None:
            self._saver = tf.train.Saver(max_to_keep=10)
        return self._saver 

class History:
    def __init__(self, config):
        self.cnn_format = config.cnn_format

        batch_size, history_length, screen_height, screen_width = \
            config.batch_size, config.history_length, config.screen_height, config.screen_width

        self.history = np.zeros(
            [history_length, screen_height, screen_width], dtype=np.float32)

    def add(self, screen):
        self.history[:-1] = self.history[1:]
        self.history[-1] = screen

    def reset(self):
        self.history *= 0

    def get(self):
        if self.cnn_format == 'NHWC':
            return np.transpose(self.history, (1, 2, 0))
        else:
            return self.history

class ReplayMemory:
    def __init__(self, config, model_dir):
        self.model_dir = model_dir

        self.cnn_format = config.cnn_format
        self.memory_size = config.memory_size
        self.actions = np.empty(self.memory_size, dtype = np.uint8)
        self.rewards = np.empty(self.memory_size, dtype = np.integer)
        self.screens = np.empty((self.memory_size, config.screen_height, config.screen_width), dtype = np.float16)
        self.terminals = np.empty(self.memory_size, dtype = np.bool)
        self.history_length = config.history_length
        self.dims = (config.screen_height, config.screen_width)
        self.batch_size = config.batch_size
        self.count = 0
        self.current = 0

        # pre-allocate prestates and poststates for minibatch
        self.prestates = np.empty((self.batch_size, self.history_length) + self.dims, dtype = np.float16)
        self.poststates = np.empty((self.batch_size, self.history_length) + self.dims, dtype = np.float16)

    def add(self, screen, reward, action, terminal):
        assert screen.shape == self.dims
        # NB! screen is post-state, after action and reward
        self.actions[self.current] = action
        self.rewards[self.current] = reward
        self.screens[self.current, ...] = screen
        self.terminals[self.current] = terminal
        self.count = max(self.count, self.current + 1)
        self.current = (self.current + 1) % self.memory_size

    def getState(self, index):
        assert self.count > 0, "replay memory is empy, use at least --random_steps 1"
        # normalize index to expected range, allows negative indexes
        index = index % self.count
        # if is not in the beginning of matrix
        if index >= self.history_length - 1:
            # use faster slicing
            return self.screens[(index - (self.history_length - 1)):(index + 1), ...]
        else:
            # otherwise normalize indexes and use slower list based access
            indexes = [(index - i) % self.count for i in reversed(range(self.history_length))]
            return self.screens[indexes, ...]

    def sample(self):
        # memory must include poststate, prestate and history
        assert self.count > self.history_length
        # sample random indexes
        indexes = []
        while len(indexes) < self.batch_size:
            # find random index 
            while True:
                # sample one index (ignore states wraping over 
                index = random.randint(self.history_length, self.count - 1)
                # if wraps over current pointer, then get new one
                if index >= self.current and index - self.history_length < self.current:
                    continue
                # if wraps over episode end, then get new one
                # NB! poststate (last screen) can be terminal state!
                if self.terminals[(index - self.history_length):index].any():
                    continue
                # otherwise use this index
                break
      
            # NB! having index first is fastest in C-order matrices
            self.prestates[len(indexes), ...] = self.getState(index - 1)
            self.poststates[len(indexes), ...] = self.getState(index)
            indexes.append(index)

        actions = self.actions[indexes]
        rewards = self.rewards[indexes]
        terminals = self.terminals[indexes]

        if self.cnn_format == 'NHWC':
            return np.transpose(self.prestates, (0, 2, 3, 1)), actions, \
                rewards, np.transpose(self.poststates, (0, 2, 3, 1)), terminals
        else:
            return self.prestates, actions, rewards, self.poststates, terminals

    def save(self):
        for idx, (name, array) in enumerate(
            zip(['actions', 'rewards', 'screens', 'terminals', 'prestates', 'poststates'],
                [self.actions, self.rewards, self.screens, self.terminals, self.prestates, self.poststates])):
            save_npy(array, os.path.join(self.model_dir, name))

    def load(self):
        for idx, (name, array) in enumerate(
            zip(['actions', 'rewards', 'screens', 'terminals', 'prestates', 'poststates'],
                [self.actions, self.rewards, self.screens, self.terminals, self.prestates, self.poststates])):
            array = load_npy(os.path.join(self.model_dir, name))

#class Agent(object):
#  def __init__(self, config, environment, sess):
#    super(Agent, self).__init__(config)
#    self.sess = sess
#    self.weight_dir = 'weights'
#
#    self.env = environment
#    self.history = History(self.config)
#    self.memory = ReplayMemory(self.config, self.model_dir)
#
#    with tf.variable_scope('step'):
#      self.step_op = tf.Variable(0, trainable=False, name='step')
#      self.step_input = tf.placeholder('int32', None, name='step_input')
#      self.step_assign_op = self.step_op.assign(self.step_input)
#
#    self.build_dqn()
#
#  def train(self):
#    start_step = self.step_op.eval()
#    start_time = time.time()
#
#    num_game, self.update_count, ep_reward = 0, 0, 0.
#    total_reward, self.total_loss, self.total_q = 0., 0., 0.
#    max_avg_ep_reward = 0
#    ep_rewards, actions = [], []
#
#    screen, reward, action, terminal = self.env.new_random_game()
#
#    for _ in range(self.history_length):
#      self.history.add(screen)
#
#    for self.step in tqdm(range(start_step, self.max_step), ncols=70, initial=start_step):
#      if self.step == self.learn_start:
#        num_game, self.update_count, ep_reward = 0, 0, 0.
#        total_reward, self.total_loss, self.total_q = 0., 0., 0.
#        ep_rewards, actions = [], []
#
#      # 1. predict
#      action = self.predict(self.history.get())
#      # 2. act
#      screen, reward, terminal = self.env.act(action, is_training=True)
#      # 3. observe
#      self.observe(screen, reward, action, terminal)
#
#      if terminal:
#        screen, reward, action, terminal = self.env.new_random_game()
#
#        num_game += 1
#        ep_rewards.append(ep_reward)
#        ep_reward = 0.
#      else:
#        ep_reward += reward
#
#      actions.append(action)
#      total_reward += reward
#
#      if self.step >= self.learn_start:
#        if self.step % self.test_step == self.test_step - 1:
#          avg_reward = total_reward / self.test_step
#          avg_loss = self.total_loss / self.update_count
#          avg_q = self.total_q / self.update_count
#
#          try:
#            max_ep_reward = np.max(ep_rewards)
#            min_ep_reward = np.min(ep_rewards)
#            avg_ep_reward = np.mean(ep_rewards)
#          except:
#            max_ep_reward, min_ep_reward, avg_ep_reward = 0, 0, 0
#
#          print('\navg_r: %.4f, avg_l: %.6f, avg_q: %3.6f, avg_ep_r: %.4f, max_ep_r: %.4f, min_ep_r: %.4f, # game: %d' \
#              % (avg_reward, avg_loss, avg_q, avg_ep_reward, max_ep_reward, min_ep_reward, num_game))
#
#          if max_avg_ep_reward * 0.9 <= avg_ep_reward:
#            self.step_assign_op.eval({self.step_input: self.step + 1})
#            self.save_model(self.step + 1)
#
#            max_avg_ep_reward = max(max_avg_ep_reward, avg_ep_reward)
#
#          if self.step > 180:
#            self.inject_summary({
#                'average.reward': avg_reward,
#                'average.loss': avg_loss,
#                'average.q': avg_q,
#                'episode.max reward': max_ep_reward,
#                'episode.min reward': min_ep_reward,
#                'episode.avg reward': avg_ep_reward,
#                'episode.num of game': num_game,
#                'episode.rewards': ep_rewards,
#                'episode.actions': actions,
#                'training.learning_rate': self.learning_rate_op.eval({self.learning_rate_step: self.step}),
#              }, self.step)
#
#          num_game = 0
#          total_reward = 0.
#          self.total_loss = 0.
#          self.total_q = 0.
#          self.update_count = 0
#          ep_reward = 0.
#          ep_rewards = []
#          actions = []
#
#  def predict(self, s_t, test_ep=None):
#    ep = test_ep or (self.ep_end +
#        max(0., (self.ep_start - self.ep_end)
#          * (self.ep_end_t - max(0., self.step - self.learn_start)) / self.ep_end_t))
#
#    if random.random() < ep:
#      action = random.randrange(self.env.action_size)
#    else:
#      action = self.q_action.eval({self.s_t: [s_t]})[0]
#
#    return action
#
#  def observe(self, screen, reward, action, terminal):
#    reward = max(self.min_reward, min(self.max_reward, reward))
#
#    self.history.add(screen)
#    self.memory.add(screen, reward, action, terminal)
#
#    if self.step > self.learn_start:
#      if self.step % self.train_frequency == 0:
#        self.q_learning_mini_batch()
#
#      if self.step % self.target_q_update_step == self.target_q_update_step - 1:
#        self.update_target_q_network()
#
#  def q_learning_mini_batch(self):
#    if self.memory.count < self.history_length:
#      return
#    else:
#      s_t, action, reward, s_t_plus_1, terminal = self.memory.sample()
#
#    t = time.time()
#    if self.double_q:
#      # Double Q-learning
#      pred_action = self.q_action.eval({self.s_t: s_t_plus_1})
#
#      q_t_plus_1_with_pred_action = self.target_q_with_idx.eval({
#        self.target_s_t: s_t_plus_1,
#        self.target_q_idx: [[idx, pred_a] for idx, pred_a in enumerate(pred_action)]
#      })
#      target_q_t = (1. - terminal) * self.discount * q_t_plus_1_with_pred_action + reward
#    else:
#      q_t_plus_1 = self.target_q.eval({self.target_s_t: s_t_plus_1})
#
#      terminal = np.array(terminal) + 0.
#      max_q_t_plus_1 = np.max(q_t_plus_1, axis=1)
#      target_q_t = (1. - terminal) * self.discount * max_q_t_plus_1 + reward
#
#    _, q_t, loss, summary_str = self.sess.run([self.optim, self.q, self.loss, self.q_summary], {
#      self.target_q_t: target_q_t,
#      self.action: action,
#      self.s_t: s_t,
#      self.learning_rate_step: self.step,
#    })
#
#    self.writer.add_summary(summary_str, self.step)
#    self.total_loss += loss
#    self.total_q += q_t.mean()
#    self.update_count += 1
#
#  def build_dqn(self):
#    self.w = {}
#    self.t_w = {}
#
#    #initializer = tf.contrib.layers.xavier_initializer()
#    initializer = tf.truncated_normal_initializer(0, 0.02)
#    activation_fn = tf.nn.relu
#
#    # training network
#    with tf.variable_scope('prediction'):
#      if self.cnn_format == 'NHWC':
#        self.s_t = tf.placeholder('float32',
#            [None, self.screen_height, self.screen_width, self.history_length], name='s_t')
#      else:
#        self.s_t = tf.placeholder('float32',
#            [None, self.history_length, self.screen_height, self.screen_width], name='s_t')
#
#      self.l1, self.w['l1_w'], self.w['l1_b'] = conv2d(self.s_t,
#          32, [8, 8], [4, 4], initializer, activation_fn, self.cnn_format, name='l1')
#      self.l2, self.w['l2_w'], self.w['l2_b'] = conv2d(self.l1,
#          64, [4, 4], [2, 2], initializer, activation_fn, self.cnn_format, name='l2')
#      self.l3, self.w['l3_w'], self.w['l3_b'] = conv2d(self.l2,
#          64, [3, 3], [1, 1], initializer, activation_fn, self.cnn_format, name='l3')
#
#      shape = self.l3.get_shape().as_list()
#      self.l3_flat = tf.reshape(self.l3, [-1, reduce(lambda x, y: x * y, shape[1:])])
#
#      if self.dueling:
#        self.value_hid, self.w['l4_val_w'], self.w['l4_val_b'] = \
#            linear(self.l3_flat, 512, activation_fn=activation_fn, name='value_hid')
#
#        self.adv_hid, self.w['l4_adv_w'], self.w['l4_adv_b'] = \
#            linear(self.l3_flat, 512, activation_fn=activation_fn, name='adv_hid')
#
#        self.value, self.w['val_w_out'], self.w['val_w_b'] = \
#          linear(self.value_hid, 1, name='value_out')
#
#        self.advantage, self.w['adv_w_out'], self.w['adv_w_b'] = \
#          linear(self.adv_hid, self.env.action_size, name='adv_out')
#
#        # Average Dueling
#        self.q = self.value + (self.advantage - 
#          tf.reduce_mean(self.advantage, reduction_indices=1, keep_dims=True))
#      else:
#        self.l4, self.w['l4_w'], self.w['l4_b'] = linear(self.l3_flat, 512, activation_fn=activation_fn, name='l4')
#        self.q, self.w['q_w'], self.w['q_b'] = linear(self.l4, self.env.action_size, name='q')
#
#      self.q_action = tf.argmax(self.q, dimension=1)
#
#      q_summary = []
#      avg_q = tf.reduce_mean(self.q, 0)
#      for idx in xrange(self.env.action_size):
#        q_summary.append(tf.summary.histogram('q/%s' % idx, avg_q[idx]))
#      self.q_summary = tf.summary.merge(q_summary, 'q_summary')
#
#    # target network
#    with tf.variable_scope('target'):
#      if self.cnn_format == 'NHWC':
#        self.target_s_t = tf.placeholder('float32', 
#            [None, self.screen_height, self.screen_width, self.history_length], name='target_s_t')
#      else:
#        self.target_s_t = tf.placeholder('float32', 
#            [None, self.history_length, self.screen_height, self.screen_width], name='target_s_t')
#
#      self.target_l1, self.t_w['l1_w'], self.t_w['l1_b'] = conv2d(self.target_s_t, 
#          32, [8, 8], [4, 4], initializer, activation_fn, self.cnn_format, name='target_l1')
#      self.target_l2, self.t_w['l2_w'], self.t_w['l2_b'] = conv2d(self.target_l1,
#          64, [4, 4], [2, 2], initializer, activation_fn, self.cnn_format, name='target_l2')
#      self.target_l3, self.t_w['l3_w'], self.t_w['l3_b'] = conv2d(self.target_l2,
#          64, [3, 3], [1, 1], initializer, activation_fn, self.cnn_format, name='target_l3')
#
#      shape = self.target_l3.get_shape().as_list()
#      self.target_l3_flat = tf.reshape(self.target_l3, [-1, reduce(lambda x, y: x * y, shape[1:])])
#
#      if self.dueling:
#        self.t_value_hid, self.t_w['l4_val_w'], self.t_w['l4_val_b'] = \
#            linear(self.target_l3_flat, 512, activation_fn=activation_fn, name='target_value_hid')
#
#        self.t_adv_hid, self.t_w['l4_adv_w'], self.t_w['l4_adv_b'] = \
#            linear(self.target_l3_flat, 512, activation_fn=activation_fn, name='target_adv_hid')
#
#        self.t_value, self.t_w['val_w_out'], self.t_w['val_w_b'] = \
#          linear(self.t_value_hid, 1, name='target_value_out')
#
#        self.t_advantage, self.t_w['adv_w_out'], self.t_w['adv_w_b'] = \
#          linear(self.t_adv_hid, self.env.action_size, name='target_adv_out')
#
#        # Average Dueling
#        self.target_q = self.t_value + (self.t_advantage - 
#          tf.reduce_mean(self.t_advantage, reduction_indices=1, keep_dims=True))
#      else:
#        self.target_l4, self.t_w['l4_w'], self.t_w['l4_b'] = \
#            linear(self.target_l3_flat, 512, activation_fn=activation_fn, name='target_l4')
#        self.target_q, self.t_w['q_w'], self.t_w['q_b'] = \
#            linear(self.target_l4, self.env.action_size, name='target_q')
#
#      self.target_q_idx = tf.placeholder('int32', [None, None], 'outputs_idx')
#      self.target_q_with_idx = tf.gather_nd(self.target_q, self.target_q_idx)
#
#    with tf.variable_scope('pred_to_target'):
#      self.t_w_input = {}
#      self.t_w_assign_op = {}
#
#      for name in self.w.keys():
#        self.t_w_input[name] = tf.placeholder('float32', self.t_w[name].get_shape().as_list(), name=name)
#        self.t_w_assign_op[name] = self.t_w[name].assign(self.t_w_input[name])
#
#    # optimizer
#    with tf.variable_scope('optimizer'):
#      self.target_q_t = tf.placeholder('float32', [None], name='target_q_t')
#      self.action = tf.placeholder('int64', [None], name='action')
#
#      action_one_hot = tf.one_hot(self.action, self.env.action_size, 1.0, 0.0, name='action_one_hot')
#      q_acted = tf.reduce_sum(self.q * action_one_hot, reduction_indices=1, name='q_acted')
#
#      self.delta = self.target_q_t - q_acted
#
#      self.global_step = tf.Variable(0, trainable=False)
#
#      self.loss = tf.reduce_mean(clipped_error(self.delta), name='loss')
#      self.learning_rate_step = tf.placeholder('int64', None, name='learning_rate_step')
#      self.learning_rate_op = tf.maximum(self.learning_rate_minimum,
#          tf.train.exponential_decay(
#              self.learning_rate,
#              self.learning_rate_step,
#              self.learning_rate_decay_step,
#              self.learning_rate_decay,
#              staircase=True))
#      self.optim = tf.train.RMSPropOptimizer(
#          self.learning_rate_op, momentum=0.95, epsilon=0.01).minimize(self.loss)
#
#    with tf.variable_scope('summary'):
#      scalar_summary_tags = ['average.reward', 'average.loss', 'average.q', \
#          'episode.max reward', 'episode.min reward', 'episode.avg reward', 'episode.num of game', 'training.learning_rate']
#
#      self.summary_placeholders = {}
#      self.summary_ops = {}
#
#      for tag in scalar_summary_tags:
#        self.summary_placeholders[tag] = tf.placeholder('float32', None, name=tag.replace(' ', '_'))
#        self.summary_ops[tag]  = tf.summary.scalar("%s-%s/%s" % (self.env_name, self.env_type, tag), self.summary_placeholders[tag])
#
#      histogram_summary_tags = ['episode.rewards', 'episode.actions']
#
#      for tag in histogram_summary_tags:
#        self.summary_placeholders[tag] = tf.placeholder('float32', None, name=tag.replace(' ', '_'))
#        self.summary_ops[tag]  = tf.summary.histogram(tag, self.summary_placeholders[tag])
#
#      self.writer = tf.summary.FileWriter('./logs/%s' % self.model_dir, self.sess.graph)
#
#    tf.initialize_all_variables().run()
#
#    self._saver = tf.train.Saver(self.w.values() + [self.step_op], max_to_keep=30)
#
#    self.load_model()
#    self.update_target_q_network()
#
#  def update_target_q_network(self):
#    for name in self.w.keys():
#      self.t_w_assign_op[name].eval({self.t_w_input[name]: self.w[name].eval()})
#
#  def save_weight_to_pkl(self):
#    if not os.path.exists(self.weight_dir):
#      os.makedirs(self.weight_dir)
#
#    for name in self.w.keys():
#      save_pkl(self.w[name].eval(), os.path.join(self.weight_dir, "%s.pkl" % name))
#
#  def load_weight_from_pkl(self, cpu_mode=False):
#    with tf.variable_scope('load_pred_from_pkl'):
#      self.w_input = {}
#      self.w_assign_op = {}
#
#      for name in self.w.keys():
#        self.w_input[name] = tf.placeholder('float32', self.w[name].get_shape().as_list(), name=name)
#        self.w_assign_op[name] = self.w[name].assign(self.w_input[name])
#
#    for name in self.w.keys():
#      self.w_assign_op[name].eval({self.w_input[name]: load_pkl(os.path.join(self.weight_dir, "%s.pkl" % name))})
#
#    self.update_target_q_network()
#
#  def inject_summary(self, tag_dict, step):
#    summary_str_lists = self.sess.run([self.summary_ops[tag] for tag in tag_dict.keys()], {
#      self.summary_placeholders[tag]: value for tag, value in tag_dict.items()
#    })
#    for summary_str in summary_str_lists:
#      self.writer.add_summary(summary_str, self.step)
#
#  def play(self, n_step=10000, n_episode=100, test_ep=None, render=False):
#    if test_ep == None:
#      test_ep = self.ep_end
#
#    test_history = History(self.config)
#
#    if not self.display:
#      gym_dir = '/tmp/%s-%s' % (self.env_name, get_time())
#      self.env.env.monitor.start(gym_dir)
#
#    best_reward, best_idx = 0, 0
#    for idx in xrange(n_episode):
#      screen, reward, action, terminal = self.env.new_random_game()
#      current_reward = 0
#
#      for _ in range(self.history_length):
#        test_history.add(screen)
#
#      for t in tqdm(range(n_step), ncols=70):
#        # 1. predict
#        action = self.predict(test_history.get(), test_ep)
#        # 2. act
#        screen, reward, terminal = self.env.act(action, is_training=False)
#        # 3. observe
#        test_history.add(screen)
#
#        current_reward += reward
#        if terminal:
#          break
#
#      if current_reward > best_reward:
#        best_reward = current_reward
#        best_idx = idx
#
#      print("="*30)
#      print(" [%d] Best reward : %d" % (best_idx, best_reward))
#      print("="*30)
#
#    if not self.display:
#      self.env.env.monitor.close()
#      #gym.upload(gym_dir, writeup='https://github.com/devsisters/DQN-tensorflow', api_key='')
