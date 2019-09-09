# Index
* [Blackjack](docs/games.md#blackjack)
* [Limit Texas Hold'em](docs/games.md#limit-texas-holdem)
* [No-limit Texas Hold'em](docs/games.md#no-limit-texas-holdem)
* [Dou Dizhu](docs/games.md#dou-dizhu)
# Blackjack
Blackjack is a globally popular banking game known as Twenty-One. The objective is to beat the dealer by reaching a higher score than the dealer without exceeding 21. In the toolkit, we implement a simple version of Blackjack. In each round, the player only has two options: "hit" which will take a card, and 'stand' which end the turn. The player will "bust" if his hands exceed 21 points.
## State Encoding
In this toy environment, we encode the state as an array `[player_score, dealer_score]` where `player_score` is the score currently obtained by the player, and the `dealer_score` is derived from the card that faces up from the dealer.
## Action Encoding
There are two actions in the simple Blackjack. They are encoded as follows:

| Action ID                     | Action  |
| ------------------------ |:--------------|
| 0 | hit |
| 1 | stand |

# Limit Texas Hold'em
test
# No-limit Texas Hold'em
test
# Doudizhu

Doudizhu is one of the most popular card game in China.  The standard version of Doudizhu is played by three people with  one pack of 54 cards including two different jokers. After bidding, one player would be the "landlord" who can get extra three face-down cards, and the other two would be "peasants" to against the landlord together.  The objective of the game is to be the first player to have no cards left. In the toolkit, we implement a standard version of Doudizhu of three players. In bidding phase, we designate one of the players as the "landlord" according to the number of some key cards. In each round of playing cards phase, the starting player must play a card or some cards, the next players is free to decide whether to follow and play cards or not. Until there are two consecutive players to choose "pass", one round will end. The player who played the greatest cards will be the first to play in the next round. In first round, the "landlord" would first play cards.

## State Information Set


Each step of the game will produces a state information set, a readable dictionary of Python, whose entries can be freely selected and encoded. The following table is an example of state information set.



| KEY          |                            VALUE                             |                       ILLUSTRATION                       |
| ------------ | :----------------------------------------------------------- | -------------------------------------------------------- |
| deck         | 3333444455556666<br>777788889999TTTTJJJJ<br>QQQQKKKKAAAA2222BR | One pack of 54 cards<br>with two different jokers(T: 10) |
| cards_seen   |                             TQA                              |  Three cards distributed to the landlord after bidding   |
| landlord     |                              0                               |                The player_id of landlord                 |
| self         |                              2                               |                   Current player's id                    |
| hand         |                      3456677799TJQKAAB                       |     All cards current player owned when a game start     |
| trace        | [(0, '8222'), (1, 'pass'), (2, 'pass'), (0 '6KKK'), (1, 'pass'), (2, 'pass'), (0, '8'), (1, 'Q')] |             A record of  actions in one game             |
| cards_played |      ['6', '8', '8', 'Q', 'K', 'K', 'K', '2', '2', '2']      |          The cards have been played in one game          |
| cards_others |                 333444555678899TTTJJJQQAA2R                  |            The union of other player's cards             |
| remaining    |                      3456677799TJQKAAB                       |          The remaining cards of current player           |
| actions      |                   ['pass', 'K', 'A', 'B']                    |     The legal actions the current player could play      |
|              |                                                              |                                                          |

## State Encoding


In this doudizhu environment,  we choose six features from state information set for encoding: current player's remaining cards, the union of other players' cards, recent three actions from trace, union of played cards. We encode these features as an 6×60 array of 0 and 1.  The cards have 15 ranks from 3 to red joker and 4 suits, so we use 1×60 vector to represent the cards of one feature to make sure that every digit is 0 or 1. 

## Action Encoding


The original action space of doudizhu is very large. It has 33676 specific actions in all. In order to compress the training time and improve training effect, we simplify the actions to 309 abstract actions. The principle is to make the kicker fuzzy and focus on major. For example, '33345' -> '333**' . The abstractions are as follows:

| TYPE             | SPECIFIC QUANTITY | ABSTRACT QUANTITY |
| ---------------- | :---------------: | :---------------: |
| Solo             |        15         |        15         |
| pair             |        13         |        13         |
| Trio             |        13         |        13         |
| Trio with single |        182        |        13         |
| Trio with pair   |        156        |        13         |
| Plane with solo  |       24721       |        38         |
| Plane with pair  |       6552        |        30         |
| Chain of solo    |        36         |        36         |
| Chain of pair    |        52         |        52         |
| Chain of trio    |        45         |        45         |
| Quad with solo   |       1339        |        13         |
| Quad with pair   |       1014        |        13         |
| Bomb             |        13         |        13         |
| Rocket           |         1         |         1         |
| Pass             |         1         |         1         |
| Total            |       33676       |        309        |

After abstraction, we encode 309 abstract actions to digit from 0 to 308.