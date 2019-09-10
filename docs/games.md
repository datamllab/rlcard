# Index
* [Blackjack](docs/games.md#blackjack)
* [Limit Texas Hold'em](docs/games.md#limit-texas-holdem)
* [No-limit Texas Hold'em](docs/games.md#no-limit-texas-holdem)
* [Dou Dizhu](docs/games.md#dou-dizhu)
# Blackjack
Blackjack is a globally popular banking game known as Twenty-One. The objective is to beat the dealer by reaching a higher score than the dealer without exceeding 21. In the toolkit, we implement a simple version of Blackjack. In each round, the player only has two options: "hit" which will take a card, and 'stand' which end the turn. The player will "bust" if his hands exceed 21 points. After the player completes his hands (chooses "stand" and has not busted), the dealer then reals his hidden card and "hit" until obtaining at least 17 points.
## State Encoding
In this toy environment, we encode the state as an array `[player_score, dealer_score]` where `player_score` is the score currently obtained by the player, and the `dealer_score` is derived from the card that faces up from the dealer.
## Action Decoding
There are two actions in the simple Blackjack. They are encoded as follows:

| Action ID                     | Action  |
| ------------------------ |:--------------|
| 0 | hit |
| 1 | stand |

# Limit Texas Hold'em
test
# No-limit Texas Hold'em
test
# Dou Dizhu

Doudizhu is one of the most popular Chinese card games with hundreds of millions of players. It is played by three people with one pack of 54 cards including a red joker and a black joker. After bidding, one player would be the "landlord" who can get an extra three cards, and the other two would be "peasants" who work together to fight against the landlord. In each round of the game, the starting player must play a card or a combination, and the other two players can decide whether to follow or "pass." A round is finished if two consecutive players choose "pass." The player who played the cards with the highest rank will be the first to play in the next round. The objective of the game is to be the first player to get rid of all the cards in hand. For detailed rules, please refer to [Wikipedia](https://en.wikipedia.org/wiki/Dou_dizhu) or  [Baike](https://baike.baidu.com/item/%E6%96%97%E5%9C%B0%E4%B8%BB/177997?fr=aladdin).

In the toolkit, we implement a standard version of Doudizhu. In the bidding phase, we heuristically designate one of the players as the "landlord." Specifically, we count the number of key cards or combinations (high-rank cards and bombs), and the player with the most powerful hand is chosen as "lanlord."

## State
At each decision point of the game, the corresponding player will be able to observe the current state (or information set in imperfect information game). The state consists of all the information that the player can observe from his view. We encode the information into a readable Python dictionary. The following table shows the structure of the state:

| KEY          | DESCRIPTION                                                  | VALUE OF AN EXAMPLE                                         |
| ------------ | :----------------------------------------------------------- | ------------------------------------------------------------ |
| deck         | A string of one pack of 54 cards with Black Joker and Red Joker. Each character means a card. For conciseness, we use 'T' for '10'. | 3333444455556666<br/>777788889999TTTTJJJJ<br/>QQQQKKKKAAAA2222BR  |
| cards_seen   | Three face-down cards distributed to the landlord after bidding. Then these cards will be made public to all players. | TQA                                                          |
| landlord     | An integer of landlord's id                                  | 0                                                            |
| self         | An integer of current player's id                            | 2                                                            |
| hand         | All cards current player initially owned when a game starts. It will not change with playing cards. | 3456677799TJQKAAB                                            |
| trace        | A list of tuples which records every actions in one game. The first entry of  the tuple is player's id, the second is corresponding player's action. | [(0, '8222'), (1, 'pass'), (2, 'pass'), (0 '6KKK'), (1, 'pass'), (2, 'pass'), (0, '8'), (1, 'Q')] |
| cards_played | The cards which have been played and sorted from low to high in one game | ['6', '8', '8', 'Q', 'K', 'K', 'K', '2', '2', '2']           |
| cards_others | The union of other player's cards                            | 333444555678899TTTJJJQQAA2R                                  |
| remaining    | The remaining cards of current player                        | 3456677799TJQKAAB                                            |
| actions      | The legal actions the current player could do                | ['pass', 'K', 'A', 'B']                                      |

## State Encoding
In Dou Dizhu environment, we encode the state into 6 feature planes. The size of each plane is 5*15. Each entry of a plane can be either 1 or 0. Note that the current encoding method is just an example to show how the feature can be encoded. Users are encouraged to encode the state for their own purposes by modifying `extract_state` function in [rlcard/envs/doudizhu.py](rlcard/envs/doudizhu.py). The example encoded planes are as below:

| Plane          |                            Feature                            |
| ------------ | :----------------------------------------------------------- |
|0         | the remaining cards |
|1         | the union of other players' cards |
|2-4         | the recent three actions |
|5         | the union of played cards |

## Action Abstraction

The size of the action space of Dou Dizhu is 33676. This number is too large for learning algorithms. Thus, we make abstractions to the original action space and obtain 309 actions. We note that some recent studies also use similar abstraction techniques. The main idea of the abstraction is to make the kicker fuzzy and only focus on the major part of the combination. For example, "33345" is abstracted as '333**'. Users can also encode the actions for their own purposes by modifying `decode_action` function in [rlcard/envs/doudizhu.py](rlcard/envs/doudizhu.py). The detailed abstractions in the environment are as below:

| Type             | Number of Actions | Number of Actions after Abstraction | Action ID
| ---------------- | :---------------: | :---------------: | :---------------: | 
| Solo             |        15         |        15         | 0-14
| pair             |        13         |        13         | 15-27
| Trio             |        13         |        13         | 28-40
| Trio with single |        182        |        13         | 41-53
| Trio with pair   |        156        |        13         | 54-66 
| Chain of solo  |       36       |        36         | 67-102
| Chain of pair  |       52        |        52         | 103-154
| Chain of trio    |        45         |        45         | 155-199
| Plane with solo    |        24721         |        38         | 200-237
| Plane with pair    |        6552         |        30         | 238-267
| Quad with solo   |       1339        |        13         | 268-280
| Quad with pair   |       1014        |        13         | 281-293
| Bomb             |        13         |        13         | 294-306
| Rocket           |         1         |         1         | 307
| Pass             |         1         |         1         | 308
| Total            |       33676       |        309        |
