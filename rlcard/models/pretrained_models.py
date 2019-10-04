''' Wrrapers of pretrained models. Designed for Tensorflow.
'''

import os
import tensorflow as tf

import rlcard
from rlcard.agents.nfsp_agent import NFSPAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.models.model import Model

# Root path of pretrianed models
ROOT_PATH = os.path.join(rlcard.__path__[0], 'models/pretrained')

class LeducHoldemNFSPModel(Model):
    ''' A pretrained model on Leduc Holdem with NFSP
    '''

    def __init__(self):
        ''' Load pretrained model
        '''
        self.graph = tf.Graph()
        self.sess = tf.Session(graph=self.graph)

        env = rlcard.make('leduc-holdem')
        with self.graph.as_default():
            self.nfsp_agents = []
            for i in range(env.player_num):
                agent = NFSPAgent(self.sess,
                                  scope='nfsp' + str(i),
                                  action_num=env.action_num,
                                  state_shape=env.state_shape,
                                  hidden_layers_sizes=[128,128],
                                  q_norm_step=1000,
                                  q_mlp_layers=[128,128])
                self.nfsp_agents.append(agent)
            normalize(env, self.nfsp_agents, 1000)
            self.sess.run(tf.global_variables_initializer())

        check_point_path = os.path.join(ROOT_PATH, 'leduc_holdem_nfsp')
        with self.sess.as_default():
            with self.graph.as_default():
                saver = tf.train.Saver(tf.model_variables())
                saver.restore(self.sess, tf.train.latest_checkpoint(check_point_path))
    @property
    def agents(self):
        ''' Get a list of agents for each position in a the game

        Returns:
            agents (list): A list of agents

        Note: Each agent should be just like RL agent with step and eval_step
              functioning well.
        '''
        return self.nfsp_agents

    @property
    def use_raw(self):
        ''' Indicate whether use raw state and action

        Returns:
            use_raw (boolean): True if using raw state and action
        '''
        return False


def normalize(e, agents, num):
    ''' Feed random data to normalizer

    Args:
        e (Env): AN Env class
        agents (list): A list of Agent object
        num (int): The number of steps to be normalized

    '''
    begin_step = e.timestep
    e.set_agents([RandomAgent(e.action_num) for _ in range(e.player_num)])
    while e.timestep - begin_step < num:
        trajectories, _ = e.run(is_training=False)
        for agent in agents:
            for tra in trajectories:
                for ts in tra:
                    agent.feed(ts)

