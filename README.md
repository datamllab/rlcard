# RLCard: A Toolkit for Reinforcement Learning in Card Games
<img width="500" src="./docs/imgs/logo.jpg" alt="Logo" />

[![Build Status](https://travis-ci.org/datamllab/RLCard.svg?branch=master)](https://travis-ci.org/datamllab/RLCard)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/248eb15c086748a4bcc830755f1bd798)](https://www.codacy.com/manual/daochenzha/rlcard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=datamllab/rlcard&amp;utm_campaign=Badge_Grade)
[![Coverage Status](https://coveralls.io/repos/github/datamllab/rlcard/badge.svg)](https://coveralls.io/github/datamllab/rlcard?branch=master)

RLCard is a toolkit for Reinforcement Learning (RL) in card games. It supports multiple card environments with easy-to-use interfaces. The goal of RLCard is to bridge reinforcement learning and imperfect information games, and push forward the research of reinforcement learning in domains with multiple agents, large state and action space, and sparse reward. RLCard is developed by [DATA Lab](http://faculty.cs.tamu.edu/xiahu/) at Texas A&M University.

*   Official Website: [http://www.rlcard.org](http://www.rlcard.org)
*   Paper: [https://arxiv.org/abs/1910.04376](https://arxiv.org/abs/1910.04376)

**News:**
*   PyTorch implementation available. Thanks for the contribution of [@mjudell](https://github.com/mjudell).
*   We have just initialized a list of [Awesome-Game-AI resources](https://github.com/datamllab/awesome-game-ai). Check it out!

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
env.set_agents([RandomAgent()])

trajectories, payoffs = env.run()
```

We also recommend the following **toy examples**.

*   [Playing with random agents](docs/toy-examples.md#playing-with-random-agents)
*   [Deep-Q learning on Blackjack](docs/toy-examples.md#deep-q-learning-on-blackjack)
*   [Running multiple processes](docs/toy-examples.md#running-multiple-processes)
*   [Having fun with pretrained Leduc model](docs/toy-examples.md#having-fun-with-pretrained-leduc-model)
*   [Leduc Hold'em as single-agent environment](docs/toy-examples.md#leduc-holdem-as-single-agent-environment)
*   [Training CFR on Leduc Hold'em](docs/toy-examples.md#training-cfr-on-leduc-holdem)

## Demo
With `tensorflow` installed, run `examples/leduc_holdem_human.py` to play with the pre-trained Leduc Hold'em model. Leduc Hold'em is a simplified version of Texas Hold'em. Rules can be found [here](docs/games.md#leduc-holdem).

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

## Cheat sheet
*   `rlcard.make(env_id, config={})`: Make an environment. `env_id` is a string of a environment; `config` is a dictionary specifying some environment configurations, which are as follows.
	*   `allow_step_back` defualt `False`. True if allowing `step_back` function to traverse backward in the tree.
	*   `allow_raw_data`: default `False`. True if allowing raw data in the `state`.
	*   `single_agent_mode`: default `False`. True if using single agent mode, i.e., Gym style interface with other players as pretrained/rule models.
	*   `active_player`: defualt `0`. If `single_agent_mode` is `True`, `active_player` will specify operating on which player in single agent mode.
	*   `record_action`: Default `False`. If True, a field of `action_record` will be in the state to record the historical actions. This may be used for human-agent play.
*   `env.step(action, raw_action=False)`: Take one step in the environment. `action` can be raw action or integer; `raw_action` should be true if the action is raw action, i,e., string.
*   `env.init_game()`: Initialize a game. Return the state and the first player ID.
*   `env.run()`: Run a complete game and return trajectories and payoffs. The function can be used after the agents are set up.
*   `state`: State will always have observation `state['obs']` and legal actions `state['legal_actions']`. If `allow_raw_data` is `True`, state will have raw observation `state['raw_obs']` and raw legal actions `state['raw_legal_actions']`.

## Documents
Please refer to the [Documents](docs/README.md) for general introductions. API documents are available at our [website](http://www.rlcard.org).

## Available Environments
We provide a complexity estimation for the games on several aspects. **InfoSet Number:** the number of information sets; **Avg. InfoSet Size:** the average number of states in a single information set; **Action Size:** the size of the action space. **Name:** the name that should be passed to `rlcard.make` to create the game environment.

| Game                                                                                                                                                                                           | InfoSet Number  | Avg. InfoSet Size | Action Size | Name            | Status     |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :-------------: | :---------------: | :---------: | :-------------: | :--------: |
| Blackjack ([wiki](https://en.wikipedia.org/wiki/Blackjack), [baike](https://baike.baidu.com/item/21%E7%82%B9/5481683?fr=aladdin))                                                              | 10^3            | 10^1              | 10^0        | blackjack       | Available  |
| Leduc Hold’em ([paper](http://poker.cs.ualberta.ca/publications/UAI05.pdf))                                                                                                                    | 10^2            | 10^2              | 10^0        | leduc-holdem    | Available  |
| Limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em), [baike](https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin))    | 10^14           | 10^3              | 10^0        | limit-holdem    | Available  |
| Dou Dizhu ([wiki](https://en.wikipedia.org/wiki/Dou_dizhu), [baike](https://baike.baidu.com/item/%E6%96%97%E5%9C%B0%E4%B8%BB/177997?fr=aladdin))                                               | 10^53 ~ 10^83   | 10^23             | 10^4        | doudizhu        | Available  |
| Simple Dou Dizhu ([wiki](https://en.wikipedia.org/wiki/Dou_dizhu), [baike](https://baike.baidu.com/item/%E6%96%97%E5%9C%B0%E4%B8%BB/177997?fr=aladdin))                                        | -               | -                 |             | simple-doudizhu | Available  |
| Mahjong ([wiki](https://en.wikipedia.org/wiki/Competition_Mahjong_scoring_rules), [baike](https://baike.baidu.com/item/%E9%BA%BB%E5%B0%86/215))                                                | 10^121          | 10^48             | 10^2        | mahjong         | Available  | 
| No-limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em), [baike](https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin)) | 10^162          | 10^3              | 10^4        | no-limit-holdem | Available  |
| UNO ([wiki](https://en.wikipedia.org/wiki/Uno_\(card_game\)), [baike](https://baike.baidu.com/item/UNO%E7%89%8C/2249587))                                                                      |  10^163         | 10^10             | 10^1        | uno             | Available  |
| Sheng Ji ([wiki](https://en.wikipedia.org/wiki/Sheng_ji), [baike](https://baike.baidu.com/item/%E5%8D%87%E7%BA%A7/3563150))                                                                    | 10^157 ~ 10^165 | 10^61             | 10^11       | -               | Developing |

## Evaluation
The perfomance is measured by winning rates through tournaments. Example outputs are as follows:
![Learning Curves](http://rlcard.org/imgs/curves.png "Learning Curves")

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

## Contributing
Contribution to this project is greatly appreciated! Please create an issue for feedbacks/bugs. If you want to contribute codes, please refer to [Contributing Guide](./CONTRIBUTING.md).

## Acknowledgements
We would like to thank JJ World Network Technology Co.,LTD for the generous support.
