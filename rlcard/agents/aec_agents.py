import numpy as np

from rlcard.agents.nfsp_agent import NFSPAgent
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.dmc_agent.model import DMCAgent
from rlcard.agents.random_agent import RandomAgent


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


class AECNFSPAgent(NFSPAgent):
    def step(self, state):
        return super().step(wrap_state(state))

    def eval_step(self, state):
        return super().eval_step(wrap_state(state))

    def feed(self, ts):
        state, action, reward, next_state, done = tuple(ts)
        state = wrap_state(state)
        next_state = wrap_state(next_state)
        ts = (state, action, reward, next_state, done)
        return super().feed(ts)


class AECDQNAgent(DQNAgent):
    def step(self, state):
        return super().step(wrap_state(state))

    def eval_step(self, state):
        return super().eval_step(wrap_state(state))

    def feed(self, ts):
        state, action, reward, next_state, done = tuple(ts)
        state = wrap_state(state)
        next_state = wrap_state(next_state)
        ts = (state, action, reward, next_state, done)
        return super().feed(ts)


class AECRandomAgent(RandomAgent):
    def step(self, state):
        return super().step(wrap_state(state))

    def eval_step(self, state):
        return super().eval_step(wrap_state(state))


class AECDMCAgent(DMCAgent):
    def step(self, state):
        return super().step(wrap_state(state))

    def eval_step(self, state):
        return super().eval_step(wrap_state(state))

    def feed(self, ts):
        state, action, reward, next_state, done = tuple(ts)
        state = wrap_state(state)
        next_state = wrap_state(next_state)
        ts = (state, action, reward, next_state, done)
        return super().feed(ts)
