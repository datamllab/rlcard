# RLCard: A Toolkit for Reinforcement Learning in Card Games
<img width="500" src="./docs/imgs/logo.jpg" alt="Logo" />

[![Build Status](https://travis-ci.org/datamllab/RLCard.svg?branch=master)](https://travis-ci.org/datamllab/RLCard)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/248eb15c086748a4bcc830755f1bd798)](https://www.codacy.com/manual/daochenzha/rlcard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=datamllab/rlcard&amp;utm_campaign=Badge_Grade)
[![Coverage Status](https://coveralls.io/repos/github/datamllab/rlcard/badge.svg)](https://coveralls.io/github/datamllab/rlcard?branch=master)

RLCard is a toolkit for Reinforcement Learning (RL) in card games. It supports multiple card environments with easy-to-use interfaces. The goal of RLCard is to bridge reinforcement learning and imperfect information games. RLCard is developed by [DATA Lab](http://faculty.cs.tamu.edu/xiahu/) at Texas A&M University and community contributors.

*   Official Website: [http://www.rlcard.org](http://www.rlcard.org)
*   Tutorial in Jupyter Notebook: [https://github.com/datamllab/rlcard-tutorial](https://github.com/datamllab/rlcard-tutorial)
*   Paper: [https://arxiv.org/abs/1910.04376](https://arxiv.org/abs/1910.04376)
*   GUI: [RLCard-Showdown](https://github.com/datamllab/rlcard-showdown)
*   Resources: [Awesome-Game-AI](https://github.com/datamllab/awesome-game-ai)

**Community:**
*  **Slack**: Discuss in our [#rlcard-project](https://join.slack.com/t/rlcard/shared_invite/zt-l4qbarxs-mtBrjBRpYIMq4Re4jvYpWQ) slack channel.
*  **QQ Group**: Join our QQ group 665647450. Password: rlcardqqgroup

**News:**
*   Our package is used in [PettingZoo](https://github.com/PettingZoo-Team/PettingZoo). Please check it out!
*   We have released RLCard-Showdown, GUI demo for RLCard. Please check out [here](https://github.com/datamllab/rlcard-showdown)!
*   Jupyter Notebook tutorial available! We add some examples in R to call Python interfaces of RLCard with reticulate. See [here](docs/toy-examples-r.md)
*   Thanks for the contribution of [@Clarit7](https://github.com/Clarit7) for supporting different number of players in Blackjack. We call for contributions for gradually making the games more configurable. See [here](CONTRIBUTING.md#making-configurable-environments) for more details.
*   Thanks for the contribution of [@Clarit7](https://github.com/Clarit7) for the Blackjack and Limit Hold'em human interface.
*   Now RLCard supports environment local seeding and multiprocessing. Thanks for the testing scripts provided by [@weepingwillowben](https://github.com/weepingwillowben).
*   Human interface of NoLimit Holdem available. The action space of NoLimit Holdem has been abstracted. Thanks for the contribution of [@AdrianP-](https://github.com/AdrianP-).
*   New game Gin Rummy and human GUI available. Thanks for the contribution of [@billh0420](https://github.com/billh0420).
*   PyTorch implementation available. Thanks for the contribution of [@mjudell](https://github.com/mjudell).

## Cite this work
If you find this repo useful, you may cite:
```bibtex
@article{zha2019rlcard,
  title={RLCard: A Toolkit for Reinforcement Learning in Card Games},
  author={Zha, Daochen and Lai, Kwei-Herng and Cao, Yuanpu and Huang, Songyi and Wei, Ruzhe and Guo, Junyu and Hu, Xia},
  journal={arXiv preprint arXiv:1910.04376},
  year={2019}
}
```

## Installation
Make sure that you have **Python 3.5+** and **pip** installed. We recommend installing the latest version of `rlcard` with `pip`:

```
git clone https://github.com/datamllab/rlcard.git
cd rlcard
pip install -e .
```
Alternatively, you can install the latest stable version with:
```
pip install rlcard
```
The default installation will only include the card environments. To use Tensorflow implementation of the example algorithms, install the supported verison of Tensorflow with:
```
pip install rlcard[tensorflow]
```
To try PyTorch implementations, please run: 
```
pip install rlcard[torch]
```
If you meet any problems when installing PyTorch with the command above, you may follow the instructions on [PyTorch official website](https://pytorch.org/get-started/locally/) to manually install PyTorch.

We also provide [**conda** installation method](https://anaconda.org/toubun/rlcard):

```
conda install -c toubun rlcard
```

Conda installation only provides the card environments, you need to manually install Tensorflow or Pytorch on your demands.

## Examples
Please refer to [examples/](examples). A **short example** is as below.

```python
import rlcard
from rlcard.agents import RandomAgent

env = rlcard.make('blackjack')
env.set_agents([RandomAgent(action_num=env.action_num)])

trajectories, payoffs = env.run()
```

We also recommend the following **toy examples** in Python.

*   [Playing with random agents](docs/toy-examples.md#playing-with-random-agents)
*   [Deep-Q learning on Blackjack](docs/toy-examples.md#deep-q-learning-on-blackjack)
*   [Running multiple processes](docs/toy-examples.md#running-multiple-processes)
*   [Training CFR (chance sampling) on Leduc Hold'em](docs/toy-examples.md#training-cfr-on-leduc-holdem)
*   [Having fun with pretrained Leduc model](docs/toy-examples.md#having-fun-with-pretrained-leduc-model)
*   [Leduc Hold'em as single-agent environment](docs/toy-examples.md#leduc-holdem-as-single-agent-environment)

R examples can be found [here](docs/toy-examples-r.md).

## Demo
Run `examples/leduc_holdem_human.py` to play with the pre-trained Leduc Hold'em model. Leduc Hold'em is a simplified version of Texas Hold'em. Rules can be found [here](docs/games.md#leduc-holdem).

```
>> Leduc Hold'em pre-trained model

>> Start a new game!
>> Agent 1 chooses raise

=============== Community Card ===============
┌─────────┐
│░░░░░░░░░│
│░░░░░░░░░│
│░░░░░░░░░│
│░░░░░░░░░│
│░░░░░░░░░│
│░░░░░░░░░│
│░░░░░░░░░│
└─────────┘
===============   Your Hand    ===============
┌─────────┐
│J        │
│         │
│         │
│    ♥    │
│         │
│         │
│        J│
└─────────┘
===============     Chips      ===============
Yours:   +
Agent 1: +++
=========== Actions You Can Choose ===========
0: call, 1: raise, 2: fold

>> You choose action (integer):
```
We also provide a GUI for easy debugging. Please check [here](https://github.com/datamllab/rlcard-showdown/). Some demos:

![doudizhu-replay](https://github.com/datamllab/rlcard-showdown/blob/master/docs/imgs/doudizhu-replay.png?raw=true)
![leduc-replay](https://github.com/datamllab/rlcard-showdown/blob/master/docs/imgs/leduc-replay.png?raw=true)

## Available Environments
We provide a complexity estimation for the games on several aspects. **InfoSet Number:** the number of information sets; **InfoSet Size:** the average number of states in a single information set; **Action Size:** the size of the action space. **Name:** the name that should be passed to `rlcard.make` to create the game environment. We also provide the link to the documentation and the random example.

| Game                                                                                                                                                                                           | InfoSet Number  | InfoSet Size      | Action Size | Name            | Usage                                                                                       |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :-------------: | :---------------: | :---------: | :-------------: | :-----------------------------------------------------------------------------------------: |
| Blackjack ([wiki](https://en.wikipedia.org/wiki/Blackjack), [baike](https://baike.baidu.com/item/21%E7%82%B9/5481683?fr=aladdin))                                                              | 10^3            | 10^1              | 10^0        | blackjack       | [doc](docs/games.md#blackjack), [example](examples/blackjack_random.py)                     |
| Leduc Hold’em ([paper](http://poker.cs.ualberta.ca/publications/UAI05.pdf))                                                                                                                    | 10^2            | 10^2              | 10^0        | leduc-holdem    | [doc](docs/games.md#leduc-holdem), [example](examples/leduc_holdem_random.py)               |
| Limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em), [baike](https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin))    | 10^14           | 10^3              | 10^0        | limit-holdem    | [doc](docs/games.md#limit-texas-holdem), [example](examples/limit_holdem_random.py)         |
| Dou Dizhu ([wiki](https://en.wikipedia.org/wiki/Dou_dizhu), [baike](https://baike.baidu.com/item/%E6%96%97%E5%9C%B0%E4%B8%BB/177997?fr=aladdin))                                               | 10^53 ~ 10^83   | 10^23             | 10^4        | doudizhu        | [doc](docs/games.md#dou-dizhu), [example](examples/doudizhu_random.py)                      |
| Simple Dou Dizhu ([wiki](https://en.wikipedia.org/wiki/Dou_dizhu), [baike](https://baike.baidu.com/item/%E6%96%97%E5%9C%B0%E4%B8%BB/177997?fr=aladdin))                                        | -               | -                 | -           | simple-doudizhu | [doc](docs/games.md#simple-dou-dizhu), [example](examples/simple_doudizhu_random.py)        |
| Mahjong ([wiki](https://en.wikipedia.org/wiki/Competition_Mahjong_scoring_rules), [baike](https://baike.baidu.com/item/%E9%BA%BB%E5%B0%86/215))                                                | 10^121          | 10^48             | 10^2        | mahjong         | [doc](docs/games.md#mahjong), [example](examples/mahjong_random.py)                         | 
| No-limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em), [baike](https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin)) | 10^162          | 10^3              | 10^4        | no-limit-holdem | [doc](docs/games.md#no-limit-texas-holdem), [example](examples/nolimit_holdem_random.py)    |
| UNO ([wiki](https://en.wikipedia.org/wiki/Uno_\(card_game\)), [baike](https://baike.baidu.com/item/UNO%E7%89%8C/2249587))                                                                      |  10^163         | 10^10             | 10^1        | uno             | [doc](docs/games.md#uno), [example](examples/uno_random.py)                                 |
| Gin Rummy ([wiki](https://en.wikipedia.org/wiki/Gin_rummy), [baike](https://baike.baidu.com/item/%E9%87%91%E6%8B%89%E7%B1%B3/3471710))                                                         | 10^52           | -                 | -           | gin-rummy       | [doc](docs/games.md#gin-rummy), [example](examples/gin_rummy_random.py)                     |

## API Cheat Sheet
### How to create an environment
You can use the the following interface to make an environment. You may optionally specify some configurations with a dictionary.
*   **env = rlcard.make(env_id, config={})**: Make an environment. `env_id` is a string of a environment; `config` is a dictionary that specifies some environment configurations, which are as follows.
	*   `seed`: Default `None`. Set a environment local random seed for reproducing the results.
	*   `env_num`: Default `1`. It specifies how many environments running in parallel. If the number is larger than 1, then the tasks will be assigned to multiple processes for acceleration.
	*   `allow_step_back`: Defualt `False`. `True` if allowing `step_back` function to traverse backward in the tree.
	*   `allow_raw_data`: Default `False`. `True` if allowing raw data in the `state`.
	*   `single_agent_mode`: Default `False`. `True` if using single agent mode, i.e., Gym style interface with other players as pretrained/rule models.
	*   `active_player`: Defualt `0`. If `single_agent_mode` is `True`, `active_player` will specify operating on which player in single agent mode.
	*   `record_action`: Default `False`. If `True`, a field of `action_record` will be in the `state` to record the historical actions. This may be used for human-agent play.
	*   Game specific configurations: These fields start with `game_`. Currently, we only support `game_player_num` in Blackjack.

Once the environemnt is made, we can access some information of the game.
*   **env.action_num**: The number of actions.
*   **env.player_num**: The number of players.
*   **env.state_space**: Ther state space of the observations.
*   **env.timestep**: The number of timesteps stepped by the environment.

### What is state in RLCard
State is a Python dictionary. It will always have observation `state['obs']` and legal actions `state['legal_actions']`. If `allow_raw_data` is `True`, state will also have raw observation `state['raw_obs']` and raw legal actions `state['raw_legal_actions']`.

### Basic interfaces
The following interfaces provide a basic usage. It is easy to use but it has assumtions on the agent. The agent must follow [agent template](docs/developping-algorithms.md). 
*   **env.set_agents(agents)**: `agents` is a list of `Agent` object. The length of the list should be equal to the number of the players in the game.
*   **env.run(is_training=False)**: Run a complete game and return trajectories and payoffs. The function can be used after the `set_agents` is called. If `is_training` is `True`, it will use `step` function in the agent to play the game. If `is_training` is `False`, `eval_step` will be called instead.

### Advanced interfaces
For advanced usage, the following interfaces allow flexible operations on the game tree. These interfaces do not make any assumtions on the agent.
*   **env.reset()**: Initialize a game. Return the state and the first player ID.
*   **env.step(action, raw_action=False)**: Take one step in the environment. `action` can be raw action or integer; `raw_action` should be `True` if the action is raw action (string).
*   **env.step_back()**: Available only when `allow_step_back` is `True`. Take one step backward. This can be used for algorithms that operate on the game tree, such as CFR (chance sampling).
*   **env.is_over()**: Return `True` if the current game is over. Otherewise, return `False`.
*   **env.get_player_id()**: Return the Player ID of the current player.
*   **env.get_state(player_id)**: Return the state that corresponds to `player_id`.
*   **env.get_payoffs()**: In the end of the game, return a list of payoffs for all the players.
*   **env.get_perfect_information()**: (Currently only support some of the games) Obtain the perfect information at the current state.

### Running with multiple processes
RLCard now supports acceleration with multiple processes. Simply change `env_num` when making the environment to indicate how many processes would be used. Currenly we only support `run()` function with multiple processes. An example is [DQN on blackjack](docs/toy-examples.md#running-multiple-processes)  

## Library Structure
The purposes of the main modules are listed as below:

*   [/examples](examples): Examples of using RLCard.
*   [/docs](docs): Documentation of RLCard.
*   [/tests](tests): Testing scripts for RLCard.
*   [/rlcard/agents](rlcard/agents): Reinforcement learning algorithms and human agents.
*   [/rlcard/envs](rlcard/envs): Environment wrappers (state representation, action encoding etc.)
*   [/rlcard/games](rlcard/games): Various game engines.
*   [/rlcard/models](rlcard/models): Model zoo including pre-trained models and rule models.

## Evaluation
The perfomance is measured by winning rates through tournaments. Example outputs are as follows:
![Learning Curves](http://rlcard.org/imgs/curves.png "Learning Curves")

For your information, there is a nice online evaluation platform [pokerwars](https://github.com/pokerwars) that could be connected with RLCard with some modifications.

## More Documents
For more documentation, please refer to the [Documents](docs/README.md) for general introductions. API documents are available at our [website](http://www.rlcard.org).


## Contributing
Contribution to this project is greatly appreciated! Please create an issue for feedbacks/bugs. If you want to contribute codes, please refer to [Contributing Guide](./CONTRIBUTING.md).

## Acknowledgements
We would like to thank JJ World Network Technology Co.,LTD for the generous support and all the contributions from the community contributors.
