'''
    File name: rlcard/games/bauernskat/sac_agent/trainer.py
    Author: Oliver Czerwinski
    Date created: 11/10/2025
    Date last modified: 12/26/2025
    Python Version: 3.9+
'''

import os
import pprint
import threading
import time
import datetime
import traceback
import copy
import csv
import json
import logging
import dataclasses
import random
import argparse
import queue
from typing import Dict, Any, Literal, get_origin, get_args
from multiprocessing.synchronize import Lock as LockType
from multiprocessing.queues import Queue as QueueType
from multiprocessing.sharedctypes import Synchronized as SynchronizedType

import numpy as np
import torch
from torch import multiprocessing as mp
from torch import nn
from torch.utils.tensorboard import SummaryWriter

from torchrl.data import TensorDictReplayBuffer, LazyTensorStorage
from torchrl.data.replay_buffers.samplers import PrioritizedSampler
from tensordict import TensorDict

import rlcard
from rlcard.agents.bauernskat.sac_agent.config import TrainerConfig
from rlcard.agents.bauernskat.sac_agent.model import BauernskatNet
from rlcard.agents.bauernskat.sac_agent.agent import SACEstimator, AgentSAC_Actor
from rlcard.agents.bauernskat.sac_agent.utils import ObsPreprocessor, setup_logging, TrainingLogger, AgentEvaluator
from rlcard.agents.bauernskat.sac_agent.reward import calculate_hybrid_reward, calculate_binary_reward, calculate_game_score_reward


log = logging.getLogger('agent_sac_trainer')

def format_time(seconds: float) -> str:
    """
    Formats seconds into a HH:MM:SS.
    """
    
    return str(datetime.timedelta(seconds=int(seconds)))

def gather_metadata(config: TrainerConfig) -> Dict:
    """
    Gathers metadata about the training run.
    """
    
    date_start = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    
    slurm_data = {k.replace('SLURM_', '').lower(): v for k, v in os.environ.items() if k.startswith('SLURM')} or None
    env_whitelist = ('USER', 'HOSTNAME')
    safe_env = {k: v for k, v in os.environ.items() if k.startswith('SLURM') or k in env_whitelist}
    
    def custom_dict_factory(data):
        """
        Handles non-serializable types in dataclasses.
        """
        
        return {k: str(v) if isinstance(v, torch.device) else v for k, v in data}

    config_dict = dataclasses.asdict(config, dict_factory=custom_dict_factory)
    
    return dict(date_start=date_start, date_end=None, successful=False, 
                slurm=slurm_data, env=safe_env, config=config_dict)


class FileWriter:
    """
    Handles logging to files and saving metadata.
    """
    
    def __init__(self, xpid: str, rootdir: str, config: TrainerConfig):
        """
        Initializes FileWriter.
        """
        
        self.xpid = xpid
        self._tick = 0
        self.metadata = gather_metadata(config)
        self.metadata['xpid'] = self.xpid
        
        self._logger = logging.getLogger(f'filewriter/{self.xpid}')
        self._logger.setLevel(logging.INFO)
        self._logger.propagate = False
        
        self.basepath = os.path.join(os.path.expandvars(os.path.expanduser(rootdir)), self.xpid)
        os.makedirs(self.basepath, exist_ok=True)
        
        self.paths = {
            'msg': f'{self.basepath}/out.log', 'logs': f'{self.basepath}/logs.csv',
            'fields': f'{self.basepath}/fields.csv', 'meta': f'{self.basepath}/meta.json'}
        
        self._save_metadata()
        
        fhandle = logging.FileHandler(self.paths['msg'])
        fhandle.setFormatter(logging.Formatter('%(message)s'))
        self._logger.addHandler(fhandle)

        self.fieldnames = ['_tick', '_time']
        
        if os.path.exists(self.paths['logs']):
            with open(self.paths['fields'], 'r') as csvfile:
                self.fieldnames = list(csv.reader(csvfile))[0]

    def log(self, to_log: Dict):
        """
        Logs values to a CSV file.
        """
        
        to_log.update({'_tick': self._tick, '_time': time.time()})
        self._tick += 1
        
        new_fields = any(k not in self.fieldnames for k in to_log)
        
        if new_fields:
            self.fieldnames.extend(k for k in to_log if k not in self.fieldnames)
            with open(self.paths['fields'], 'w') as f:
                csv.writer(f).writerow(self.fieldnames)
        
        if to_log['_tick'] == 1:
            with open(self.paths['logs'], 'a') as f:
                f.write(f'# {",".join(self.fieldnames)}\n')
        
        self._logger.info(f'LOG | {", ".join([f"{k}: {v}" for k,v in sorted(to_log.items())])}')
        
        with open(self.paths['logs'], 'a') as f:
            csv.DictWriter(f, fieldnames=self.fieldnames).writerow(to_log)

    def close(self, successful: bool = True):
        """
        Closes the FileWriter and saves final metadata.
        """
        
        self.metadata['date_end'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.metadata['successful'] = successful
        
        self._save_metadata()
        
        for handler in self._logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                self._logger.removeHandler(handler)

    def _save_metadata(self):
        """
        Saves metadata to a JSON file.
        """
        
        with open(self.paths['meta'], 'w') as f:
            json.dump(self.metadata, f, indent=4, sort_keys=True)


def act(actor_id: int, 
        config: TrainerConfig, 
        actor_model: nn.Module, 
        sample_queue: QueueType,
        log_queue: QueueType,
        shared_trump_prob: SynchronizedType,
        shared_teacher_eps: SynchronizedType,
        dropped_batches_counter: SynchronizedType,
        start_seed_offset: int):
    """
    Main loop for an actor process.
    """
    
    setup_logging()
    
    seed = config.seed + actor_id + start_seed_offset
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    log = logging.getLogger('agent_sac_trainer')
    obs_preprocessor = ObsPreprocessor()

    try:
        log.info(f'Actor {actor_id} started (seed={seed}).')
        env_config = {
            'seed': seed,
            'information_level': config.information_level}
        env = rlcard.make(config.env, config=env_config)
        
        agent = AgentSAC_Actor(actor_model, 'cpu', use_teacher=config.use_teacher_forcing)
        
        # Main loop
        while True:
            aggregated_samples = []
            for _ in range(config.actor_game_batch_size):
                trajectories = {p_id: [] for p_id in range(env.num_players)}
                state, player_id = env.reset()
                
                while not env.is_over():
                    action_id, legal_keys = agent.step(state, env, 
                                                    trump_rule_prob=shared_trump_prob.value,
                                                    teacher_epsilon=shared_teacher_eps.value)
                    
                    sac_idx = 32 + action_id if action_id < 5 else action_id - 5
                    
                    trajectories[player_id].append((state['obs'], sac_idx, legal_keys))
                    state, player_id = env.step(action_id)
                
                # Reward Calculation
                final_scores = env.get_payoffs()
                final_pips = env.get_scores()
                payoffs = np.zeros(2, dtype=np.float32)

                if config.reward_type == 'hybrid':
                    payoffs[0] = calculate_hybrid_reward(final_pips[0], final_pips[1], final_scores[0],
                        config.reward_shaping_steepness, config.reward_shaping_threshold, 
                        config.reward_shaping_score_weight, config.reward_shaping_win_bonus)
                    payoffs[1] = calculate_hybrid_reward(final_pips[1], final_pips[0], final_scores[1],
                        config.reward_shaping_steepness, config.reward_shaping_threshold, 
                        config.reward_shaping_score_weight, config.reward_shaping_win_bonus)
                elif config.reward_type == 'binary':
                    payoffs[0] = calculate_binary_reward(final_scores[0])
                    payoffs[1] = calculate_binary_reward(final_scores[1])
                elif config.reward_type == 'game_score':
                    payoffs[0] = calculate_game_score_reward(final_scores[0])
                    payoffs[1] = calculate_game_score_reward(final_scores[1])

                if config.log_p0_p1_payoffs:
                    log_queue.put({'p0_payoff': env.get_payoffs()[0], 'p1_payoff': env.get_payoffs()[1]})

                # N-Step Return
                for p_id, trajectory in trajectories.items():
                    if not trajectory: continue
                    
                    G = float(payoffs[p_id])
                    traj_len = len(trajectory)
                    
                    for i in range(traj_len):
                        obs, act_idx, legal_keys = trajectory[i]
                        n_step_end_idx = i + config.n_step_returns
                        
                        if n_step_end_idx < traj_len:
                            reward = 0.0 
                            done = False
                            next_obs, _, next_legal_keys = trajectory[n_step_end_idx]
                        else:
                            steps_to_end = (traj_len - 1) - i
                            reward = G * (config.gamma ** steps_to_end)
                            done = True
                            next_obs, _, next_legal_keys = trajectory[-1] 

                        sample = {
                            "observation": obs,
                            "action": [act_idx],
                            "legal_keys": legal_keys,
                            "next": {
                                "observation": next_obs,
                                "reward": [reward],
                                "done": [done],
                                "legal_keys": next_legal_keys
                            }
                        }
                        
                        processed_sample = obs_preprocessor(sample)
                        aggregated_samples.append(processed_sample)

            if aggregated_samples:
                try:
                    sample_queue.put(aggregated_samples, timeout=config.sample_queue_put_timeout)
                except queue.Full:
                    with dropped_batches_counter.get_lock():
                        dropped_batches_counter.value += 1

    except KeyboardInterrupt:
        log.info(f"Actor {actor_id} interrupted.")
    except Exception as e:
        log.error(f'Exception in actor process {actor_id}: {e}\n{traceback.format_exc()}')
        raise e


def learn(config: TrainerConfig,
        estimator: SACEstimator,
        actor_model: nn.Module,
        replay_buffer: TensorDictReplayBuffer,
        frames_counter: SynchronizedType,
        learner_lock: LockType,
        buffer_lock: LockType,
        log_queue: QueueType,
        latest_critic_loss: SynchronizedType,
        latest_actor_loss: SynchronizedType,
        latest_alpha: SynchronizedType,
        latest_mean_q: SynchronizedType,
        latest_lr: SynchronizedType):
    """ 
    Main loop for a learner thread. 
    """
    
    last_log_frame = 0

    while frames_counter.value < config.total_frames:
        with buffer_lock:
            if len(replay_buffer) < config.min_buffer_size_to_learn:
                time.sleep(1)
                continue
            try:
                batch = replay_buffer.sample(config.batch_size)
            except Exception:
                time.sleep(0.1)
                continue
        
        # Training step
        with learner_lock:
            c_loss, a_loss, alpha, mean_q, lr = estimator.train_step(batch, config.gradient_clip_norm)
            
            estimator.update_target_net()

            # Sync actor model
            with torch.no_grad():
                for p_learner, p_actor in zip(estimator.net.parameters(), actor_model.parameters()):
                    p_actor.data.copy_(p_learner.data)
            
            frames_counter.value += config.batch_size

            if frames_counter.value - last_log_frame >= config.log_every_frames:
                latest_critic_loss.value = c_loss
                latest_actor_loss.value = a_loss
                latest_alpha.value = alpha
                latest_mean_q.value = mean_q
                latest_lr.value = lr
                
                log_queue.put({ 
                    'type': 'train_stats', 
                    'frames': frames_counter.value, 
                    'critic_loss': c_loss,
                    'actor_loss': a_loss,
                    'mean_q': mean_q, 
                    'alpha': alpha,
                    'lr': lr
                })
                last_log_frame = frames_counter.value


class SACTrainer:
    """
    Trainer for the SAC agent.
    """
    
    def __init__(self, config: TrainerConfig):
        """
        Initialized SACTrainer.
        """
        
        self.config = config
        self.plogger = FileWriter(xpid=config.xpid, rootdir=config.savedir, config=self.config)
        self.writer = None
        
        if config.log_to_tensorboard:
            tb_dir = os.path.join(config.savedir, config.xpid, 'tensorboard_logs')
            self.writer = SummaryWriter(log_dir=tb_dir)
            log.info(f"TensorBoard logging to {tb_dir}")
        
        self.checkpointpath = os.path.join(os.path.expandvars(
            os.path.expanduser(config.savedir)), config.xpid, "model.tar")
        
        self.shutdown_event = threading.Event()
        self.evaluator = AgentEvaluator(self.config)
        
        self.actor_processes = []
        self.learner_thread = None
        self.logger = None
        self.ingest_thread = None

    def _setup_components(self):
        """
        Sets up multiprocessing components.
        """
        
        cfg = self.config
        self.ctx = mp.get_context('spawn')
        log.info(f"Using learner device: {cfg.device}")

        self.estimator = SACEstimator(cfg.model_config, cfg, device=cfg.device)

        self.actor_model = BauernskatNet(cfg.model_config).to('cpu')
        self.actor_model.share_memory()
        self.actor_model.eval()
    
        self.sample_queue = self.ctx.Queue(maxsize=cfg.num_actors * cfg.actor_queue_size_multiplier)
        self.log_queue = self.ctx.Queue()
        
        self.frames = self.ctx.Value('Q', 0)
        self.learner_lock = self.ctx.Lock()
        self.buffer_lock = self.ctx.Lock()
        self.avg_p0_payoff = self.ctx.Value('f', 0.0)
        self.dropped_batches_total = self.ctx.Value('Q', 0)
        self.total_elapsed_time = self.ctx.Value('d', 0.0)
        
        # Logging shared variables
        self.latest_critic_loss = self.ctx.Value('f', 0.0)
        self.latest_actor_loss = self.ctx.Value('f', 0.0)
        self.latest_alpha = self.ctx.Value('f', cfg.initial_alpha)
        self.latest_mean_q = self.ctx.Value('f', 0.0)
        self.latest_lr = self.ctx.Value('f', cfg.critic_lr)

        self.current_teacher_eps = self.ctx.Value('f', cfg.teacher_start if cfg.use_teacher_forcing else 0.0)
        self.current_trump_prob = self.ctx.Value('f', cfg.trump_start if cfg.use_rule_based_trump_decay else 0.0)

        sampler = PrioritizedSampler(max_capacity=cfg.replay_buffer_size, alpha=cfg.per_alpha, beta=cfg.per_beta)
        self.replay_buffer = TensorDictReplayBuffer(
            storage=LazyTensorStorage(max_size=cfg.replay_buffer_size),
            sampler=sampler, batch_size=cfg.batch_size)
        
        log.info("Seeding replay buffer schema...")
        
        try:
            obs_preprocessor = ObsPreprocessor()
            temp_env = rlcard.make(cfg.env, config={'seed': 999})
            temp_agent = AgentSAC_Actor(self.actor_model, 'cpu')
            state, _ = temp_env.reset()
            act_id, legal_keys = temp_agent.step(state, temp_env)
            act_idx = 32 + act_id if act_id < 5 else act_id - 5
            
            dummy_sample = {
                "observation": state['obs'], 
                "action": [act_idx], 
                "legal_keys": legal_keys,
                "next": {
                    "observation": state['obs'], 
                    "reward": [0.0], 
                    "done": [False], 
                    "legal_keys": legal_keys
                }
            }
            self.replay_buffer.add(TensorDict(obs_preprocessor(dummy_sample), batch_size=[]))
            self.replay_buffer.empty()
            
            log.info("Replay buffer seeded.")
        except Exception as e:
            log.error(f"Failed to seed buffer: {e}")
            raise

        # Load model
        if cfg.load_model and os.path.exists(self.checkpointpath):
            log.info(f"Loading checkpoint from {self.checkpointpath}")
            checkpoint = torch.load(self.checkpointpath, map_location=cfg.device, weights_only=False)
            
            self.estimator.net.load_state_dict(checkpoint['model_state_dict'])
            self.estimator.target_net.load_state_dict(checkpoint['target_state_dict'])
            self.estimator.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            
            if 'alpha_log' in checkpoint and hasattr(self.estimator, 'log_alpha'):
                self.estimator.log_alpha.data = torch.tensor([checkpoint['alpha_log']], device=cfg.device)
                self.estimator.alpha = self.estimator.log_alpha.exp()
            if hasattr(self.estimator, 'alpha_optim') and 'alpha_optim_state_dict' in checkpoint:
                self.estimator.alpha_optim.load_state_dict(checkpoint['alpha_optim_state_dict'])
            
            if hasattr(self.estimator, 'scheduler') and 'scheduler_state_dict' in checkpoint:
                self.estimator.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

            self.frames.value = checkpoint.get('frames', 0)
            self.total_elapsed_time.value = checkpoint.get('total_elapsed_time', 0.0)
            self.avg_p0_payoff.value = checkpoint.get('avg_p0_payoff', 0.0)

            if 'rng_states' in checkpoint:
                rng_states = checkpoint['rng_states']
                try:
                    torch.set_rng_state(rng_states['torch'].cpu())
                    if torch.cuda.is_available() and rng_states['cuda'] is not None:
                        torch.cuda.set_rng_state_all(rng_states['cuda'])
                    np.random.set_state(rng_states['numpy'])
                    random.setstate(rng_states['python'])
                    log.info("RNG states restored.")
                except Exception as e:
                    log.warning(f"Failed to restore RNG states: {e}")
            
            log.info(f"Resumed from {self.frames.value} frames.")
            
            # Initial sync of actor model
            with torch.no_grad():
                for p_l, p_a in zip(self.estimator.net.parameters(), self.actor_model.parameters()):
                    p_a.data.copy_(p_l.data)

    def _sample_ingest_worker(self):
        """
        Ingests samples from the sample queue into the replay buffer.
        """
        
        log.info("Sample ingest worker started.")
        
        while not self.shutdown_event.is_set():
            try:
                batch = self.sample_queue.get(timeout=1.0)
                if batch is None: break
                
                with self.buffer_lock:
                    for s in batch:
                        self.replay_buffer.add(TensorDict(s, batch_size=[]))
            except queue.Empty:
                continue
            except (KeyboardInterrupt, EOFError):
                break

    def start(self):
        """
        Starts the training process.
        """
        
        self._setup_components()
        
        self.logger = TrainingLogger(self)
        self.logger.start()

        self.ingest_thread = threading.Thread(target=self._sample_ingest_worker, daemon=True)
        self.ingest_thread.start()

        self.actor_processes = [
            self.ctx.Process(target=act, args=(i, self.config, self.actor_model, 
            self.sample_queue, self.log_queue, self.current_trump_prob, self.current_teacher_eps, 
            self.dropped_batches_total, int(self.frames.value))) 
            for i in range(self.config.num_actors)
        ]
        for p in self.actor_processes: p.start()

        self.learner_thread = threading.Thread(target=learn, args=(
            self.config, self.estimator, self.actor_model, self.replay_buffer, 
            self.frames, self.learner_lock, self.buffer_lock, self.log_queue,
            self.latest_critic_loss, self.latest_actor_loss, self.latest_alpha,
            self.latest_mean_q, self.latest_lr
        ))
        self.learner_thread.start()
        
        try:
            last_checkpoint_frame = self.frames.value
            last_eval_frame = self.frames.value
            resumed_time = self.total_elapsed_time.value
            start_time = time.time()
            
            while self.frames.value < self.config.total_frames:
                time.sleep(1)
                current_frames = self.frames.value
                self.total_elapsed_time.value = resumed_time + (time.time() - start_time)
                
                # Trump Decay
                if self.config.use_rule_based_trump_decay:
                    ratio = min(1.0, current_frames / self.config.trump_decay_frames)
                    self.current_trump_prob.value = self.config.trump_start - (self.config.trump_start - self.config.trump_end) * ratio
                
                # Teacher Forcing Decay
                if self.config.use_teacher_forcing:
                    ratio = min(1.0, current_frames / self.config.teacher_decay_frames)
                    self.current_teacher_eps.value = self.config.teacher_start - (self.config.teacher_start - self.config.teacher_end) * ratio

                with self.buffer_lock: mem_size = len(self.replay_buffer)
                
                print(f"\rTime: {format_time(self.total_elapsed_time.value)} | "
                    f"Step: {current_frames/1e6:.2f}M/{self.config.total_frames/1e6:.1f}M | "
                    f"Mem: {mem_size/1e3:.1f}k | "
                    f"Teacher-ε: {self.current_teacher_eps.value:.4f} | "
                    f"Trump-ε: {self.current_trump_prob.value:.4f} | "
                    f"Alpha: {self.latest_alpha.value:.4f} | "
                    f"LR: {self.latest_lr.value:.3e} | "
                    f"ØQ: {self.latest_mean_q.value:+.4f} | "
                    f"C-Loss: {self.latest_critic_loss.value:.4f} | "
                    f"ØPayoff: {self.avg_p0_payoff.value:+.2f}", end="", flush=True)

                if current_frames - last_checkpoint_frame >= self.config.save_every_frames:
                    self.checkpoint()
                    last_checkpoint_frame = current_frames
                
                # Evaluation
                if current_frames - last_eval_frame >= self.config.eval_every:
                    print()
                    eval_net = copy.deepcopy(self.estimator.net).to('cpu')
                    self.evaluator.evaluate(eval_net, current_frames, self.writer)
                    last_eval_frame = current_frames
        
        except KeyboardInterrupt:
            print("\nTraining interrupted.")
        finally:
            print("\nShutting down...")
            
            self.shutdown_event.set()
            
            for p in self.actor_processes:
                if p.is_alive(): p.terminate(); p.join(timeout=1.0)
            
            if self.ingest_thread.is_alive(): self.ingest_thread.join(timeout=1.0)
            if self.logger: self.logger.stop()
            
            self.checkpoint()
            
            self.plogger.close()
            if self.writer: self.writer.close()

    def checkpoint(self):
        """
        Saves the current model checkpoint.
        """
        
        log.info(f"Saving checkpoint to {self.checkpointpath}")
        
        rng_states = {
            'torch': torch.get_rng_state(),
            'cuda': torch.cuda.get_rng_state_all() if torch.cuda.is_available() else None,
            'numpy': np.random.get_state(),
            'python': random.getstate()
        }

        checkpoint = {
            'model_state_dict': self.estimator.net.state_dict(),
            'target_state_dict': self.estimator.target_net.state_dict(),
            'optimizer_state_dict': self.estimator.optimizer.state_dict(),
            'frames': self.frames.value,
            'total_elapsed_time': self.total_elapsed_time.value,
            'avg_p0_payoff': self.avg_p0_payoff.value,
            'rng_states': rng_states,
            'config': self.config
        }
        
        if hasattr(self.estimator, 'log_alpha'):
            checkpoint['alpha_log'] = self.estimator.log_alpha.item()
        if hasattr(self.estimator, 'alpha_optim'):
            checkpoint['alpha_optim_state_dict'] = self.estimator.alpha_optim.state_dict()
        if hasattr(self.estimator, 'scheduler'):
            checkpoint['scheduler_state_dict'] = self.estimator.scheduler.state_dict()
            
        torch.save(checkpoint, self.checkpointpath)
        
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bkp = os.path.join(os.path.dirname(self.checkpointpath), f"model_{ts}_frame{self.frames.value}.tar")
        torch.save(checkpoint, bkp)

        inference_checkpoint = {
            'model_state_dict': self.estimator.net.state_dict(),
            'config': self.config
        }
        inf_path = os.path.join(os.path.dirname(self.checkpointpath), "inference_model.pt")
        inf_bkp_path = os.path.join(os.path.dirname(self.checkpointpath), f"inference_model_{ts}_frame{self.frames.value}.pt")
        
        torch.save(inference_checkpoint, inf_path)
        torch.save(inference_checkpoint, inf_bkp_path)
        log.info(f"Saved inference checkpoint to {inf_path}")


def main():
    """
    Main function to run the SAC trainer.
    """
    
    try:
        mp.set_start_method('spawn', force=True)
    except RuntimeError:
        pass

    setup_logging()
    parser = argparse.ArgumentParser("Agent SAC Trainer for RLCard")
    
    for field in dataclasses.fields(TrainerConfig):
        if not field.init or field.name == "model_config": continue
        
        if field.type == bool:
            if field.default:
                parser.add_argument(f'--no-{field.name}', dest=field.name, action='store_false')
            else:
                parser.add_argument(f'--{field.name}', dest=field.name, action='store_true')
            
            parser.set_defaults(**{field.name: field.default})
        else:
            kwargs = {'type': field.type, 'default': field.default}
            
            if get_origin(field.type) is Literal:
                kwargs['choices'] = get_args(field.type)
                kwargs['type'] = type(kwargs['choices'][0])
            
            parser.add_argument(f'--{field.name}', **kwargs)
    
    args = parser.parse_args()
    config = TrainerConfig(**vars(args))
    os.environ["CUDA_VISIBLE_DEVICES"] = config.cuda
    
    trainer = SACTrainer(config)
    log.info(f"Starting training for {config.xpid} with config:\n{pprint.pformat(dataclasses.asdict(config))}")
    trainer.start()

if __name__ == '__main__':
    main()