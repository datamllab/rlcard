'''
    File name: rlcard/games/bauernskat/dmc_agent/utils.py
    Author: Oliver Czerwinski
    Date created: 08/15/2025
    Date last modified: 12/26/2025
    Python Version: 3.9+
'''

import logging
import time
import queue
import threading
import numpy as np
import torch
from typing import Dict, Any

import rlcard
from rlcard.agents.bauernskat import rule_agents as bauernskat_rule_agents
from rlcard.agents.bauernskat.dmc_agent.agent import AgentDMC_Actor

from rlcard.agents.bauernskat.dmc_agent.config import MAX_TRICK_SIZE, MAX_CEMETERY_SIZE

def setup_logging(level=logging.INFO):
    """
    Prepares the logging.
    """
    
    logger = logging.getLogger('agent_dmc_trainer')
    if logger.hasHandlers():
        return

    logger.setLevel(level)
    shandle = logging.StreamHandler()
    shandle.setFormatter(
        logging.Formatter(
            '[%(levelname)s:%(process)d %(module)s:%(lineno)d %(asctime)s] '
            '%(message)s'))
    logger.addHandler(shandle)
    logger.propagate = False

class ObsPreprocessor:
    """
    Preprocesses observations for the DMC agent.
    """
    
    def __init__(self):
        """
        Initialized ObsPreprocessor.
        """
        
        self.pad_keys = {
            'trick_card_ids': MAX_TRICK_SIZE,
            'cemetery_card_ids': MAX_CEMETERY_SIZE,
        }

    def _pad_obs(self, obs_dict: Dict) -> Dict:
        """
        Pads observation of different lengths to a fixed size.
        """
        
        padded_dict = obs_dict.copy()
        
        for key, max_len in self.pad_keys.items():
            if key in padded_dict:
                original_list = padded_dict[key]
                padding_needed = max_len - len(original_list)
                if padding_needed > 0:
                    padded_dict[key] = original_list + [-1] * padding_needed
        
        return padded_dict

    def _prepare_for_tensordict(self, data: Dict) -> Dict:
        """
        Converts a list to a numpy array for tensordict compatibility.
        """
        
        for key, value in data.items():
            if isinstance(value, dict):
                self._prepare_for_tensordict(value)
            elif isinstance(value, list):
                data[key] = np.array(value, dtype=np.int32)
            elif isinstance(value, np.ndarray) and value.dtype == np.float64:
                data[key] = value.astype(np.float32)
        
        return data

    def __call__(self, obs_or_sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pads and converts for tensordict compatibility.
        """
        
        if 'observation' in obs_or_sample:
            obs_or_sample['observation'] = self._pad_obs(obs_or_sample['observation'])
            if 'next' in obs_or_sample and 'observation' in obs_or_sample['next']:
                obs_or_sample['next']['observation'] = self._pad_obs(obs_or_sample['next']['observation'])
            return self._prepare_for_tensordict(obs_or_sample)
        else:
            padded_obs = self._pad_obs(obs_or_sample)
            return self._prepare_for_tensordict(padded_obs)


class TrainingLogger:
    """
    Handles logging during training.
    """
    
    def __init__(self, trainer_instance):
        """
        Initializes TrainingLogger.
        """
        
        self.config = trainer_instance.config
        self.plogger = trainer_instance.plogger
        self.writer = trainer_instance.writer
        self.log_queue = trainer_instance.log_queue
        self.shutdown_event = trainer_instance.shutdown_event
        self.replay_buffer = trainer_instance.replay_buffer
        self.buffer_lock = trainer_instance.buffer_lock
        self.avg_p0_payoff = trainer_instance.avg_p0_payoff
        self.dropped_batches_total = trainer_instance.dropped_batches_total
        self.total_elapsed_time = trainer_instance.total_elapsed_time
        
        self.current_epsilon = trainer_instance.current_epsilon
        self.current_teacher_eps = trainer_instance.current_teacher_eps
        self.current_trump_prob = trainer_instance.current_trump_prob

        self.thread = None
        self.log = logging.getLogger('agent_dmc_trainer')

    def start(self):
        """
        Starts a logging thread.
        """
        
        self.thread = threading.Thread(target=self._log_worker, daemon=True)
        self.thread.start()

    def stop(self):
        """
        Stops the logging thread.
        """
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=self.config.process_join_timeout)

    def _log_worker(self):
        """
        Processes log records from a queue.
        """
        
        payoff_buffer = []
        last_log_time = time.time()
        
        latest_frames, latest_loss, latest_mean_q, latest_lr = 0, 0.0, 0.0, 0.0

        def perform_log():
            nonlocal payoff_buffer, last_log_time
            if latest_frames > 0:
                with self.buffer_lock:
                    buffer_size = len(self.replay_buffer)

                log_data = {
                    'Training/frames': latest_frames, 
                    'Training/loss': latest_loss,
                    'Training/mean_q_values': latest_mean_q, 
                    'Training/learning_rate': latest_lr,
                    'Performance/buffer_size': buffer_size, 
                    'Performance/total_dropped_batches': self.dropped_batches_total.value,
                    'Performance/total_training_time_hours': self.total_elapsed_time.value / 3600.0,
                    'Exploration/Random-epsilon': self.current_epsilon.value,
                }

                if self.config.use_teacher_forcing:
                    log_data['Exploration/Teacher-epsilon'] = self.current_teacher_eps.value
                
                if self.config.use_rule_based_trump_decay:
                    log_data['Exploration/Trump-epsilon'] = self.current_trump_prob.value
                
                if payoff_buffer:
                    avg_payoff = np.mean(payoff_buffer)
                    self.avg_p0_payoff.value = avg_payoff
                    log_data['Performance/avg_p0_payoff_5s'] = avg_payoff
                    log_data['Performance/total_games_in_5s'] = len(payoff_buffer)
                    payoff_buffer = []

                self.plogger.log(log_data)
                if self.writer:
                    for key, value in log_data.items():
                        if key not in ['_tick', '_time']:
                            self.writer.add_scalar(key, value, latest_frames)
            
            last_log_time = time.time()

        while not self.shutdown_event.is_set():
            try:
                record = self.log_queue.get(timeout=1.0)
                if record is None: break
                
                if record.get('type') == 'train_stats':
                    latest_frames = record.get('frames', latest_frames)
                    latest_loss = record.get('loss', latest_loss)
                    latest_mean_q = record.get('mean_q', latest_mean_q)
                    latest_lr = record.get('learning_rate', latest_lr)
                else:
                    payoff_buffer.append(record['p0_payoff'])

            except queue.Empty:
                continue
            except (KeyboardInterrupt, EOFError):
                break

            if time.time() - last_log_time >= self.config.log_interval_seconds:
                perform_log()
        
        perform_log()
        self.log.info("Log worker terminated.")


class AgentEvaluator:
    """
    Evaluates the agent against multiple rule-based agents.
    """
    
    def __init__(self, config):
        """
        Initializes AgentEvaluator.
        """
        
        self.config = config
        self.log = logging.getLogger('agent_dmc_trainer')
        self.opponents = {
            'Random': bauernskat_rule_agents.BauernskatRandomRuleAgent(),
            'Frugal': bauernskat_rule_agents.BauernskatFrugalRuleAgent(),
            'Lookahead': bauernskat_rule_agents.BauernskatLookaheadRuleAgent(),
            'SHOT': bauernskat_rule_agents.BauernskatSHOTAlphaBetaRuleAgent()
        }
    
    def evaluate(self, eval_net, current_frames, writer):
        """
        Evaluates the agent against all opponents.
        """
        
        self.log.info("Starting Evaluation Run...")
        
        with torch.no_grad():
            eval_agent = AgentDMC_Actor(eval_net, self.config.device, use_teacher=False)
            
            eval_env_config = {
                'seed': 500,
                'information_level': self.config.information_level
            }
            eval_env = rlcard.make(self.config.env, config=eval_env_config)
            
            total_p0_wins, total_p1_wins, total_p0_payoff, total_p1_payoff = 0, 0, 0.0, 0.0
            total_games_as_p0, total_games_as_p1 = 0, 0

            win_rates_by_opponent = {}
            avg_rewards_by_opponent = {}

            for name, opponent in self.opponents.items():
                games_per_opponent_half = self.config.num_eval_games // (2 * len(self.opponents))
                
                eval_env.set_agents([eval_agent, opponent])
                p0_wins, p0_payoff = self._run_half(eval_env, games_per_opponent_half, agent_pos=0)
                
                eval_env.set_agents([opponent, eval_agent])
                p1_wins, p1_payoff = self._run_half(eval_env, games_per_opponent_half, agent_pos=1)
                
                # Accumulate stats
                total_p0_wins += p0_wins
                total_p0_payoff += p0_payoff
                total_games_as_p0 += games_per_opponent_half
                total_p1_wins += p1_wins
                total_p1_payoff += p1_payoff
                total_games_as_p1 += games_per_opponent_half
                
                # Individual Opponent Stats
                p0_win_rate = p0_wins / games_per_opponent_half if games_per_opponent_half > 0 else 0
                p0_avg_reward = p0_payoff / games_per_opponent_half if games_per_opponent_half > 0 else 0
                p1_win_rate = p1_wins / games_per_opponent_half if games_per_opponent_half > 0 else 0
                p1_avg_reward = p1_payoff / games_per_opponent_half if games_per_opponent_half > 0 else 0
                self.log.info(f"  vs {name}: P0 [WR: {p0_win_rate:.1%}, AvgR: {p0_avg_reward:+.2f}] | P1 [WR: {p1_win_rate:.1%}, AvgR: {p1_avg_reward:+.2f}]")

                # Combined Stats for specific opponent
                total_games_this_opponent = games_per_opponent_half * 2
                if total_games_this_opponent > 0:
                    combined_win_rate = (p0_wins + p1_wins) / total_games_this_opponent
                    combined_avg_reward = (p0_payoff + p1_payoff) / total_games_this_opponent
                    win_rates_by_opponent[name] = combined_win_rate
                    avg_rewards_by_opponent[name] = combined_avg_reward

            # Overall Stats
            overall_p0_win_rate = total_p0_wins / total_games_as_p0 if total_games_as_p0 > 0 else 0
            overall_p1_win_rate = total_p1_wins / total_games_as_p1 if total_games_as_p1 > 0 else 0
            overall_p0_avg_reward = total_p0_payoff / total_games_as_p0 if total_games_as_p0 > 0 else 0.0
            overall_p1_avg_reward = total_p1_payoff / total_games_as_p1 if total_games_as_p1 > 0 else 0.0
            
            self.log.info(f"Overall Factual -> P0 [WR: {overall_p0_win_rate:.1%}, AvgR: {overall_p0_avg_reward:+.2f}] | P1 [WR: {overall_p1_win_rate:.1%}, AvgR: {overall_p1_avg_reward:+.2f}]")
            
            if writer:
                writer.add_scalar('Evaluation/overall_p0_win_rate', overall_p0_win_rate, current_frames)
                writer.add_scalar('Evaluation/overall_p1_win_rate', overall_p1_win_rate, current_frames)
                writer.add_scalar('Evaluation/overall_p0_avg_reward', overall_p0_avg_reward, current_frames)
                writer.add_scalar('Evaluation/overall_p1_avg_reward', overall_p1_avg_reward, current_frames)

                if win_rates_by_opponent:
                    writer.add_scalars('Evaluation/Combined_WinRate_vs_Opponent', win_rates_by_opponent, current_frames)
                
                if avg_rewards_by_opponent:
                    writer.add_scalars('Evaluation/Combined_AvgR_vs_Opponent', avg_rewards_by_opponent, current_frames)

    def _run_half(self, env, num_games, agent_pos):
        """
        Runs games in a specified player role.
        """
        
        total_wins = 0
        total_payoff = 0.0
        agent = env.agents[agent_pos]
        opponent = env.agents[1 - agent_pos]

        for _ in range(num_games):
            state, player_id = env.reset()
            
            while not env.is_over():
                if player_id == agent_pos:
                    action, _ = agent.eval_step(state, env)
                else:
                    action = opponent.step(state)
                state, player_id = env.step(action)
            payoffs = env.get_payoffs()
            total_payoff += payoffs[agent_pos]
            
            if payoffs[agent_pos] > 0:
                total_wins += 1
        
        return total_wins, total_payoff