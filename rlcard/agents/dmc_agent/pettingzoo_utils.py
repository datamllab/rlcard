import traceback

import numpy as np
import torch

from .utils import log
from rlcard.utils import run_game_pettingzoo

def create_buffers_pettingzoo(
    T,
    num_buffers,
    env,
    device_iterator,
):
    buffers = {}
    for device in device_iterator:
        buffers[device] = []
        for agent_name in env.agents:
            state_shape = env.observation_space(agent_name)["observation"].shape
            specs = dict(
                done=dict(size=(T,), dtype=torch.bool),
                episode_return=dict(size=(T,), dtype=torch.float32),
                target=dict(size=(T,), dtype=torch.float32),
                state=dict(size=(T,)+tuple(state_shape), dtype=torch.int8),
                action=dict(size=(T,)+(env.action_space(agent_name).n,), dtype=torch.int8),
            )
            _buffers = {key: [] for key in specs}
            for _ in range(num_buffers):
                for key in _buffers:
                    if device == "cpu":
                        _buffer = torch.empty(**specs[key]).to('cpu').share_memory_()
                    else:
                        _buffer = torch.empty(**specs[key]).to('cuda:'+str(device)).share_memory_()
                    _buffers[key].append(_buffer)
            buffers[device].append(_buffers)
    return buffers

def _get_action_feature(action, action_space):
    out = np.zeros(action_space)
    out[action] = 1
    return out

def act_pettingzoo(
    i,
    device,
    T,
    free_queue,
    full_queue,
    model,
    buffers,
    env
):
    log.info('Device %s Actor %i started.', str(device), i)
    try:
        done_buf = [[] for _ in range(env.num_agents)]
        episode_return_buf = [[] for _ in range(env.num_agents)]
        target_buf = [[] for _ in range(env.num_agents)]
        state_buf = [[] for _ in range(env.num_agents)]
        action_buf = [[] for _ in range(env.num_agents)]
        size = [0 for _ in range(env.num_agents)]

        while True:
            trajectories = run_game_pettingzoo(env, model.agents, is_training=True)
            for agent_id, agent_name in enumerate(env.possible_agents):
                traj_size = len(trajectories[agent_name]) // 2
                if traj_size > 0:
                    size[agent_id] += traj_size
                    target_return = trajectories[agent_name][-2][1]
                    target_buf[agent_id].extend([target_return for _ in range(traj_size)])
                    for i in range(0, len(trajectories[agent_name]), 2):
                        state = trajectories[agent_name][i][0]['observation']
                        action = _get_action_feature(
                            trajectories[agent_name][i+1], model.agents[agent_name].action_shape
                        )
                        episode_return = trajectories[agent_name][i][1]
                        done = trajectories[agent_name][i][2]
                        state_buf[agent_id].append(torch.from_numpy(state))
                        action_buf[agent_id].append(torch.from_numpy(action))
                        episode_return_buf[agent_id].append(episode_return)
                        done_buf[agent_id].append(done)

                while size[agent_id] > T:
                    index = free_queue[agent_id].get()
                    if index is None:
                        print("index is None")
                        break
                    for t in range(T):
                        temp_done = done_buf[agent_id][t]
                        buffers[agent_id]['done'][index][t, ...] = temp_done
                        buffers[agent_id]['episode_return'][index][t, ...] = episode_return_buf[agent_id][t]
                        buffers[agent_id]['target'][index][t, ...] = target_buf[agent_id][t]
                        buffers[agent_id]['state'][index][t, ...] = state_buf[agent_id][t]
                        buffers[agent_id]['action'][index][t, ...] = action_buf[agent_id][t]
                    full_queue[agent_id].put(index)
                    done_buf[agent_id] = done_buf[agent_id][T:]
                    episode_return_buf[agent_id] = episode_return_buf[agent_id][T:]
                    target_buf[agent_id] = target_buf[agent_id][T:]
                    state_buf[agent_id] = state_buf[agent_id][T:]
                    action_buf[agent_id] = action_buf[agent_id][T:]
                    size[agent_id] -= T

    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.error('Exception in worker process %i', i)
        traceback.print_exc()
        raise e
