import numpy as np
import collections

import os
import pickle

from rlcard.utils.utils import *

class BRAgent():
    ''' Implement CFR algorithm
    '''

    def __init__(self, env, policy):
        ''' Initilize Agent

        Args:
            env (Env): Env class
        '''
        self.use_raw = False
        self.env = env
        self._num_of_player = env.player_num
        if self._num_of_player > 2:
            raise "Best Response only for Two-player games"

        # A policy is a dict state_str -> action probabilities
        self.opponent_policy = policy 
        self.average_policy = collections.defaultdict(np.array)

        # Regret is a dict state_str -> action regrets
        self.regrets = collections.defaultdict(np.array)

        self.iteration = 0

    def traverse_tree(self, probs, player_id):
        ''' Traverse the game tree, get information set 

        Args:
            probs: The reach probability of the current node
            player_id: The player to update the value

        Returns:
            state_utilities (list): The expected utilities for all the players
        '''
        if self.env.is_over():
            return self.env.get_payoffs()

        current_player = self.env.get_player_id()

        obs, legal_actions = self.get_state(current_player)
        state = self.env.get_state(current_player)
        action_probs = self.action_probs(state, self.opponent_policy)

        for action in legal_actions:
            action_prob = action_probs[action]
            new_probs = probs.copy()
            new_probs[current_player] *= action_prob

            # Keep traversing the child state
            self.env.step(action)
            utility = self.traverse_tree(new_probs, player_id)
            self.env.step_back()

        # If it is current player, we record the policy and compute regret
        player_prob = probs[current_player]
        counterfactual_prob = (np.prod(probs[:current_player]) *
                                np.prod(probs[current_player + 1:]))
        s = self.get_state(current_player)
        self.infosets[obs].append((s, counterfactual_prob))

    def value(self, curr_player, state, this_player):
        """Returns the value of the specified state to the best-responder."""
        if self.env.is_over():
            print(self.env.get_payoffs())
            return self.env.get_payoffs()
        elif this_player == curr_player: 
            print("Is current Player")
            self.infosets = collections.defaultdict(list)
            probs = np.ones(self.env.player_num)
            self.traverse_tree(probs, this_player)
            action = self.best_response_action(this_player, state['obs'].tostring())
            q_val = self.get_q_value(action, [0.0, 0.0])
            return q_val[this_player]
        else:
            print("Not current Player")
            action_probs = self.action_probs(state, self.opponent_policy)
            sum_qval = np.array([0.0, 0.0])
            for a, p in enumerate(self.action_probs(state, self.opponent_policy)):
                q_val = self.get_q_value(a, [0.0, 0.0])
                weighted_qval = np.array([q*p for q in q_val])
                sum_qval += weighted_qval
            return sum_qval[this_player]

    def get_q_value(self, action, q_value):
        if self.env.is_over():
            return self.env.get_payoffs()
        current_player = self.env.get_player_id()
        obs, legal_actions = self.get_state(current_player)
        curr_state = self.env.get_state(current_player)
        action_probs = self.action_probs(curr_state, self.opponent_policy)
        for act in legal_actions:
            self.env.step(act)
            q_val_out = q_value.copy()
            curr_qval = np.array(self.get_q_value(act, q_value))
            q_val_out += curr_qval * action_probs[act]
            #q_value += self.get_q_value(act, q_value)
            self.env.step_back()
        return q_val_out

    def best_response_action(self, this_player, obs):
        infoset = self.infosets[obs]
        best_act = ""
        max_value = -1000.0
        for each in infoset:
            p, legal_act = each[0]
            cf_p = each[1]
            q_value = [0.0, 0.0]
            for a in legal_act:
                self.env.step(a)
                q_value = self.get_q_value(a, q_value)
                self.env.step_back()
                tmp_q = cf_p * q_value[this_player]
                if tmp_q > max_value:
                    max_value = tmp_q
                    best_act = a
        return best_act

    def action_probs(self, state, policy):
        ''' Obtain the action probabilities of the current state

        Args:
            state(dictionaty): The state dictionary
            policy (dict): The used policy

        Returns:
            (tuple) that contains:
                action_probs(numpy.array): The action probabilities
                legal_actions (list): Indices of legal actions
        '''
        #obs = state['obs']
        legal_actions = state['legal_actions']

        _, action_probs = policy.eval_step(state)
        if action_probs != []:
            action_probs = np.array(action_probs)
            action_probs = remove_illegal(action_probs, legal_actions)
        else:
            action_probs = [1.0/len(legal_actions) if a in legal_actions else 0.0 for a in range(self.env.action_num)]
            #action_probs = [1.0/self.env.action_num for i in range(self.env.action_num)]
        return action_probs

    def eval_step(self, state):
        ''' Given a state, predict action based on average policy

        Args:
            state (numpy.array): State representation

        Returns:
            action (int): Predicted action
        '''
        #probs = self.action_probs(state['obs'].tostring(), state['legal_actions'], self.average_policy)
        this_player = self.env.get_player_id()
        self.infosets = collections.defaultdict(list)
        probs = np.ones(self.env.player_num)
        self.tmp_state = state['obs']
        obs, legal_act = self.get_state(this_player)
        self.traverse_tree(probs, this_player)
        act = self.best_response_action(this_player, state['obs'].tostring())
        return act, []

    def get_state(self, player_id):
        ''' Get state_str of the player

        Args:
            player_id (int): The player id

        Returns:
            (tuple) that contains:
                state (str): The state str
                legal_actions (list): Indices of legal actions
        '''
        state = self.env.get_state(player_id)
        return state['obs'].tostring(), state['legal_actions']

    def save(self):
        ''' Save model
        '''
        if not os.path.exists(self.model_path):
            os.makedirs(self.model_path)

        policy_file = open(os.path.join(self.model_path, 'policy.pkl'),'wb')
        pickle.dump(self.policy, policy_file)
        policy_file.close()

        average_policy_file = open(os.path.join(self.model_path, 'average_policy.pkl'),'wb')
        pickle.dump(self.average_policy, average_policy_file)
        average_policy_file.close()

        regrets_file = open(os.path.join(self.model_path, 'regrets.pkl'),'wb')
        pickle.dump(self.regrets, regrets_file)
        regrets_file.close()

        iteration_file = open(os.path.join(self.model_path, 'iteration.pkl'),'wb')
        pickle.dump(self.iteration, iteration_file)
        iteration_file.close()

    def load(self):
        ''' Load model
        '''
        if not os.path.exists(self.model_path):
            return

        policy_file = open(os.path.join(self.model_path, 'policy.pkl'),'rb')
        self.policy = pickle.load(policy_file)
        policy_file.close()

        average_policy_file = open(os.path.join(self.model_path, 'average_policy.pkl'),'rb')
        self.average_policy = pickle.load(average_policy_file)
        average_policy_file.close()

        regrets_file = open(os.path.join(self.model_path, 'regrets.pkl'),'rb')
        self.regrets = pickle.load(regrets_file)
        regrets_file.close()

        iteration_file = open(os.path.join(self.model_path, 'iteration.pkl'),'rb')
        self.iteration = pickle.load(iteration_file)
        iteration_file.close()

