import rlcard
from rlcard.agents.random_agent import RandomAgent

env = rlcard.make('uno')

env.set_mode(single_agent_mode=True)

state = env.reset()

agent = RandomAgent(env.action_num)

counter = 0
total = .0

while True:
    action = agent.step(state)
    state, reward, done = env.step(action)
    if done:
        counter += 1
        total += reward
    if counter == 1:
        break

print(total / counter)
