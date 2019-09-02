# RLCard: A Toolkit for Reinforcement Learning in Card Games
RLCard is an opensource toolkit for devopling Reinforcement Learning (RL) algorithms in card games. It supports multiple challenging card game environments with common and easy-to-use interfaces. The  goal  of  the  toolkit  is  to  enable  more  researchers  to  study  game  AI  and  push  forward  the  research of imperfect information games.

# Installation
Make sure that you have **Python 3.6+** and **pip** installed. You can install `rlcard` with `pip` as follow:
```
pip install -e .
```

# A Running Example
An example of running Dou Dizhu with three random agents is as follow:
```python
import rlcard
from rlcard.agents.random_agent import RandomAgent

# STEP 1: Initialize the environment
env = rlcard.make('doudizhu')

# STEP 2: Initialize the 3 random agents
env.set_agents([RandomAgent(), RandomAgent(), RandomAgent()])

# STEP 3: Run the game and collect data
while True:
    # Generate data from the environment
    trajectories, payoffs = env.run()
    
    # Update the agent here
```
More examples can be found in `examples/`

# Available Environments
We provide a complexity estimation for each game on the following aspects: 
* **InfoSet Number:** the number of information set
* **Avg. InfoSet Size:** the average number of states in a single information set
* **Action Size:** the size of the action space (without abstraction)

**Note:** For some of the large card games, obtaining some of the statistics is computationally challenging, and thus they are 'unknown' to us. 

| Game                     | InfoSet Number  |Avg. InfoSet Size | Action Size |Status  |
| ------------------------ |:--------------:| :-------:|:------:| :-------:|
| Blackjack ([wiki](https://en.wikipedia.org/wiki/Blackjack)) | 10^3      |  10^1 | 10^0| Available |
| Two-player limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em))      |10^14 | 10^3| 10^0 |Available |
| No-limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em))      |10^162 | 10^3| 10^4 |Available |
| Two-player UNO ([wiki](https://en.wikipedia.org/wiki/Uno_(card_game)))      |  unknown      |   unknown | 10^1| Come soon|
| Mahjong ([wiki](https://en.wikipedia.org/wiki/Competition_Mahjong_scoring_rules))      | 10^121      |   10^48 |10^2 | Come soon| 
| Dou Dizhu ([wiki](https://en.wikipedia.org/wiki/Dou_dizhu))      | unknown      |   unknown | 10^4| Available|
| Sheng Ji ([wiki](https://en.wikipedia.org/wiki/Sheng_ji))      | unknown      |   unknown | unknown | Come soon|


# Documents
Please refer to the [Documents Index](docs/index.md).

# DISCLAIMER
Please note that this is a **pre-release** version of the RLCard. The toolkit is provided **"as is"**, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement.

# Acknowledgements
We would like to thank JJ World Network Technology Co.,LTD for the technical support.

