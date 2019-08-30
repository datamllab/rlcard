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

## Available Environments
Detailed documents of the APIs for each game can be found by clicking the game. The complexity is extimated based on the following aspects: 
* **InfoSet Number:** the number of information set
* **Avg. InfoSet Size:** the average number of states in a single information set
* **Action Size:** the size of the action space (without abstraction)

**Note:** For some of the large card games, obtaining the some of the above statistics is computationally challenging, and thus they are 'unknown' to us. 

| Game                     | InfoSet Number  |Avg. InfoSet Size | Action Size |Status  |
| ------------------------ |:--------------:| :-------:|:------:| :-------:|
| Blackjack ([wiki](https://en.wikipedia.org/wiki/Blackjack)) | 10^3      |  10^1 | 10^0| Available |
| Two-player limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em))      |10^14 | 10^3| 10^0 |Available |
| Two-player UNO ([wiki](https://en.wikipedia.org/wiki/Uno_(card_game)))      |  unknown      |   unknown | 10^1| Come soon|
| Mahjong ([wiki](https://en.wikipedia.org/wiki/Competition_Mahjong_scoring_rules))      | 10^121      |   10^48 |10^2 | Come soon| 
| Dou Dizhu ([wiki](https://en.wikipedia.org/wiki/Dou_dizhu))      | unknown      |   unknown | 10^4| Available|
| Sheng Ji ([wiki](https://en.wikipedia.org/wiki/Sheng_ji))      | unknown      |   unknown | unknown | Come soon|

Suggetions/contributions of more card games are welcomed.
