''' A toy example of learning a Deep-Q Agent on Blackjack with multiple processes
'''
import numpy as np
import tensorflow as tf
import multiprocessing
from multiprocessing import Process, JoinableQueue, Queue

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.utils.utils import set_global_seed, assign_task, tournament
from rlcard.utils.logger import Logger

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 100
norm_step = 100

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
save_plot_every = 1000
evaluate_num = 10000
episode_num = 1000000

# The paths for saving the logs and learning curves
log_dir = './experiments/blackjack_dqn_result/'

# Set the process class to generate trajectories for training and evaluation
class BlackjackProcess(Process):

    def __init__(self, index, input_queue, output_queue, seed=None):
        Process.__init__(self)
        if seed is not None:
            np.random.seed(seed)
        self.index = index
        self.input_queue = input_queue
        self.output_queue = output_queue

    def run(self):
        #import tensorflow as tf
        self.env = rlcard.make('blackjack')
        self.sess = tf.Session()
        agent = DQNAgent(self.sess,
                         scope='sub-dqn' + str(self.index),
                         action_num=self.env.action_num,
                         replay_memory_init_size=memory_init_size,
                         state_shape=self.env.state_shape,
                         mlp_layers=[10, 10])
        self.env.set_agents([agent])
        self.sess.run(tf.global_variables_initializer())

        # normalize
        for _ in range(norm_step):
            trajectories, _ = self.env.run()
            for ts in trajectories[0]:
                agent.feed(ts)

        # Receive instruction to run game and generate trajectories
        while True:
            instruction = self.input_queue.get()
            if instruction is not None:
                tasks, train_flag, variables, total_t = instruction

                # For evaluation
                if not train_flag:
                    agent.total_t = total_t
                    global_vars = [tf.convert_to_tensor(var) for var in variables]
                    agent.copy_params_op(global_vars)
                    for _ in range(tasks):
                        _, payoffs = self.env.run(is_training=train_flag)
                        self.output_queue.put(payoffs)

                # For training
                else:
                    for _ in range(tasks):
                        trajectories, _ = self.env.run(is_training=train_flag)
                        self.output_queue.put(trajectories)
                self.input_queue.task_done()
            else:
                self.input_queue.task_done()
                break
        self.sess.close()
        return

if __name__ == '__main__':
    # Avoid RuntimeError
    multiprocessing.freeze_support()

    # Set a global seed
    set_global_seed(0)

    # Initialize processes
    PROCESS_NUM = 16
    INPUT_QUEUE = JoinableQueue()
    OUTPUT_QUEUE = Queue()
    PROCESSES = [BlackjackProcess(index, INPUT_QUEUE, OUTPUT_QUEUE, np.random.randint(1000000))
                 for index in range(PROCESS_NUM)]
    for p in PROCESSES:
        p.start()

    # Make environment
    env = rlcard.make('blackjack')
    eval_env = rlcard.make('blackjack')

    with tf.Session() as sess:

        # Set agents
        global_step = tf.Variable(0, name='global_step', trainable=False)
        agent = DQNAgent(sess,
                         scope='dqn',
                         action_num=env.action_num,
                         replay_memory_init_size=memory_init_size,
                         state_shape=env.state_shape,
                         mlp_layers=[10, 10])
        env.set_agents([agent])
        eval_env.set_agents([agent])
        sess.run(tf.global_variables_initializer())

        # Init a Logger to plot the learning curve
        logger = Logger(xlabel='timestep', ylabel='reward',
                        legend='DQN on Blackjack', log_path=log_path, csv_path=csv_path)

        for episode in range(episode_num // evaluate_every):

            # Generate data from the environment
            tasks = assign_task(evaluate_every, PROCESS_NUM)
            for task in tasks:
                INPUT_QUEUE.put((task, True, None, None))
            for _ in range(evaluate_every):
                trajectories = OUTPUT_QUEUE.get()

                # Feed transitions into agent memory, and train
                for ts in trajectories[0]:
                    agent.feed(ts)
            # Evaluate the performance
            reward = 0
            tasks = assign_task(evaluate_num, PROCESS_NUM)
            variables = tf.contrib.slim.get_variables(scope="dqn", collection=tf.GraphKeys.TRAINABLE_VARIABLES)
            variables = [var.eval() for var in variables]
            for task in tasks:
                INPUT_QUEUE.put((task, False, variables, agent.total_t))
            for _ in range(evaluate_num):
                payoffs = OUTPUT_QUEUE.get()
                reward += payoffs[0]
            logger.log('\n########## Evaluation ##########')
            logger.log('Average reward is {}'.format(float(reward)/evaluate_num))

        # Close files in the logger
        logger.close_files()

        # Plot the learning curve
        logger.plot('DQN')
        
        # Save model
        save_dir = 'models/blackjack_dqn'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        saver = tf.train.Saver()
        saver.save(sess, os.path.join(save_dir, 'model'))

        # Close multi-processes
        for _ in range(PROCESS_NUM):
            INPUT_QUEUE.put(None)

        INPUT_QUEUE.join()

        for p in PROCESSES:
            p.join()
