'''A toy example of learning a Deep-Q Agent on Leduc Hold'em with multiple processes
'''
import numpy as np
import tensorflow as tf
import multiprocessing
from multiprocessing import Process, JoinableQueue, Queue

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed, assign_task, tournament
from rlcard.utils.logger import Logger

# and intial memory size
memory_init_size = 100

# Train the agent every X steps
train_every = 1

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
save_plot_every = 1000
evaluate_num = 10000
episode_num = 1000000

# The paths for saving the logs and learning curves
log_dir = './experiments/leduc_holdem_dqn_multi_result/'

# Set the process class to generate trajectories for training and evaluation
class LeducHoldemProcess(Process):

    def __init__(self, index, input_queue, output_queue, seed=None):
        Process.__init__(self)
        if seed is not None:
            np.random.seed(seed)
        self.index = index
        self.input_queue = input_queue
        self.output_queue = output_queue

    def run(self):
        import tensorflow as tf
        self.env = rlcard.make('leduc-holdem')
        self.sess = tf.Session()
        agent = DQNAgent(self.sess,
                         scope='sub-dqn' + str(self.index),
                         action_num=self.env.action_num,
                         replay_memory_init_size=memory_init_size,
                         train_every=train_every,
                         state_shape=self.env.state_shape,
                         mlp_layers=[128, 128])
        random_agent = RandomAgent(action_num=self.env.action_num)
        self.env.set_agents([agent, random_agent])
        self.sess.run(tf.global_variables_initializer())


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
                        self.output_queue.put((trajectories, self.env.timestep))
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
    PROCESSES = [LeducHoldemProcess(index, INPUT_QUEUE, OUTPUT_QUEUE, np.random.randint(1000000))
                 for index in range(PROCESS_NUM)]
    for p in PROCESSES:
        p.start()

    # Make environment
    env = rlcard.make('leduc-holdem')
    eval_env = rlcard.make('leduc-holdem')

    with tf.Session() as sess:

        # Set agents
        global_step = tf.Variable(0, name='global_step', trainable=False)
        agent = DQNAgent(sess,
                         scope='dqn',
                         action_num=env.action_num,
                         replay_memory_init_size=memory_init_size,
                         state_shape=env.state_shape,
                         train_every=train_every,
                         mlp_layers=[128, 128])
        random_agent = RandomAgent(action_num=env.action_num)
        env.set_agents([agent, random_agent])
        eval_env.set_agents([agent, random_agent])
        sess.run(tf.global_variables_initializer())

        # Init a Logger to plot the learning curve
        logger = Logger(log_dir)

        for episode in range(episode_num // evaluate_every):

            # Generate data from the environment
            tasks = assign_task(evaluate_every, PROCESS_NUM)
            for task in tasks:
                INPUT_QUEUE.put((task, True, None, None))
            for _ in range(evaluate_every):
                trajectories, timestep = OUTPUT_QUEUE.get()
                env.timestep += timestep
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
        logger.plot('DQN_multi_process')
        
        # Save model
        save_dir = 'models/leduc_dqn_multi'
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
