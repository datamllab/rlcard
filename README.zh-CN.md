# RLCard: 卡牌游戏强化学习工具包
<img width="500" src="https://dczha.com/files/rlcard/logo.jpg" alt="Logo" />

[![Build Status](https://travis-ci.org/datamllab/RLCard.svg?branch=master)](https://travis-ci.org/datamllab/RLCard)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/248eb15c086748a4bcc830755f1bd798)](https://www.codacy.com/manual/daochenzha/rlcard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=datamllab/rlcard&amp;utm_campaign=Badge_Grade)
[![Coverage Status](https://coveralls.io/repos/github/datamllab/rlcard/badge.svg)](https://coveralls.io/github/datamllab/rlcard?branch=master)
[![Downloads](https://pepy.tech/badge/rlcard)](https://pepy.tech/project/rlcard)
[![Downloads](https://pepy.tech/badge/rlcard/month)](https://pepy.tech/project/rlcard)

[English README](README.md)

RLCard是一款卡牌游戏强化学习 (Reinforcement Learning, RL) 的工具包。 它支持多种卡牌游戏环境，具有易于使用的接口，以用于实现各种强化学习和搜索算法。 RLCard的目标是架起强化学习和非完全信息游戏之间的桥梁。 RLCard由[DATA Lab](http://faculty.cs.tamu.edu/xiahu/) at Texas A&M University以及社区贡献者共同开发.

*   官方网站：[https://www.rlcard.org](https://www.rlcard.org)
*   Jupyter Notebook教程：[https://github.com/datamllab/rlcard-tutorial](https://github.com/datamllab/rlcard-tutorial)
*   论文：[https://arxiv.org/abs/1910.04376](https://arxiv.org/abs/1910.04376)
*   图形化界面：[RLCard-Showdown](https://github.com/datamllab/rlcard-showdown)
*   斗地主演示：[Demo](https://douzero.org/)
*   资源：[Awesome-Game-AI](https://github.com/datamllab/awesome-game-ai)
*   相关项目：[DouZero项目](https://github.com/kwai/DouZero)

**社区:**
*  **Slack**: 在我们的[#rlcard-project](https://join.slack.com/t/rlcard/shared_invite/zt-rkvktsaq-xkMwz8BfKupCM6zGhO01xg) slack频道参与讨论.
*  **QQ群**: 加入我们的QQ群665647450. 密码：rlcardqqgroup

**新闻:**
*   请关注[DouZero](https://github.com/kwai/DouZero), 一个强大的斗地主AI，以及[ICML 2021论文](https://arxiv.org/abs/2106.06135)。点击[这里]进入在线演示(https://douzero.org/)。该算法同样集成到了RLCard中，详见[在斗地主中训练DMC](docs/toy-examples.md#training-dmc-on-dou-dizhu)。
*   我们的项目被用在[PettingZoo](https://github.com/PettingZoo-Team/PettingZoo)中，去看看吧!
*   我们发布了RLCard的可视化演示项目：RLCard-Showdown。请点击[这里]查看详情(https://github.com/datamllab/rlcard-showdown)！
*   Jupyter Notebook教程发布了！我们添加了一些R语言的例子，包括用reticulate调用RLCard的Python接口。[点击](docs/toy-examples-r.md)查看详情。
*   感谢[@Clarit7](https://github.com/Clarit7)为支持不同人数的Blackjack做出的贡献。我们欢迎更多的贡献，使得RLCard中的游戏配置更加多样化。点击[这里](CONTRIBUTING.md#making-configurable-environments)查看详情。
*   感谢[@Clarit7](https://github.com/Clarit7)为Blackjack和限注德州扑克的人机界面做出的贡献。
*   现在RLCard支持本地随机环境种子和多进程。感谢[@weepingwillowben](https://github.com/weepingwillowben)提供的测试脚本。
*   无限注德州扑克人机界面现已可用。无限注德州扑克的动作空间已被抽象化。感谢[@AdrianP-](https://github.com/AdrianP-)做出的贡献。
*   新游戏Gin Rummy以及其可视化人机界面现已可用，感谢[@billh0420](https://github.com/billh0420)做出的贡献。
*   PyTorch实现现已可用，感谢[@mjudell](https://github.com/mjudell)做出的恭喜。

## 引用
如果本项目对您有帮助，请添加引用：

Zha, Daochen, et al. "RLCard: A Platform for Reinforcement Learning in Card Games." IJCAI. 2020.
```bibtex
@inproceedings{zha2020rlcard,
  title={RLCard: A Platform for Reinforcement Learning in Card Games},
  author={Zha, Daochen and Lai, Kwei-Herng and Huang, Songyi and Cao, Yuanpu and Reddy, Keerthana and Vargas, Juan and Nguyen, Alex and Wei, Ruzhe and Guo, Junyu and Hu, Xia},
  booktitle={IJCAI},
  year={2020}
}
```

## 安装
确保您已安装**Python 3.6+**和**pip**。我们推荐您使用`pip`安装稳定版本`rlcard`：

```
pip3 install rlcard
```
默认安装方式只包括卡牌环境。如果想使用PyTorch实现的训练算法，运行
```
pip3 install rlcard[torch]
```
或者，您可以克隆最新版本：
```
git clone https://github.com/datamllab/rlcard.git
```
或使只克隆一个分支以使其更快
```
git clone -b master --single-branch --depth=1 https://github.com/datamllab/rlcard.git
```
然后运行以下命令进行安装
```
cd rlcard
pip3 install -e .
pip3 install -e .[torch]
```

我们也提供[**conda**安装方法](https://anaconda.org/toubun/rlcard):

```
conda install -c toubun rlcard
```

Conda安装只包含卡牌环境，您需要按照您的需求手动安装PyTorch。

## 释例
以下是一个**小例子**

```python
import rlcard
from rlcard.agents import RandomAgent

print(env.num_actions) # 2
print(env.num_players) # 1
print(env.state_shape) # [[2]]
print(env.action_shape) # [None]

env = rlcard.make('blackjack')
env.set_agents([RandomAgent(num_actions=env.num_actions)])

trajectories, payoffs = env.run()
```

RLCard可以灵活地连接到各种算法中，参考以下例子：

*   [小试随机智能体](docs/toy-examples.md#playing-with-random-agents)
*   [Blackjack上的Deep-Q学习](docs/toy-examples.md#deep-q-learning-on-blackjack)
*   [在Leduc Hold'em上训练CFR(机会抽样)](docs/toy-examples.md#training-cfr-on-leduc-holdem)
*   [与预训练Leduc模型游玩](docs/toy-examples.md#having-fun-with-pretrained-leduc-model)
*   [在斗地主上训练DMC](docs/toy-examples.md#training-dmc-on-dou-dizhu)
*   [评估智能体](docs/toy-examples.md#evaluating-agents)

## 演示

运行`examples/human/leduc_holdem_human.py`来游玩预训练的Leduc Hold'em模型。Leduc Hold'em是简化版的德州扑克，具体规则可以参考[这里](docs/games.md#leduc-holdem)。

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
| Mahjong ([wiki](https://en.wikipedia.org/wiki/Competition_Mahjong_scoring_rules), [baike](https://baike.baidu.com/item/%E9%BA%BB%E5%B0%86/215))                                                | 10^121          | 10^48             | 10^2        | mahjong         | [doc](docs/games.md#mahjong), [example](examples/mahjong_random.py)                         | 
| No-limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em), [baike](https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin)) | 10^162          | 10^3              | 10^4        | no-limit-holdem | [doc](docs/games.md#no-limit-texas-holdem), [example](examples/nolimit_holdem_random.py)    |
| UNO ([wiki](https://en.wikipedia.org/wiki/Uno_\(card_game\)), [baike](https://baike.baidu.com/item/UNO%E7%89%8C/2249587))                                                                      |  10^163         | 10^10             | 10^1        | uno             | [doc](docs/games.md#uno), [example](examples/uno_random.py)                                 |
| Gin Rummy ([wiki](https://en.wikipedia.org/wiki/Gin_rummy), [baike](https://baike.baidu.com/item/%E9%87%91%E6%8B%89%E7%B1%B3/3471710))                                                         | 10^52           | -                 | -           | gin-rummy       | [doc](docs/games.md#gin-rummy), [example](examples/gin_rummy_random.py)                     |

## Supported Algorithms
| Algorithm | example | reference |
| :--------------------------------------: | :-----------------------------------------: | :------------------------------------------------------------------------------------------------------: |
| Deep Monte-Carlo (DMC)                   | [examples/run\_dmc.py](examples/run_dmc.py) | [[paper]](https://arxiv.org/abs/2106.06135)                                                              |
| Deep Q-Learning (DQN)                    | [examples/run\_rl.py](examples/run_rl.py)   | [[paper]](https://arxiv.org/abs/1312.5602)                                                               |
| Neural Fictitious Self-Play (NFSP)       | [examples/run\_rl.py](examples/run_rl.py)   | [[paper]](https://arxiv.org/abs/1603.01121)                                                              |
| Counterfactual Regret Minimization (CFR) | [examples/run\_cfr.py](examples/run_cfr.py) | [[paper]](http://papers.nips.cc/paper/3306-regret-minimization-in-games-with-incomplete-information.pdf) |

## Pre-trained and Rule-based Models
We provide a [model zoo](rlcard/models) to serve as the baselines.

| Model                                    | Explanation                                              |
| :--------------------------------------: | :------------------------------------------------------: |
| leduc-holdem-cfr                         | Pre-trained CFR (chance sampling) model on Leduc Hold'em |
| leduc-holdem-rule-v1                     | Rule-based model for Leduc Hold'em, v1                   |
| leduc-holdem-rule-v2                     | Rule-based model for Leduc Hold'em, v2                   |
| uno-rule-v1                              | Rule-based model for UNO, v1                             |
| limit-holdem-rule-v1                     | Rule-based model for Limit Texas Hold'em, v1             |
| doudizhu-rule-v1                         | Rule-based model for Dou Dizhu, v1                       |
| gin-rummy-novice-rule                    | Gin Rummy novice rule model                              |

## API Cheat Sheet
### How to create an environment
You can use the the following interface to make an environment. You may optionally specify some configurations with a dictionary.
*   **env = rlcard.make(env_id, config={})**: Make an environment. `env_id` is a string of a environment; `config` is a dictionary that specifies some environment configurations, which are as follows.
	*   `seed`: Default `None`. Set a environment local random seed for reproducing the results.
	*   `allow_step_back`: Defualt `False`. `True` if allowing `step_back` function to traverse backward in the tree.
	*   Game specific configurations: These fields start with `game_`. Currently, we only support `game_num_players` in Blackjack, .

Once the environemnt is made, we can access some information of the game.
*   **env.num_actions**: The number of actions.
*   **env.num_players**: The number of players.
*   **env.state_shape**: The shape of the state space of the observations.
*   **env.action_shape**: The shape of the action features (Dou Dizhu's action can encoded as features)

### What is state in RLCard
State is a Python dictionary. It consists of observation `state['obs']`, legal actions `state['legal_actions']`, raw observation `state['raw_obs']` and raw legal actions `state['raw_legal_actions']`.

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

## Library Structure
The purposes of the main modules are listed as below:

*   [/examples](examples): Examples of using RLCard.
*   [/docs](docs): Documentation of RLCard.
*   [/tests](tests): Testing scripts for RLCard.
*   [/rlcard/agents](rlcard/agents): Reinforcement learning algorithms and human agents.
*   [/rlcard/envs](rlcard/envs): Environment wrappers (state representation, action encoding etc.)
*   [/rlcard/games](rlcard/games): Various game engines.
*   [/rlcard/models](rlcard/models): Model zoo including pre-trained models and rule models.

## More Documents
For more documentation, please refer to the [Documents](docs/README.md) for general introductions. API documents are available at our [website](http://www.rlcard.org).

## Contributing
Contribution to this project is greatly appreciated! Please create an issue for feedbacks/bugs. If you want to contribute codes, please refer to [Contributing Guide](./CONTRIBUTING.md). If you have any questions, please contact [Daochen Zha](https://github.com/daochenzha) with [daochen.zha@tamu.edu](mailto:daochen.zha@tamu.edu).

## Acknowledgements
We would like to thank JJ World Network Technology Co.,LTD for the generous support and all the contributions from the community contributors.
