RLCard: A Toolkit for Reinforcement Learning in Card Games
==========================================================

RLCard is an opensource toolkit for devopling Reinforcement Learning
(RL) algorithms in card games. It supports multiple challenging card
game environments with common and easy-to-use interfaces. The goal of
the toolkit is to enable more people to study game AI and push forward
the research of imperfect information games. RLCard is developped by
`DATA Lab <http://faculty.cs.tamu.edu/xiahu/>`__ at Texas A&M
University.

Installation
============

Make sure that you have **Python 3.5+** and **pip** installed. You can
install ``rlcard`` with ``pip`` as follow:

::

    git clone https://github.com/datamllab/rlcard.git
    cd rlcard
    pip install -e .

Getting Started
===============

The interfaces generally follow `OpenAI
gym <https://github.com/openai/gym>`__ style. We recommend to start with
the following **toy examples**. \* `Playing with random
agents <docs/toy-examples.md#playing-with-random-agents>`__ \* `Deep-Q
learning on
Blackjack <docs/toy-examples.md#deep-q-learning-on-blackjack>`__ \*
`DeepCFR on Blackjack <docs/toy-examples.md#deepcfr-on-blackjack>`__

For more examples, please refer to `examples/ <examples>`__.

Documents
=========

Please refer to the `Documents <docs/README.md>`__ for general concepts
desription. API documents are available at our `github
page <https://rlcard.github.io/index.html>`__.

Available Environments
======================

The table below shows the environments that are (or will be soon)
available in RLCard. We provide a complexity estimation for the games on
several aspects. **InfoSet Number:** the number of information set;
**Avg. InfoSet Size:** the average number of states in a single
information set; **Action Size:** the size of the action space. For some
of the complex card games, we can only provide a range of the
estimation. **Name** is the name that should be passed to ``env.make``
to create the game environment.

+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------+---------------------+---------------+-------------------+-------------+
| Game                                                                                                                                                                                                   | InfoSet Number    | Avg. InfoSet Size   | Action Size   | Name              | Status      |
+========================================================================================================================================================================================================+===================+=====================+===============+===================+=============+
| Blackjack (`wiki <https://en.wikipedia.org/wiki/Blackjack>`__, `baike <https://baike.baidu.com/item/21%E7%82%B9/5481683?fr=aladdin>`__)                                                                | 10^3              | 10^1                | 10^0          | blackjack         | Available   |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------+---------------------+---------------+-------------------+-------------+
| Limit Texas Hold'em (`wiki <https://en.wikipedia.org/wiki/Texas_hold_%27em>`__, `baike <https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin>`__)      | 10^14             | 10^3                | 10^0          | limit-holdem      | Available   |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------+---------------------+---------------+-------------------+-------------+
| Dou Dizhu (`wiki <https://en.wikipedia.org/wiki/Dou_dizhu>`__, `baike <https://baike.baidu.com/item/%E6%96%97%E5%9C%B0%E4%B8%BB/177997?fr=aladdin>`__)                                                 | 10^53 ~ 10^83     | 10^23               | 10^4          | doudizhu          | Available   |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------+---------------------+---------------+-------------------+-------------+
| Mahjong (`wiki <https://en.wikipedia.org/wiki/Competition_Mahjong_scoring_rules>`__, `baike <https://baike.baidu.com/item/%E9%BA%BB%E5%B0%86/215>`__)                                                  | 10^121            | 10^48               | 10^2          | -                 | Come soon   |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------+---------------------+---------------+-------------------+-------------+
| No-limit Texas Hold'em (`wiki <https://en.wikipedia.org/wiki/Texas_hold_%27em>`__, `baike <https://baike.baidu.com/item/%E5%BE%B7%E5%85%8B%E8%90%A8%E6%96%AF%E6%89%91%E5%85%8B/83440?fr=aladdin>`__)   | 10^162            | 10^3                | 10^4          | no-limit-holdem   | Available   |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------+---------------------+---------------+-------------------+-------------+
| UNO (`wiki <https://en.wikipedia.org/wiki/Uno_(card_game>`__, `baike <https://baike.baidu.com/item/UNO%E7%89%8C/2249587>`__)                                                                           | 10^163            | 10^10               | 10^1          | -                 | Come soon   |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------+---------------------+---------------+-------------------+-------------+
| Sheng Ji (`wiki <https://en.wikipedia.org/wiki/Sheng_ji>`__, `baike <https://baike.baidu.com/item/%E5%8D%87%E7%BA%A7/3563150>`__)                                                                      | 10^173 ~ 10^180   | 10^61               | 10^13         | -                 | Come soon   |
+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------+---------------------+---------------+-------------------+-------------+

Disclaimer
==========

Please note that this is a **pre-release** version of the RLCard. The
toolkit is provided **"as is"**, without warranty of any kind, express
or implied, including but not limited to the warranties of
merchantability, fitness for a particular purpose and noninfringement.

Acknowledgements
================

We would like to thank JJ World Network Technology Co.,LTD for the
support.
