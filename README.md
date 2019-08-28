# RLCard
RLCard is an opensource toolkit for devopling Reinforcement Learning (RL) algorithms on Poker games.

### Installation
Make sure that you have **Python 3.6+** and **pip** installed. You can install `rlcard` with `pip` as follow:
```
pip install -e .
```

### Example
Run an example of Doudizhu environment by:
```
python examples/doudizhu.py
```
Below is an example of genrating self-play data of game **Doudizhu** with **random agents**:
**STEP 1:** import `rlcard` and a random agent
```python
import rlcard
from rlcard.agents.random_agent import RandomAgent
```

**STEP 2:** Initialize the environment
```python
env = rlcard.make('doudizhu')
```
**STEP 3:** Initialize and set the 3 random agents for Doudizhu.
```python
agent_0 = RandomAgent()
agent_1 = RandomAgent()
agent_2 = RandomAgent()
env.set_agents([agent_0, agent_1, agent_2])
```
**STEP 4:** Seed everything for reproductibility.
```python
env.set_seed(0)
agent_0.set_seed(0)
agent_1.set_seed(0)
agent_2.set_seed(0)
```
**STEP 5:** Play one game of Doudizhu and generate the data
```python
trajectories, player_wins = env.run()
```
