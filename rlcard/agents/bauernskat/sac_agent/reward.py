'''
    File name: rlcard/games/bauernskat/sac_agent/reward.py
    Author: Oliver Czerwinski
    Date created: 11/10/2025
    Date last modified: 12/26/2025
    Python Version: 3.9+
'''

import numpy as np

def _custom_centered_tanh(final_score: float, steepness: float, win_loss_threshold: int) -> float:
    """
    Centered tanh function to compress score magnitudes.
    """
    
    if final_score >= win_loss_threshold:
        adjusted_magnitude = float(final_score - win_loss_threshold)
        return np.tanh(adjusted_magnitude * steepness)
    elif final_score <= -win_loss_threshold:
        adjusted_magnitude = float(abs(final_score) - win_loss_threshold)
        return -np.tanh(adjusted_magnitude * steepness)
    else:
        return 0.0

def calculate_game_score_reward(final_score: float) -> float:
    """
    Returns the raw game score as reward.
    """
    
    return float(final_score)

def calculate_binary_reward(final_score: float) -> float:
    """
    Returns +1.0 for win or -1.0 for loss as reward.
    """
    
    return float(np.sign(final_score))

def calculate_hybrid_reward(my_final_pips: int, opponent_final_pips: int, final_score: float, steepness: float = 0.009, threshold: int = 18, score_weight: float = 0.5, win_bonus_magnitude: float = 1.0) -> float:
    """
    Calculates a hybrid reward based on game outcome, pip difference and score magnitude.
    """
    
    # Sign of the outcome
    outcome_sign = 0.0
    if final_score >= threshold:
        outcome_sign = 1.0
    elif final_score <= -threshold:
        outcome_sign = -1.0

    # Safety for draw
    if outcome_sign == 0.0:
        return 0.0

    # Pip difference
    r_base = float(my_final_pips - opponent_final_pips)

    # Score multiplier
    compressed_score = _custom_centered_tanh(final_score, steepness=steepness, win_loss_threshold=threshold)
    m_score = 1.0 + score_weight * abs(compressed_score)
    
    total_magnitude = win_bonus_magnitude + abs(r_base * m_score)
    final_reward = outcome_sign * total_magnitude
    
    return final_reward