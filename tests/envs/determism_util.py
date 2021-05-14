import rlcard
from rlcard.agents.random_agent import RandomAgent
import random
import numpy as np

def hash_obsevation(obs):
    try:
        val = hash(obs.tobytes())
        return val
    except AttributeError:
        try:
            return hash(obs)
        except TypeError:
            warnings.warn("Observation not an int or an Numpy array")
            return 0

def rand_iter(n):
    for x in range(n+1):
        random.randint(0, 1000)
        np.random.normal(size=100)

def gather_observations(env, actions, num_rand_steps):
    rand_iter(num_rand_steps)
    state, player_id = env.reset()
    rand_iter(num_rand_steps)

    action_idx = 0
    observations = []
    while not env.is_over() and action_idx < len(actions):
        # Agent plays
        rand_iter(num_rand_steps)
        legals = list(state['legal_actions'].keys())
        action = legals[actions[action_idx]%len(legals)]
        # Environment steps
        next_state, next_player_id = env.step(action)
        # Set the state and player
        state = next_state
        player_id = next_player_id

        action_idx += 1
        # Save state.
        if not env.game.is_over():
            observations.append(state)

    return observations

def is_deterministic(env_name):
    env = rlcard.make(env_name)

    NUM_STEPS = 25

    actions = [random.randrange(env.game.get_num_actions()) for _ in range(NUM_STEPS)]
    base_seed = 12941
    hashes = []
    for rand_iters in range(2):
        env = rlcard.make(env_name,config={'seed':base_seed})

        hashes.append(hash(tuple([hash_obsevation(obs['obs']) for obs in gather_observations(env,actions,rand_iters)])))

    return hashes[0] == hashes[1]
