# RLCard: A Toolkit for Reinforcement Learning in Card Games
RLCard is an opensource toolkit for devopling Reinforcement Learning (RL) algorithms in card games. It supports multiple challenging card game environments with common and easy-to-use interfaces. The  goal  of  the  toolkit  is  to  enable  more  people  to  study  game  AI  and  push  forward  the  research of imperfect information games. RLCard is developped by [DATA Lab](http://faculty.cs.tamu.edu/xiahu/) at Texas A&M University.

# Installation
Make sure that you have **Python 3.5+** and **pip** installed. You can install `rlcard` with `pip` as follow:
```
git clone https://github.com/datamllab/rlcard.git
cd rlcard
pip install -e .
```

# Getting Started
The interfaces generally follow [OpenAI gym](https://github.com/openai/gym) style. You are recommended to start with the following **toy examples**.
* Play with random agents
* Deep-Q learning on Blackjack
* DeepCFR on Blackjack

For more examples, please refer to [examples/](examples).

# Documents
Please refer to the [Documents](docs/README.md) for general concepts desription. API documents are available at our [github page](https://rlcard.github.io/index.html).

# Available Environments
The table below shows the environments that are (or will be soon) available in RLCard. We provide a complexity estimation for the games on several aspects. **InfoSet Number:** the number of information set; **Avg. InfoSet Size:** the average number of states in a single information set; **Action Size:** the size of the action space (without abstraction). For some of the large card games, obtaining the statistics is computationally challenging, and thus they are 'unknown' to us. **Name** is the name you should pass to `env.make` to create the game environment.

| Game                     | InfoSet Number  |Avg. InfoSet Size | Action Size | Name | Status  |
| ------------------------ |:--------------:| :-------:|:------:| :-------:| :-------:|
| Blackjack ([wiki](https://en.wikipedia.org/wiki/Blackjack), [baike](https://baike.baidu.com/item/21%E7%82%B9/5481683?fr=aladdin)) | 10^3      |  10^1 | 10^0 | blackjack |Available |
| Limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em), [baike](https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin))    |10^14 | 10^3| 10^0 | limit-holdem |Available |
| No-limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em), [baike](https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin))      |10^162 | 10^3| 10^4 | no-limit-holdem|Available |
| Two-player UNO ([wiki](https://en.wikipedia.org/wiki/Uno_\(card_game), [baike](https://baike.baidu.com/item/UNO%E7%89%8C/2249587))      |  unknown      |   unknown | 10^1| - | Come soon|
| Mahjong ([wiki](https://en.wikipedia.org/wiki/Competition_Mahjong_scoring_rules), [baike](https://baike.baidu.com/item/%E9%BA%BB%E5%B0%86/215))      | 10^121      |   10^48 |10^2 | - | Come soon| 
| Dou Dizhu ([wiki](https://en.wikipedia.org/wiki/Dou_dizhu), [baike](https://baike.baidu.com/item/%E6%96%97%E5%9C%B0%E4%B8%BB/177997?fr=aladdin))      | unknown      |   unknown | 10^4| doudizhu | Available|
| Sheng Ji ([wiki](https://en.wikipedia.org/wiki/Sheng_ji), [baike](https://baike.baidu.com/item/%E5%8D%87%E7%BA%A7/3563150))      | unknown      |   unknown | unknown | - | Come soon|



# Disclaimer
Please note that this is a **pre-release** version of the RLCard. The toolkit is provided **"as is"**, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement.

# Acknowledgements
We would like to thank JJ World Network Technology Co.,LTD for the technical support.

