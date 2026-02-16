'''
    File name: rlcard/games/bauernskat/dmc_agent/trainer.py
    Author: Oliver Czerwinski
    Date created: 08/14/2025
    Date last modified: 12/26/2025
    Python Version: 3.9+
'''

import os
import threading
import time
import datetime
import pprint
import traceback
import copy
import csv
import json
import logging
from typing import Dict, Any, Literal, get_origin, get_args
import argparse
import queue
import dataclasses
import random

import numpy as np
import torch
from torch import multiprocessing as mp
from multiprocessing.synchronize import Lock as LockType
from multiprocessing.queues import Queue as QueueType
from multiprocessing.sharedctypes import Synchronized as SynchronizedType
from torch import nn
import torch.nn.functional as F
from torch.utils.tensorboard import SummaryWriter

from torchrl.data import TensorDictReplayBuffer, LazyTensorStorage
from torchrl.data.replay_buffers.samplers import PrioritizedSampler
from tensordict import TensorDict

import rlcard

from rlcard.agents.bauernskat.dmc_agent.config import TrainerConfig
from rlcard.agents.bauernskat.dmc_agent.model import BauernskatNet
from rlcard.agents.bauernskat.dmc_agent.agent import Estimator, AgentDMC_Actor
from rlcard.agents.bauernskat.dmc_agent.utils import ObsPreprocessor, setup_logging, TrainingLogger, AgentEvaluator
from rlcard.agents.bauernskat.dmc_agent.reward import calculate_hybrid_reward, calculate_binary_reward, calculate_game_score_reward


log = logging.getLogger('agent_dmc_trainer')

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


def act(actor_id: int, config: TrainerConfig, actor_model: nn.Module, sample_queue: QueueType, 
        log_queue: QueueType, shared_epsilon: SynchronizedType, shared_trump_prob: SynchronizedType, 
        shared_teacher_eps: SynchronizedType, dropped_batches_counter: SynchronizedType):
    """
    Main loop for an actor process.
    """
    
    setup_logging()
    
    seed = config.seed + actor_id
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    log = logging.getLogger('agent_dmc_trainer')
    obs_preprocessor = ObsPreprocessor()

    try:
        log.info(f'Actor {actor_id} started.')
        
        env_config = {
            'seed': seed,
            'information_level': config.information_level}
        
        env = rlcard.make(config.env, config=env_config)
        
        agent = AgentDMC_Actor(actor_model, 'cpu', use_teacher=config.use_teacher_forcing)
        
        # Main loop
        while True:
            aggregated_samples = []
            
            for _ in range(config.actor_game_batch_size):
                trajectories = {p_id: [] for p_id in range(env.num_players)}
                state, player_id = env.reset()
                
                while not env.is_over():
                    action, action_obs = agent.step(state, env, epsilon=shared_epsilon.value, trump_rule_prob=shared_trump_prob.value, teacher_epsilon=shared_teacher_eps.value)
                    trajectories[player_id].append((state['obs'], action_obs))
                    state, player_id = env.step(action)
                
                # Reward calculation
                final_scores = env.get_payoffs()
                final_pips = env.get_scores()
                
                payoffs = np.zeros(2, dtype=np.float32)

                if config.reward_type == 'hybrid':
                    payoffs[0] = calculate_hybrid_reward(
                        my_final_pips=final_pips[0],
                        opponent_final_pips=final_pips[1],
                        final_score=final_scores[0],
                        steepness=config.reward_shaping_steepness,
                        threshold=config.reward_shaping_threshold,
                        score_weight=config.reward_shaping_score_weight,
                        win_bonus_magnitude=config.reward_shaping_win_bonus
                    )
                    payoffs[1] = calculate_hybrid_reward(
                        my_final_pips=final_pips[1],
                        opponent_final_pips=final_pips[0],
                        final_score=final_scores[1],
                        steepness=config.reward_shaping_steepness,
                        threshold=config.reward_shaping_threshold,
                        score_weight=config.reward_shaping_score_weight,
                        win_bonus_magnitude=config.reward_shaping_win_bonus
                    )
                
                elif config.reward_type == 'binary':
                    payoffs[0] = calculate_binary_reward(final_scores[0])
                    payoffs[1] = calculate_binary_reward(final_scores[1])
                    
                elif config.reward_type == 'game_score':
                    payoffs[0] = calculate_game_score_reward(final_scores[0])
                    payoffs[1] = calculate_game_score_reward(final_scores[1])
                
                if config.log_p0_p1_payoffs:
                    log_queue.put({'p0_payoff': env.get_payoffs()[0], 'p1_payoff': env.get_payoffs()[1]})

                samples_this_game = []
                
                # Monte Carlo learning
                for p_id, trajectory in trajectories.items():
                    if trajectory:
                        G = payoffs[p_id]
                        for s_obs, a_obs in trajectory:
                            sample = {"observation": s_obs, "action": a_obs,
                                    "next": { "observation": s_obs, "reward": G, "done": True, "action": a_obs }}
                            samples_this_game.append(obs_preprocessor(sample))
                
                if samples_this_game:
                    aggregated_samples.extend(samples_this_game)

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


def learn(config: TrainerConfig, learner_estimator: Estimator, actor_model: nn.Module, replay_buffer: Any, 
        frames_counter: SynchronizedType, learner_lock: LockType, buffer_lock: LockType, log_queue: QueueType, 
        latest_loss: SynchronizedType, latest_mean_q: SynchronizedType, latest_lr: SynchronizedType):
    """ 
    Main loop for a learner thread. 
    """
    
    device = learner_estimator.device
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
        
        is_weights = torch.from_numpy(batch.get("_weight").cpu().numpy().copy()).to(device).float()
        indices = torch.from_numpy(batch.get("index").cpu().numpy().copy())
        rewards = torch.from_numpy(batch.get(("next", "reward")).cpu().numpy().copy()).to(device).float()
        
        state_batch = batch.get("observation").to(device)
        action_batch = batch.get("action").to(device)
        
        targets = rewards.clone()
        
        mean_q = float(targets.mean().item())

        # Training step
        with learner_lock:
            learner_estimator.qnet.train()
            predicted_q = learner_estimator.qnet(state_batch, action_batch).clone()
            
            td_errors = predicted_q - targets
            squared_errors = td_errors * td_errors
            
            with torch.no_grad():
                new_priorities = td_errors.abs().cpu().numpy().copy()
            
            weighted_loss = (squared_errors * is_weights).mean()
            
            learner_estimator.optimizer.zero_grad()
            weighted_loss.backward()
            torch.nn.utils.clip_grad_norm_(learner_estimator.qnet.parameters(), config.gradient_clip_norm)
            learner_estimator.optimizer.step()
            learner_estimator.scheduler.step()
            
            # Sync actor model
            with torch.no_grad():
                for p_learner, p_actor in zip(learner_estimator.qnet.parameters(), actor_model.parameters()):
                    p_actor.data.copy_(p_learner.data)
            
            frames_counter.value += config.batch_size

            if frames_counter.value - last_log_frame >= config.log_every_frames:
                latest_loss.value = weighted_loss.item()
                latest_mean_q.value = mean_q
                latest_lr.value = learner_estimator.scheduler.get_last_lr()[0]
                
                log_queue.put({ 
                    'type': 'train_stats', 'frames': frames_counter.value, 'loss': latest_loss.value,
                    'mean_q': mean_q, 'learning_rate': latest_lr.value
                })
                last_log_frame = frames_counter.value
        
        with buffer_lock:
            replay_buffer.update_priority(indices, torch.from_numpy(new_priorities))


class DMCTrainer:
    """
    Trainer for the DMC agent.
    """
    
    def __init__(self, config: TrainerConfig):
        """
        Initializes DMCTrainer.
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
        self.learner_threads = []
        self.logger = None
        self.ingest_thread = None
        self.eval_thread = None

    def _setup_components(self):
        """
        Sets up multiprocessing components.
        """
        
        cfg = self.config
        self.ctx = mp.get_context('spawn')
    
        log.info(f"Using learner device: {cfg.device}")

        # T_0 conversion
        t0_in_steps = cfg.cosine_T0 // cfg.batch_size
        log.info(f"Scheduler T_0 (frames): {cfg.cosine_T0}, Batch Size: {cfg.batch_size} -> T_0 (steps): {t0_in_steps}")

        self.learner_estimator = Estimator(
            cfg.model_config, 
            cfg.learning_rate, 
            cfg.lr_gamma, 
            device=cfg.device, 
            weight_decay=cfg.weight_decay,
            cosine_T0=t0_in_steps,
            cosine_T_mult=cfg.cosine_T_mult,
            cosine_eta_min=cfg.cosine_eta_min
        )

        self.actor_model = BauernskatNet(cfg.model_config).to('cpu')
        self.actor_model.share_memory()
        self.actor_model.eval()
    
        self.sample_queue = self.ctx.Queue(maxsize=cfg.num_actors * cfg.actor_queue_size_multiplier)
        
        sampler = PrioritizedSampler(max_capacity=cfg.replay_buffer_size, alpha=cfg.per_alpha, beta=cfg.per_beta)
        self.replay_buffer = TensorDictReplayBuffer(
            storage=LazyTensorStorage(max_size=cfg.replay_buffer_size),
            sampler=sampler, batch_size=cfg.batch_size)
        
        log.info("Seeding the replay buffer...")
        try:
            obs_preprocessor = ObsPreprocessor()
            temp_env = rlcard.make(cfg.env, config={'seed': cfg.seed + 999})
            temp_agent = AgentDMC_Actor(self.actor_model, 'cpu')
            
            state, _ = temp_env.reset()
            _, action_obs = temp_agent.step(state, temp_env)
            
            seed_sample = {"observation": state['obs'], "action": action_obs, "next": {
                        "observation": state['obs'], "reward": 0.0, "done": False, "action": action_obs}}
            self.replay_buffer.add(TensorDict(obs_preprocessor(seed_sample), batch_size=[]))
            self.replay_buffer.empty()
            
            log.info("Replay buffer seeded successfully.")
        except Exception as e:
            log.error(f"Failed to seed replay buffer: {e}")
            raise
    
        # Shared variables
        self.log_queue = self.ctx.Queue()
        self.frames = self.ctx.Value('Q', 0)
        self.learner_lock = self.ctx.Lock()
        self.buffer_lock = self.ctx.Lock()
        self.latest_loss = self.ctx.Value('f', 0.0)
        self.latest_mean_q = self.ctx.Value('f', 0.0)
        self.latest_lr = self.ctx.Value('f', cfg.learning_rate)
        self.avg_p0_payoff = self.ctx.Value('f', 0.0)
        self.current_epsilon = self.ctx.Value('f', cfg.epsilon_start)
        self.dropped_batches_total = self.ctx.Value('Q', 0)
        self.total_elapsed_time = self.ctx.Value('d', 0.0)

        # Trump
        initial_trump_prob = cfg.trump_start if cfg.use_rule_based_trump_decay else 0.0
        self.current_trump_prob = self.ctx.Value('f', initial_trump_prob)
        
        # Teacher forcing
        self.current_teacher_eps = self.ctx.Value('f', cfg.teacher_start if cfg.use_teacher_forcing else 0.0)
        
        # Load model
        if cfg.load_model and os.path.exists(self.checkpointpath):
            checkpoint = torch.load(self.checkpointpath, map_location=cfg.device, weights_only=False)
            
            self.learner_estimator.qnet.load_state_dict(checkpoint['model_state_dict'])
            
            self.learner_estimator.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            if 'scheduler_state_dict' in checkpoint:
                self.learner_estimator.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
            
            self.frames.value = checkpoint.get('frames', 0)
            self.current_epsilon.value = checkpoint.get('epsilon', cfg.epsilon_start)
            self.total_elapsed_time.value = checkpoint.get('total_elapsed_time', 0.0)
            
            log.info(f"Resuming job from {self.frames.value} frames with epsilon {self.current_epsilon.value:.4f} after {format_time(self.total_elapsed_time.value)} of training.")
            
        # Initial sync of actor model
        with torch.no_grad():
            for p_learner, p_actor in zip(self.learner_estimator.qnet.parameters(), self.actor_model.parameters()):
                p_actor.data.copy_(p_learner.data)

    def _sample_ingest_worker(self):
        """
        Ingests samples from the sample queue into the replay buffer.
        """
        
        log.info("Sample ingest worker started.")
        
        while not self.shutdown_event.is_set():
            try:
                sample_batch = self.sample_queue.get(timeout=1.0)
                if sample_batch is None: break
                
                with self.buffer_lock:
                    for sample in sample_batch:
                        self.replay_buffer.add(TensorDict(sample, batch_size=[]))

            except queue.Empty:
                continue
            except (KeyboardInterrupt, EOFError):
                break
        
        log.info("Sample ingest worker terminated.")

    def start(self):
        """
        Starts the training process.
        """
        
        cfg = self.config
        self._setup_components()
        
        self.logger = TrainingLogger(self)
        self.logger.start()

        self.ingest_thread = threading.Thread(target=self._sample_ingest_worker, daemon=True)
        self.ingest_thread.start()

        self.actor_processes = [self.ctx.Process(target=act, args=(i, cfg, self.actor_model, self.sample_queue, 
                            self.log_queue, self.current_epsilon, self.current_trump_prob, self.current_teacher_eps, 
                            self.dropped_batches_total)) 
                                for i in range(cfg.num_actors)]
        for p in self.actor_processes: p.start()

        self.learner_threads = [threading.Thread(target=learn, args=(cfg, self.learner_estimator, self.actor_model, 
                            self.replay_buffer, self.frames, self.learner_lock, self.buffer_lock, self.log_queue, 
                            self.latest_loss, self.latest_mean_q, self.latest_lr)) for _ in range(cfg.num_threads)]
        for t in self.learner_threads: t.start()
        
        try:
            last_checkpoint_frame, last_eval_frame = 0, 0
            
            resumed_time = self.total_elapsed_time.value
            start_time = time.time()
            
            while self.frames.value < cfg.total_frames:
                time.sleep(1)
                current_frames = self.frames.value
                
                # Epsilon Decay
                if cfg.epsilon_decay_type == 'exponential':
                    eps = max(cfg.epsilon_end, cfg.epsilon_start * (cfg.epsilon_gamma ** current_frames))
                else:
                    ratio = min(1.0, current_frames / cfg.epsilon_decay_frames)
                    eps = cfg.epsilon_start - (cfg.epsilon_start - cfg.epsilon_end) * ratio
                self.current_epsilon.value = eps

                # Trump Decay
                if cfg.use_rule_based_trump_decay:
                    trump_ratio = min(1.0, current_frames / cfg.trump_decay_frames)
                    self.current_trump_prob.value = cfg.trump_start - (cfg.trump_start - cfg.trump_end) * trump_ratio
                else:
                    self.current_trump_prob.value = 0.0

                # Teacher Forcing Decay
                if cfg.use_teacher_forcing:
                    t_ratio = min(1.0, current_frames / cfg.teacher_decay_frames)
                    t_eps = cfg.teacher_start - (cfg.teacher_start - cfg.teacher_end) * t_ratio
                    self.current_teacher_eps.value = t_eps

                with self.buffer_lock: mem_size = len(self.replay_buffer)
                
                current_session_duration = time.time() - start_time
                self.total_elapsed_time.value = resumed_time + current_session_duration

                status_text = (f"\rTime: {format_time(self.total_elapsed_time.value)} | "
                            f"Step: {current_frames/1e6:.2f}M/{cfg.total_frames/1e6:.1f}M | "
                            f"Mem: {mem_size/1e3:.1f}k | Teacher-ε: {self.current_teacher_eps.value:.4f} | "
                            f"Trump-ε: {self.current_trump_prob.value:.4f} | Random-ε: {eps:.4f} | "
                            f"LR: {self.latest_lr.value:.3e} | "
                            f"ØQ: {self.latest_mean_q.value:+.4f} | Loss: {self.latest_loss.value:.4f} | "
                            f"ØPayoff: {self.avg_p0_payoff.value:+.2f}")
                
                print(status_text, end="", flush=True)

                if current_frames - last_checkpoint_frame >= cfg.save_every_frames:
                    self.checkpoint()
                    last_checkpoint_frame = current_frames
                
                # Evaluation
                if current_frames - last_eval_frame >= cfg.eval_every:
                    if self.eval_thread is not None and self.eval_thread.is_alive():
                        pass
                    else:
                        with self.learner_lock:
                            eval_net_copy = copy.deepcopy(self.learner_estimator.qnet).to(cfg.device)
                        
                        def run_eval_thread():
                            """
                            Runs the evaluation in a separate thread.
                            """
                            
                            try:
                                self.evaluator.evaluate(eval_net_copy, current_frames, self.writer)
                            except Exception as e:
                                log.error(f"Error in evaluation thread: {e}\n{traceback.format_exc()}")

                        self.eval_thread = threading.Thread(target=run_eval_thread, daemon=True)
                        self.eval_thread.start()
                        
                        last_eval_frame = current_frames
        
        except KeyboardInterrupt:
            print("\nTraining interrupted by user.")
        finally:
            print("\nTerminating processes and saving final model...")
            self.shutdown_event.set()
            
            for p in self.actor_processes:
                if p.is_alive(): p.terminate(); p.join(timeout=cfg.process_join_timeout)
            if self.ingest_thread.is_alive(): self.ingest_thread.join(timeout=cfg.process_join_timeout)
            
            if self.eval_thread is not None and self.eval_thread.is_alive():
                print("Waiting for final evaluation to complete...")
                self.eval_thread.join(timeout=120)

            if self.logger: self.logger.stop()

            self.checkpoint()
            self.plogger.close()
            if self.writer: self.writer.close()
            log.info("Trainer shutdown complete.")
    
    def checkpoint(self):
        """
        Saves the current model checkpoint.
        """
        
        cfg = self.config
        log.info(f"Saving full training checkpoint to {self.checkpointpath}")
        
        checkpoint = {
            'model_state_dict': self.learner_estimator.qnet.state_dict(),
            'optimizer_state_dict': self.learner_estimator.optimizer.state_dict(),
            'scheduler_state_dict': self.learner_estimator.scheduler.state_dict(),
            'frames': self.frames.value,
            'epsilon': self.current_epsilon.value,
            'total_elapsed_time': self.total_elapsed_time.value,
            'config': cfg
        }
        
        torch.save(checkpoint, self.checkpointpath)
        
        checkpoint_dir = os.path.dirname(self.checkpointpath)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(checkpoint_dir, f"model_{timestamp}_frame{self.frames.value}.tar")
        torch.save(checkpoint, backup_path)
        
        log.info(f"Backup saved to {backup_path}")
        
        inference_path = os.path.join(checkpoint_dir, f"inference_model_{self.frames.value}.pt")
        torch.save(self.learner_estimator.qnet.state_dict(), inference_path)
        
        log.info(f"Inference checkpoint saved to {inference_path}")

def main():
    """
    Main function to run the DMC trainer.
    """
    
    try:
        mp.set_start_method('spawn', force=True)
    except RuntimeError:
        pass

    setup_logging()
    parser = argparse.ArgumentParser("Agent DMC Trainer for RLCard")
    
    for field in dataclasses.fields(TrainerConfig):
        if not field.init or field.name == "model_config": continue
        
        if field.type == bool:
            if field.default:
                parser.add_argument(f'--no-{field.name}', dest=field.name, action='store_false', help=f"Disable {field.name}")
            else:
                parser.add_argument(f'--{field.name}', dest=field.name, action='store_true', help=f"Enable {field.name}")
            parser.set_defaults(**{field.name: field.default})
        else:
            kwargs = {'type': field.type, 'default': field.default, 'help': f"Set {field.name} (default: {field.default})"}
            if get_origin(field.type) is Literal:
                kwargs['choices'] = get_args(field.type)
                kwargs['type'] = type(kwargs['choices'][0])
            parser.add_argument(f'--{field.name}', **kwargs)
    
    args = parser.parse_args()
    config = TrainerConfig(**vars(args))
    os.environ["CUDA_VISIBLE_DEVICES"] = config.cuda
    
    trainer = DMCTrainer(config)
    log.info(f"Starting training for {config.xpid} with config:\n{pprint.pformat(dataclasses.asdict(config))}")
    trainer.start()

if __name__ == '__main__':
    main()