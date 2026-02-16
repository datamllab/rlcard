'''
    File name: rlcard/games/bauernskat/sac_agent/config.py
    Author: Oliver Czerwinski
    Date created: 11/10/2025
    Date last modified: 12/26/2025
    Python Version: 3.9+
'''

from dataclasses import dataclass, field
from typing import Tuple, Literal
import torch

# Bauernskat specific constants
MAX_PLAYER_CARDS = 16
MAX_TRICK_SIZE = 2
MAX_CEMETERY_SIZE = 32

# Model architecture
@dataclass
class BauernskatNetConfig:
    """
    Configuration for the BauernskatNet model.
    """
    
    card_embedding_dim: int = 32
    branch_output_dim: int = 96
    
    pool_type: Literal['mean', 'sum'] = 'mean'

    mlp_hidden_dims: Tuple[int, ...] = (64, 64)
    indicator_mlp_dims: Tuple[int, ...] = (64, 64)
    layout_processor_hidden_dim: int = 128
    mask_processor_hidden_dims: Tuple[int, ...] = (64,)

    num_lstm_layers: int = 2
    lstm_hidden_dim: int = 96
    use_bidirectional: bool = True
    use_attention: bool = True
    attn_heads: int = 4
    lstm_fc_dims: Tuple[int, ...] = (96,)

    context_vector_dim: int = 11
    indicator_vector_dim: int = 8
    action_history_frame_size: int = 49

    head_hidden_dims: Tuple[int, ...] = (512, 256)
    head_dropout: float = 0.0

# Training configuration
@dataclass
class TrainerConfig:
    """
    Configuration for the DMCTrainer.
    """
    
    xpid: str = 'sac_agent_bauernskat_v1'
    savedir: str = 'experiments/sac_agent_result'
    load_model: bool = True
    save_every_frames: int = 4_096_000
    seed: int = 21000

    # Logging
    log_to_tensorboard: bool = True
    log_p0_p1_payoffs: bool = True
    log_every_frames: int = 4_096
    log_interval_seconds: float = 5.0

    # Pipeline & Threading
    cuda: str = '0'
    training_device: str = "0"
    num_actors: int = 10
    num_threads: int = 1
    actor_queue_size_multiplier: int = 64
    actor_game_batch_size: int = 1
    process_join_timeout: float = 5.0
    sample_queue_put_timeout: float = 5.0

    # Training Hyperparameters
    batch_size: int = 1024
    gamma: float = 0.99
    tau: float = 0.005
    n_step_returns: int = 3
    actor_lr: float = 3e-4
    critic_lr: float = 1.5e-4
    alpha_lr: float = 3e-4
    gradient_clip_norm: float = 1.0
    weight_decay: float = 1e-3

    use_lr_scheduler: bool = True
    cosine_T0: int = 5_120_000
    cosine_T_mult: int = 2
    cosine_eta_min: float = 3e-6
    
    # Entropy parameters
    initial_alpha: float = 1.0
    learn_alpha: bool = True
    target_entropy_ratio: float = 0.98

    # Replay Buffer
    replay_buffer_size: int = 204_800
    min_buffer_size_to_learn: int = 8_192
    
    # Prioritized Experience Replay
    per_alpha: float = 0.6
    per_beta: float = 0.4
    
    # Reward Function
    reward_type: Literal['game_score', 'binary', 'hybrid'] = 'hybrid'

    # Parameters for 'hybrid' reward function
    max_reward_abs: float = 480.0
    reward_shaping_steepness: float = 0.009
    reward_shaping_threshold: int = 18
    reward_shaping_score_weight: float = 0.5
    reward_shaping_win_bonus: float = 1.0

    # Rule-Based Trump Selection
    use_rule_based_trump_decay: bool = False
    trump_start: float = 1.0
    trump_end: float = 0.0
    trump_decay_frames: int = 1_024_000_000

    # Teacher Forcing
    use_teacher_forcing: bool = False
    teacher_start: float = 1.0
    teacher_end: float = 0.0
    teacher_decay_frames: int = 64_000_000
    
    # Environment and Evaluation
    env: str = 'bauernskat'
    information_level: Literal['normal', 'show_self', 'perfect'] = 'normal'
    total_frames: int = 1_024_000_000
    eval_every: int = 4_096_000
    num_eval_games: int = 512

    # Model Configuration
    model_config: BauernskatNetConfig = field(default_factory=BauernskatNetConfig)
    device: torch.device = field(init=False)
    
    def __post_init__(self):
        """
        Sets the device and validate some hyperparameters.
        """
        
        if self.training_device != "cpu" and torch.cuda.is_available():
            self.device = torch.device(f"cuda:{self.training_device}")
        else:
            self.device = torch.device("cpu")

        if self.min_buffer_size_to_learn > self.replay_buffer_size:
            raise ValueError("min_buffer_size_to_learn cannot be larger than replay_buffer_size")
        if self.batch_size > self.min_buffer_size_to_learn:
            raise ValueError("batch_size cannot be larger than min_buffer_size_to_learn")
        if self.num_actors <= 0:
            raise ValueError("num_actors must be a positive integer")