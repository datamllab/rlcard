from collections import defaultdict
import numpy as np


def wrap_state(state):
    # check if obs is already wrapped
    if "obs" in state and "legal_actions" in state and "raw_legal_actions" in state:
        return state

    wrapped_state = {}
    wrapped_state["obs"] = state["observation"]
    legal_actions = np.flatnonzero(state["action_mask"])
    # the values of legal_actions isn't available so setting them to None
    wrapped_state["legal_actions"] = {l: None for l in legal_actions}
    # raw_legal_actions isn't available so setting it to legal actions
    wrapped_state["raw_legal_actions"] = list(wrapped_state["legal_actions"].keys())
    return wrapped_state


def run_game_pettingzoo(env, agents, is_training=False):
    env.reset()
    trajectories = defaultdict(list)
    for agent_name in env.agent_iter():
        obs, reward, done, _ = env.last()
        trajectories[agent_name].append((obs, reward, done))

        if done:
            action = None
        else:
            if is_training:
                action = agents[agent_name].step(obs)
            else:
                action, _ = agents[agent_name].eval_step(obs)
        trajectories[agent_name].append(action)

        env.step(action)
    return trajectories


def reorganize_pettingzoo(trajectories):
    ''' Reorganize the trajectory to make it RL friendly

    Args:
        trajectory (list): A list of trajectories

    Returns:
        (list): A new trajectories that can be fed into RL algorithms.

    '''
    new_trajectories = defaultdict(list)
    for agent_name, trajectory in trajectories.items():
        for i in range(0, len(trajectory)-2, 2):
            transition = [
                trajectory[i][0], # obs,
                trajectory[i+1], # action
                trajectory[i+2][1], # reward
                trajectory[i+2][0], # next_obs
                trajectory[i+2][2], # done
            ]
            new_trajectories[agent_name].append(transition)
    return new_trajectories


def tournament_pettingzoo(env, agents, num_episodes):
    total_rewards = defaultdict(float)
    for _ in range(num_episodes):
        trajectories = run_game_pettingzoo(env, agents)
        trajectories = reorganize_pettingzoo(trajectories)
        for agent_name, trajectory in trajectories.items():
            reward = sum([t[2] for t in trajectory])
            total_rewards[agent_name] += reward
    return {k: v / num_episodes for (k, v) in total_rewards.items()}
