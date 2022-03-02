from rlcard.agents.nfsp_agent import NFSPAgent
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.pettingzoo_utils import wrap_state


class NFSPAgentPettingZoo(NFSPAgent):
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


class DQNAgentPettingZoo(DQNAgent):
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


class RandomAgentPettingZoo(RandomAgent):
    def step(self, state):
        return super().step(wrap_state(state))

    def eval_step(self, state):
        return super().eval_step(wrap_state(state))
