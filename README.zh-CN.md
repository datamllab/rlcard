# RLCard: 卡牌游戏强化学习工具包
<img width="500" src="https://dczha.com/files/rlcard/logo.jpg" alt="Logo" />

[![Testing](https://github.com/datamllab/rlcard/actions/workflows/python-package.yml/badge.svg)](https://github.com/datamllab/rlcard/actions/workflows/python-package.yml)
[![PyPI version](https://badge.fury.io/py/rlcard.svg)](https://badge.fury.io/py/rlcard)
[![Coverage Status](https://coveralls.io/repos/github/datamllab/rlcard/badge.svg)](https://coveralls.io/github/datamllab/rlcard?branch=master)
[![Downloads](https://pepy.tech/badge/rlcard)](https://pepy.tech/project/rlcard)
[![Downloads](https://pepy.tech/badge/rlcard/month)](https://pepy.tech/project/rlcard)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English README](README.md)

RLCard是一款卡牌游戏强化学习 (Reinforcement Learning, RL) 的工具包。 它支持多种卡牌游戏环境，具有易于使用的接口，以用于实现各种强化学习和搜索算法。 RLCard的目标是架起强化学习和非完全信息游戏之间的桥梁。 RLCard由[DATA Lab](http://faculty.cs.tamu.edu/xiahu/) at Rice and Texas A&M University以及社区贡献者共同开发.

*   官方网站：[https://www.rlcard.org](https://www.rlcard.org)
*   Jupyter Notebook教程：[https://github.com/datamllab/rlcard-tutorial](https://github.com/datamllab/rlcard-tutorial)
*   论文：[https://arxiv.org/abs/1910.04376](https://arxiv.org/abs/1910.04376)
*   图形化界面：[RLCard-Showdown](https://github.com/datamllab/rlcard-showdown)
*   斗地主演示：[Demo](https://douzero.org/)
*   资源：[Awesome-Game-AI](https://github.com/datamllab/awesome-game-ai)
*   相关项目：[DouZero项目](https://github.com/kwai/DouZero)
*   知乎：[https://zhuanlan.zhihu.com/p/526723604](https://zhuanlan.zhihu.com/p/526723604)

**社区:**
*  **Slack**: 在我们的[#rlcard-project](https://join.slack.com/t/rlcard/shared_invite/zt-rkvktsaq-xkMwz8BfKupCM6zGhO01xg) slack频道参与讨论.
*  **QQ群**: 加入我们的QQ群讨论。密码：rlcardqqgroup
    *  一群：665647450
    *  二群：117349516

**新闻:**
*   我们更新Jupyter Notebook的教程帮助您快速了解RLCard！请看 [RLCard 教程](https://github.com/datamllab/rlcard-tutorial).
*   所有的算法都已支持[PettingZoo](https://github.com/PettingZoo-Team/PettingZoo)接口. 请点击[这里](examples/pettingzoo). 感谢[Yifei Cheng](https://github.com/ycheng517)的贡献。
*   请关注[DouZero](https://github.com/kwai/DouZero), 一个强大的斗地主AI，以及[ICML 2021论文](https://arxiv.org/abs/2106.06135)。点击[此处](https://douzero.org/)进入在线演示。该算法同样集成到了RLCard中，详见[在斗地主中训练DMC](docs/toy-examples.md#training-dmc-on-dou-dizhu)。
*   我们的项目被用在[PettingZoo](https://github.com/PettingZoo-Team/PettingZoo)中，去看看吧！
*   我们发布了RLCard的可视化演示项目：RLCard-Showdown。请点击[此处](https://github.com/datamllab/rlcard-showdown)查看详情！
*   Jupyter Notebook教程发布了！我们添加了一些R语言的例子，包括用reticulate调用RLCard的Python接口。[点击](docs/toy-examples-r.md)查看详情。
*   感谢[@Clarit7](https://github.com/Clarit7)为支持不同人数的二十一点游戏（Blackjack）做出的贡献。我们欢迎更多的贡献，以使得RLCard中的游戏配置更加多样化。点击[这里](CONTRIBUTING.md#making-configurable-environments)查看详情。
*   感谢[@Clarit7](https://github.com/Clarit7)为二十一点游戏（Blackjack）和限注德州扑克的人机界面做出的贡献。
*   RLCard现支持本地随机环境种子和多进程。感谢[@weepingwillowben](https://github.com/weepingwillowben)提供的测试脚本。
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
如果您访问较慢，国内用户可以通过清华镜像源安装：
```
pip3 install rlcard -i https://pypi.tuna.tsinghua.edu.cn/simple
```
或者，您可以克隆最新版本（如果您访问Github较慢，国内用户可以使用[Gitee镜像](https://gitee.com/daochenzha/rlcard)）：
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

env = rlcard.make('blackjack')
env.set_agents([RandomAgent(num_actions=env.num_actions)])

print(env.num_actions) # 2
print(env.num_players) # 1
print(env.state_shape) # [[2]]
print(env.action_shape) # [None]

trajectories, payoffs = env.run()
```

RLCard可以灵活地连接各种算法，参考以下例子：

*   [小试随机智能体](docs/toy-examples.md#playing-with-random-agents)
*   [Blackjack上的Deep-Q学习](docs/toy-examples.md#deep-q-learning-on-blackjack)
*   [在Leduc Hold'em上训练CFR(机会抽样)](docs/toy-examples.md#training-cfr-on-leduc-holdem)
*   [与预训练Leduc模型游玩](docs/toy-examples.md#having-fun-with-pretrained-leduc-model)
*   [在斗地主上训练DMC](docs/toy-examples.md#training-dmc-on-dou-dizhu)
*   [评估智能体](docs/toy-examples.md#evaluating-agents)
*   [在PettingZoo上训练](examples/pettingzoo)

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
我们也提供图形界面以实现更便捷的调试，详情请查看[这里](https://github.com/datamllab/rlcard-showdown/)。以下是一些演示：

![斗地主回放](https://github.com/datamllab/rlcard-showdown/blob/master/docs/imgs/doudizhu-replay.png?raw=true)
![Leduc回放](https://github.com/datamllab/rlcard-showdown/blob/master/docs/imgs/leduc-replay.png?raw=true)

## 可用环境
我们从不同角度提供每种游戏的估算复杂度。
**InfoSet数量：** 信息集数量；**InfoSet尺寸：** 单个信息集的平均状态数量；**状态尺寸：** 状态空间的尺寸；**环境名：** 应该传入`rlcard.make`以创建新游戏环境的名称。除此之外，我们也提供每种环境的文档链接和随机智能体释例。

| 游戏                                                                                                                                                                                                         | InfoSet数量     | InfoSet尺寸       | 状态尺寸    | 环境名          | 用法                                                                                       |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | :-------------: | :---------------: | :---------: | :-------------: | :--------------------------------------------------------------------------------------------------: |
| 二十一点 Blackjack ([wiki](https://en.wikipedia.org/wiki/Blackjack), [百科](https://baike.baidu.com/item/21%E7%82%B9/5481683?fr=aladdin))                                                                    | 10^3            | 10^1              | 10^0        | blackjack       | [文档](docs/games.md#blackjack), [释例]](examples/run_random.py)                                     |
| Leduc Hold’em ([论文](http://poker.cs.ualberta.ca/publications/UAI05.pdf))                                                                                                                                   | 10^2            | 10^2              | 10^0        | leduc-holdem    | [文档](docs/games.md#leduc-holdem), [释例](examples/run_random.py)                                   |
| 限注德州扑克 Limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em), [百科](https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin))      | 10^14           | 10^3              | 10^0        | limit-holdem    | [文档](docs/games.md#limit-texas-holdem), [释例](examples/run_random.py)                             |
| 斗地主 Dou Dizhu ([wiki](https://en.wikipedia.org/wiki/Dou_dizhu), [百科](https://baike.baidu.com/item/%E6%96%97%E5%9C%B0%E4%B8%BB/177997?fr=aladdin))                                                       | 10^53 ~ 10^83   | 10^23             | 10^4        | doudizhu        | [文档](docs/games.md#dou-dizhu), [释例](examples/run_random.py)                                      |
| 麻将 Mahjong ([wiki](https://en.wikipedia.org/wiki/Competition_Mahjong_scoring_rules), [百科](https://baike.baidu.com/item/%E9%BA%BB%E5%B0%86/215))                                                          | 10^121          | 10^48             | 10^2        | mahjong         | [文档](docs/games.md#mahjong), [释例](examples/run_random.py)                                        | 
| 无限注德州扑克 No-limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em), [百科](https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin)) | 10^162          | 10^3              | 10^4        | no-limit-holdem | [文档](docs/games.md#no-limit-texas-holdem), [释例](examples/run_random.py)                          |
| UNO ([wiki](https://en.wikipedia.org/wiki/Uno_\(card_game\)), [百科](https://baike.baidu.com/item/UNO%E7%89%8C/2249587))                                                                                     |  10^163         | 10^10             | 10^1        | uno             | [文档](docs/games.md#uno), [释例](examples/run_random.py)                                            |
| Gin Rummy ([wiki](https://en.wikipedia.org/wiki/Gin_rummy), [百科](https://baike.baidu.com/item/%E9%87%91%E6%8B%89%E7%B1%B3/3471710))                                                                        | 10^52           | -                 | -           | gin-rummy       | [文档](docs/games.md#gin-rummy), [释例](examples/run_random.py)                                      |
| 桥牌 ([wiki](https://en.wikipedia.org/wiki/Bridge), [baike](https://baike.baidu.com/item/%E6%A1%A5%E7%89%8C/332030))                                                                                         |                 | -                 | -           | bridge          | [文档](docs/games.md#bridge), [释例](examples/run_random.py)                                         |

## 支持算法
| 算法                                                          | 释例                                        | 参考                                                                                                    |
| :-----------------------------------------------------------: | :-----------------------------------------: | :-----------------------------------------------------------------------------------------------------: |
| 深度蒙特卡洛（Deep Monte-Carlo，DMC）                         | [examples/run\_dmc.py](examples/run_dmc.py) | [[论文]](https://arxiv.org/abs/2106.06135)                                                              |
| 深度Q学习 （Deep Q Learning, DQN）                            | [examples/run\_rl.py](examples/run_rl.py)   | [[论文]](https://arxiv.org/abs/1312.5602)                                                               |
| 虚拟自我对局 （Neural Fictitious Self-Play，NFSP）            | [examples/run\_rl.py](examples/run_rl.py)     | [[论文]](https://arxiv.org/abs/1603.01121)                                                            |
| 虚拟遗憾最小化算法（Counterfactual Regret Minimization，CFR） | [examples/run\_cfr.py](examples/run_cfr.py) | [[论文]](http://papers.nips.cc/paper/3306-regret-minimization-in-games-with-incomplete-information.pdf) |

## 预训练和基于规则的模型
我们提供了一个[模型集合](rlcard/models)作为基准线。

| 模型                                     | 解释                                              |
| :--------------------------------------: | :-----------------------------------------------: |
| leduc-holdem-cfr                         | Leduc Hold'em上的预训练CFR（机会抽样）模型        |
| leduc-holdem-rule-v1                     | 基于规则的Leduc Hold'em模型，v1                   |
| leduc-holdem-rule-v2                     | 基于规则的Leduc Hold'em模型，v2                   |
| uno-rule-v1                              | 基于规则的UNO模型，v1                             |
| limit-holdem-rule-v1                     | 基于规则的限注德州扑克模型，v1                    |
| doudizhu-rule-v1                         | 基于规则的斗地主模型，v1                          |
| gin-rummy-novice-rule                    | Gin Rummy新手规则模型                             |

## API小抄
### 如何创建新的环境
您可以使用以下的接口创建新环境，并且可以用字典传入一些可选配置项
*   **env = rlcard.make(env_id, config={})**: 创建一个环境。`env_id`是环境的字符串代号；`config`是一个包含一些环境配置的字典，具体包括：
	*   `seed`：默认值`None`。设置一个本地随机环境种子用以复现结果。
	*   `allow_step_back`: 默认值`False`. `True`将允许`step_back`函数用以回溯遍历游戏树。
	*   其他特定游戏配置：这些配置将以`game_`开头。目前我们只支持配置Blackjack游戏中的玩家数量`game_num_players`。

环境创建完成后，我们就能访问一些游戏信息。
*   **env.num_actions**: 状态数量。
*   **env.num_players**: 玩家数量。
*   **env.state_shape**: 观测到的状态空间的形状（shape）。
*   **env.action_shape**: 状态特征的形状（shape），斗地主的状态可以被编码为特征。

### RLCard中的状态是什么
状态（State）是一个Python字典。它包括观测值`state['obs']`，合规动作`state['legal_actions']`，原始观测值`state['raw_obs']`和原始合规动作`state['raw_legal_actions']`。

### 基础接口
以下接口提供基础功能，虽然其简单易用，但会对智能体做出一些前提假设。智能体必须符合[智能体模版](docs/developping-algorithms.md)。
*   **env.set_agents(agents)**: `agents`是`Agent`对象的列表。列表长度必须等于游戏中的玩家数量。
*   **env.run(is_training=False)**: 运行一局完整游戏并返回轨迹（trajectories）和回报（payoffs）。该函数可以在`set_agents`被调用之后调用。如果`is_training`设定为`True`，它将使用智能体中的`step`函数来进行游戏；如果`is_training`设定为`False`，则会调用`eval_step`。

### 高级接口
对于更高级的方法，可以使用以下接口来对游戏树进行更灵活的操作。这些接口不会对智能体有前提假设。
*   **env.reset()**: 初始化一个游戏，返回状态和第一个玩家的ID。
*   **env.step(action, raw_action=False)**: 推进环境到下一步骤。`action`可以是一个原始动作或整型数值；当传入原始动作（字符串）时，`raw_action`应该被设置为`True`。
*   **env.step_back()**: 只有当`allow_step_back`设定为`True`时可用，向后回溯一步。 该函数可以被用在需要操作游戏树的算法中，例如CFR（机会抽样）。
*   **env.is_over()**: 如果当前游戏结束，则返回`True`，否则返回`False`。
*   **env.get_player_id()**: 返回当前玩家的ID。
*   **env.get_state(player_id)**: 返回玩家ID`player_id`对应的状态。
*   **env.get_payoffs()**: 在游戏结束时，返回所有玩家的回报（payoffs）列表。
*   **env.get_perfect_information()**: （目前仅支持部分游戏）获取当前状态的完全信息。

## 库结构
主要模块的功能如下：

*   [/examples](examples): 使用RLCard的一些样例。
*   [/docs](docs): RLCard的文档。
*   [/tests](tests): RLCard的测试脚本。
*   [/rlcard/agents](rlcard/agents): 强化学习算法以及人类智能体。
*   [/rlcard/envs](rlcard/envs): 环境包装（状态表述，动作编码等）。
*   [/rlcard/games](rlcard/games): 不同的游戏引擎。
*   [/rlcard/models](rlcard/models): 包括预训练模型和规则模型在内的模型集合。

## 更多文档
请参考[这里](docs/README.md)查阅更多文档[Documents](docs/README.md)。API文档在我们的[网站](http://www.rlcard.org)中。

## 贡献
我们非常感谢对本项目的贡献！请为反馈或漏洞创建Issue。如果您想恭喜代码，请参考[贡献指引](./CONTRIBUTING.md)。如果您有任何问题，请联系通过[daochen.zha@rice.edu](mailto:daochen.zha@rice.edu)联系[Daochen Zha](https://github.com/daochenzha)

## 致谢
我们诚挚的感谢竞技世界网络技术有限公司（JJ World Network Technology Co.,LTD）为本项目提供的大力支持，以及所有来自社区成员的贡献。
