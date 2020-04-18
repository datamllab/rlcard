# RLCard: A Toolkit for Reinforcement Learning in Card Games
<img width="500" src="./docs/imgs/logo.jpg" alt="Logo" />

[![Build Status](https://travis-ci.org/datamllab/RLCard.svg?branch=master)](https://travis-ci.org/datamllab/RLCard)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/248eb15c086748a4bcc830755f1bd798)](https://www.codacy.com/manual/daochenzha/rlcard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=datamllab/rlcard&amp;utm_campaign=Badge_Grade)
[![Coverage Status](https://coveralls.io/repos/github/datamllab/rlcard/badge.svg)](https://coveralls.io/github/datamllab/rlcard?branch=master)

RLCard is a toolkit for Reinforcement Learning (RL) in card games. It supports multiple card environments with easy-to-use interfaces. The goal of RLCard is to bridge reinforcement learning and imperfect information games, and push forward the research of reinforcement learning in domains with multiple agents, large state and action space, and sparse reward. RLCard is developed by [DATA Lab](http://faculty.cs.tamu.edu/xiahu/) at Texas A&M University.

*   Official Website: [http://www.rlcard.org](http://www.rlcard.org)
*   Paper: [https://arxiv.org/abs/1910.04376](https://arxiv.org/abs/1910.04376)

**News:**
*   New game Gin Rummy available. Thanks for the contribution of [@billh0420](https://github.com/billh0420).
*   PyTorch implementation available. Thanks for the contribution of [@mjudell](https://github.com/mjudell).
*   We have just initialized a list of [Awesome-Game-AI resources](https://github.com/datamllab/awesome-game-ai). Check it out!

## Cite this work
If you find this repo useful, you may cite:
```
@article{zha2019rlcard,
  title={RLCard: A Toolkit for Reinforcement Learning in Card Games},
  author={Zha, Daochen and Lai, Kwei-Herng and Cao, Yuanpu and Huang, Songyi and Wei, Ruzhe and Guo, Junyu and Hu, Xia},
  journal={arXiv preprint arXiv:1910.04376},
  year={2019}
}
```

## Installation
Make sure that you have **Python 3.5+** and **pip** installed. We recommend installing `rlcard` with `pip` as follow:

```
git clone https://github.com/datamllab/rlcard.git
cd rlcard
pip install -e .
```
or use PyPI with:
```
pip install rlcard
```
To use tensorflow implementation, run:
```
pip install rlcard[tensorflow]
```
To try out PyTorch implementation for DQN and NFSP, please run: 
```
pip install rlcard[torch]
```
If you meet any problems when installing PyTorch with the command above, you may follow the instructions on [PyTorch official website](https://pytorch.org/get-started/locally/) to manually install PyTorch.

## Examples
Please refer to [examples/](examples). A **short example** is as below.

```python
import rlcard
from rlcard.agents.random_agent import RandomAgent

env = rlcard.make('blackjack')
env.set_agents([RandomAgent(action_num=env.action_num)])

trajectories, payoffs = env.run()
```

We also recommend the following **toy examples**.

*   [Playing with random agents](docs/toy-examples.md#playing-with-random-agents)
*   [Deep-Q learning on Blackjack](docs/toy-examples.md#deep-q-learning-on-blackjack)
*   [Training CFR on Leduc Hold'em](docs/toy-examples.md#training-cfr-on-leduc-holdem)
*   [Having fun with pretrained Leduc model](docs/toy-examples.md#having-fun-with-pretrained-leduc-model)
*   [Leduc Hold'em as single-agent environment](docs/toy-examples.md#leduc-holdem-as-single-agent-environment)
*   [Running multiple processes](docs/toy-examples.md#running-multiple-processes)

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

## Documents
Please refer to the [Documents](docs/README.md) for general introductions. API documents are available at our [website](http://www.rlcard.org).

## Available Environments
We provide a complexity estimation for the games on several aspects. **InfoSet Number:** the number of information sets; **InfoSet Size:** the average number of states in a single information set; **Action Size:** the size of the action space. **Name:** the name that should be passed to `rlcard.make` to create the game environment. We also provide the link to the documentation and the random example.

| Game                                                                                                                                                                                           | InfoSet Number  | InfoSet Size | Action Size | Name            | Usage     |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :-------------: | :---------------: | :---------: | :-------------: | :--------: |
| Blackjack ([wiki](https://en.wikipedia.org/wiki/Blackjack), [baike](https://baike.baidu.com/item/21%E7%82%B9/5481683?fr=aladdin))                                                              | 10^3            | 10^1              | 10^0        | blackjack       | [doc](docs/games.md#blackjack), [example](examples/blackjack_random.py)                     |
| Leduc Hold’em ([paper](http://poker.cs.ualberta.ca/publications/UAI05.pdf))                                                                                                                    | 10^2            | 10^2              | 10^0        | leduc-holdem    | [doc](docs/games.md#leduc-holdem), [example](examples/leduc_holdem_random.py)               |
| Limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em), [baike](https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin))    | 10^14           | 10^3              | 10^0        | limit-holdem    | [doc](docs/games.md#limit-texas-holdem), [example](examples/limit_holdem_random.py)         |
| Dou Dizhu ([wiki](https://en.wikipedia.org/wiki/Dou_dizhu), [baike](https://baike.baidu.com/item/%E6%96%97%E5%9C%B0%E4%B8%BB/177997?fr=aladdin))                                               | 10^53 ~ 10^83   | 10^23             | 10^4        | doudizhu        | [doc](docs/games.md#dou-dizhu), [example](examples/doudizhu_random.py)                      |
| Simple Dou Dizhu ([wiki](https://en.wikipedia.org/wiki/Dou_dizhu), [baike](https://baike.baidu.com/item/%E6%96%97%E5%9C%B0%E4%B8%BB/177997?fr=aladdin))                                        | -               | -                 | -           | simple-doudizhu | [doc](docs/games.md#simple-dou-dizhu), [example](examples/simple_doudizhu_random.py)        |
| Mahjong ([wiki](https://en.wikipedia.org/wiki/Competition_Mahjong_scoring_rules), [baike](https://baike.baidu.com/item/%E9%BA%BB%E5%B0%86/215))                                                | 10^121          | 10^48             | 10^2        | mahjong         | [doc](docs/games.md#mahjong), [example](examples/mahjong_random.py)                         | 
| No-limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em), [baike](https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin)) | 10^162          | 10^3              | 10^4        | no-limit-holdem | [doc](docs/games.md#no-limit-texas-holdem), [example](examples/nolimit_holdem_random.py)    |
| UNO ([wiki](https://en.wikipedia.org/wiki/Uno_\(card_game\)), [baike](https://baike.baidu.com/item/UNO%E7%89%8C/2249587))                                                                      |  10^163         | 10^10             | 10^1        | uno             | [doc](docs/games.md#uno), [example](examples/uno_random.py)                                 |
| Gin Rummy ([wiki](https://en.wikipedia.org/wiki/Gin_rummy), [baike](https://baike.baidu.com/item/%E9%87%91%E6%8B%89%E7%B1%B3/3471710))                                                         | -               | -                 | -           | gin-rummy       | [doc](docs/games.md#gin-rummy), [example](examples/gin_rummy_random.py)                     |

## Evaluation
The perfomance is measured by winning rates through tournaments. Example outputs are as follows:
![Learning Curves](http://rlcard.org/imgs/curves.png "Learning Curves")

## Library Structure
The purposes of the main modules are listed as below:

*   [/examples](examples): Examples of using RLCard.
*   [/docs](docs): Documentation of RLCard.
*   [/tests](tests): Testing scripts for RLCard.
*   [/rlcard/agents](rlcard/agents): Reinforcement learning algorithms and human agents.
*   [/rlcard/envs](rlcard/envs): Environment wrappers (state representation, action encoding etc.)
*   [/rlcard/games](rlcard/games): Various game engines.
*   [/rlcard/models](rlcard/models): Model zoo including pre-trained models and rule models.

## API Cheat Sheet
*   **rlcard.make(env_id, config={})**: Make an environment. `env_id` is a string of a environment; `config` is a dictionary specifying some environment configurations, which are as follows.
	*   `allow_step_back`: Defualt `False`. `True` if allowing `step_back` function to traverse backward in the tree.
	*   `allow_raw_data`: Default `False`. `True` if allowing raw data in the `state`.
	*   `single_agent_mode`: Default `False`. `True` if using single agent mode, i.e., Gym style interface with other players as pretrained/rule models.
	*   `active_player`: Defualt `0`. If `single_agent_mode` is `True`, `active_player` will specify operating on which player in single agent mode.
	*   `record_action`: Default `False`. If `True`, a field of `action_record` will be in the `state` to record the historical actions. This may be used for human-agent play.
*   **env.init_game()**: Initialize a game. Return the state and the first player ID.
*   **env.step(action, raw_action=False)**: Take one step in the environment. `action` can be raw action or integer; `raw_action` should be `True` if the action is raw action (string).
*   **env.step_back()**: Available only when `allow_step_back` is `True`. Take one step backward. This can be used for algorithms that operate on the game tree, such as CFR. 
*   **env.get_payoffs()**: In the end of the game, return a list of payoffs for all the players.
*   **env.get_perfect_information()**: (Currently only support some of the games) Obtain the perfect information at the current state. 
*   **env.set_agents(agents)**: `agents` is a list of `Agent` object. The length of the the list should equal to the number of the player in the game.
*   **env.run(is_training=False)**: Run a complete game and return trajectories and payoffs. The function can be used after the `set_agents` is called. If `is_training` is `True`, the function will use `step` function in the agent to play the game. If `is_training` is `False`, `eval_step` will be called instead.
*   **State Definition**: State will always have observation `state['obs']` and legal actions `state['legal_actions']`. If `allow_raw_data` is `True`, state will have raw observation `state['raw_obs']` and raw legal actions `state['raw_legal_actions']`.

For basic usage, `env.set_agents` and `env.run()` are a good chioce. For advanced useage, you may also play the game step be step with `env.init_game()` and `env.step()`.

## Contributing
Contribution to this project is greatly appreciated! Please create an issue for feedbacks/bugs. If you want to contribute codes, please refer to [Contributing Guide](./CONTRIBUTING.md).

## Acknowledgements
We would like to thank JJ World Network Technology Co.,LTD for the generous support.
