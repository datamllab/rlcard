# Index

*   [Blackjack](games.md#blackjack)
*   [Leduc Hold'em](games.md#leduc-holdem)
*   [Limit Texas Hold'em](games.md#limit-texas-holdem)
*   [Dou Dizhu](games.md#dou-dizhu)
*   [Mahjong](games.md#mahjong)
*   [No-limit Texas Hold'em](games.md#no-limit-texas-holdem)
*   [UNO](games.md#uno)
*   [Sheng Ji](games.md#sheng-ji)
 
## Blackjack
Blackjack is a globally popular banking game known as Twenty-One. The objective is to beat the dealer by reaching a higher score than the dealer without exceeding 21. In the toolkit, we implement a simple version of Blackjack. In each round, the player only has two options: "hit" which will take a card, and 'stand' which end the turn. The player will "bust" if his hands exceed 21 points. After the player completes his hands (chooses "stand" and has not busted), the dealer then reals his hidden card and "hit" until obtaining at least 17 points.
### State Representation of Blackjack
In this toy environment, we encode the state as an array `[player_score, dealer_score]` where `player_score` is the score currently obtained by the player, and the `dealer_score` is derived from the card that faces up from the dealer.
### Action Encoding of Blackjack
There are two actions in the simple Blackjack. They are encoded as follows:

| Action ID  | Action  |
| -----------| :------ |
| 0          | hit     |
| 1          | stand   |

### Payoff of Blackjack
The player may receive a reward -1 (lose), 0 (tie), or 1 (win) in the end of the game.

## Leduc Hold'em
Leduc Hold'em is a smaller version of Limit Texas Hold'em (first
introduced in [Bayes' Bluff: Opponent Modeling in Poker](http://poker.cs.ualberta.ca/publications/UAI05.pdf)). The deck consists only two pairs of King, Queen and Jack, six cards in total. Each game is fixed with two players, two rounds, two-bet maximum and raise amounts of 2 and 4 in the first and second round. In the first round, each player puts 1 unit in the pot and is dealt one card, then starts betting. In the second round, one public card is revealed first, then the players bet again. Finally, the player whose hand has the same rank as the public card is the winner. If neither, then the one with higher rank wins. Other rules such as 'fold' can refer to Limit Texas hold'em.

### State Representation of Leduc Hold'em
Similar to the Limit Hold'em game. The state is encoded as a vector of length 6 with each element corresponding to one card. The state contains player's hand and public card (if it has been dealt). The correspondence between the index and the card is as below.

| Index   | Card                  |
| --------| :--------------------:|
| 0~2     | Spade J ~ Spade K     |
| 3~6     | Heart J ~ Heart K     |

### Action Encoding of Leduc Hold'em
The action encoding is the same as Limit Hold'em game.

### Payoff of Leduc Hold'em
The payoff is calculated similarly with Limit Hold'em game. The only difference is that Leduc Hold'em does not has the 'big blind' concept. As both players start the first round with 1 unit in the pot, we treat the 'big blind' in calculation as 1 by default.

## Limit Texas Hold'em
Texas Hold'em is a popular betting game. Each player is dealt two face-down cards, called hole cards. Then 5 community cards are dealt in three stages (the flop, the turn and the river). Each player seeks the five best cards among the hole cards and community cards. There are 4 betting rounds. During each round each player can choose "call", "check", "raise", or "fold".

In fixed limit Texas Hold'em. Each player can only choose a fixed amount of raise. And in each round the number of raises is limited to 4.

### State Representation of Limit Texas Hold'em
The state is encoded as a vector of length 72. The first 52 elements represent cards, where each element corresponds to one card. The hand is represented as the two hole cards plus the observed community cards so far. The last 20 elements are the betting history. The correspondence between the index and the card is as below.

| Index   | Meaning                 |
| ------- | :----------------------:|
| 0~12    | Spade A ~ Spade K       |
| 13~25   | Heart A ~ Heart K       |
| 26~38   | Diamond A ~ Diamond K   |
| 39~51   | Club A ~ Club K         |
| 52~56   | Raise number in round 1 |
| 37~61   | Raise number in round 2 |
| 62~66   | Raise number in round 3 |
| 67~71   | Raise number in round 4 |

### Action Encoding of Limit Texas Hold'em
There 4 actions in Limit Texas Hold'em. They are encoded as below.

| Action ID   |     Action    |
| ----------- | :------------ |
| 0           | Call          |
| 1           | Raise         |
| 2           | Fold          |
| 3           | Check         |

### Payoff of Limit Texas Hold'em
The stardard unit used in the leterature is milli big blinds per hand (mbb/h). In the toolkit, the reward is calculated based on big blinds per hand. For example, a reward of 0.5 (-0.5) means that the player wins (loses) 0.5 times of the amount of big blind.

## Dou Dizhu

Doudizhu is one of the most popular Chinese card games with hundreds of millions of players. It is played by three people with one pack of 54 cards including a red joker and a black joker. After bidding, one player would be the "landlord" who can get an extra three cards, and the other two would be "peasants" who work together to fight against the landlord. In each round of the game, the starting player must play a card or a combination, and the other two players can decide whether to follow or "pass." A round is finished if two consecutive players choose "pass." The player who played the cards with the highest rank will be the first to play in the next round. The objective of the game is to be the first player to get rid of all the cards in hand. For detailed rules, please refer to [Wikipedia](https://en.wikipedia.org/wiki/Dou_dizhu) or  [Baike](https://baike.baidu.com/item/%E6%96%97%E5%9C%B0%E4%B8%BB/177997?fr=aladdin).

In the toolkit, we implement a standard version of Doudizhu. In the bidding phase, we heuristically designate one of the players as the "landlord." Specifically, we count the number of key cards or combinations (high-rank cards and bombs), and the player with the most powerful hand is chosen as "lanlord."

### State Representation of Dou Dizhu
At each decision point of the game, the corresponding player will be able to observe the current state (or information set in imperfect information game). The state consists of all the information that the player can observe from his view. We encode the information into a readable Python dictionary. The following table shows the structure of the state:

| Key           | Description                                                                                                                                          | Example value                                                                                       |
| ------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| deck          | A string of one pack of 54 cards with Black Joker and Red Joker. Each character means a card. For conciseness, we use 'T' for '10'.                  | 3333444455556666<br/>777788889999TTTTJJJJ<br/>QQQQKKKKAAAA2222BR                                    |
| seen\_cards   | Three face-down cards distributed to the landlord after bidding. Then these cards will be made public to all players.                                | TQA                                                                                                 |
| landlord      | An integer of landlord's id                                                                                                                          | 0                                                                                                   |
| self          | An integer of current player's id                                                                                                                    | 2                                                                                                   |
| initial\_hand | All cards current player initially owned when a game starts. It will not change with playing cards.                                                  | 3456677799TJQKAAB                                                                                   |
| trace         | A list of tuples which records every actions in one game. The first entry of  the tuple is player's id, the second is corresponding player's action. | \[(0, '8222'), (1, 'pass'), (2, 'pass'), (0 '6KKK'), (1, 'pass'), (2, 'pass'), (0, '8'), (1, 'Q')\] |
| played\_cards | As the game progresses, the cards which have been played by the three players and sorted from low to high.                                           | \['6', '8', '8', 'Q', 'K', 'K', 'K', '2', '2', '2'\]                                                |
| others\_hand  | The union of the other two player's current hand                                                                                                     | 333444555678899TTTJJJQQAA2R                                                                         |
| current\_hand | The current hand of current player                                                                                                                   | 3456677799TJQKAAB                                                                                   |
| actions       | The legal actions the current player could do                                                                                                        | \['pass', 'K', 'A', 'B'\]                                                                           |

### State Encoding of Dou Dizhu
In Dou Dizhu environment, we encode the state into 6 feature planes. The size of each plane is 5*15. Each entry of a plane can be either 1 or 0. Note that the current encoding method is just an example to show how the feature can be encoded. Users are encouraged to encode the state for their own purposes by modifying `extract_state` function in [rlcard/envs/doudizhu.py](rlcard/envs/doudizhu.py). The example encoded planes are as below:

| Plane          |                            Feature       |
| -------------- | :--------------------------------------- |
| 0              | the current hand                         |
| 1              | the union of the other two players' hand |
| 2-4            | the recent three actions                 |
| 5              | the union of all played cards            |

### Action Abstraction of Dou Dizhu

The size of the action space of Dou Dizhu is 33676. This number is too large for learning algorithms. Thus, we make abstractions to the original action space and obtain 309 actions. We note that some recent studies also use similar abstraction techniques. The main idea of the abstraction is to make the kicker fuzzy and only focus on the major part of the combination. For example, "33345" is abstracted as "333
\*\*". When the predicted action of the agent is **not legal**, the agent will choose "**pass**.". Thus, the current environment is simple, since once the agent learns how to play legal actions, it can beat random agents. Users can also encode the actions for their own purposes (such as increasing the difficulty of the environment) by modifying `decode_action` function in [rlcard/envs/doudizhu.py](rlcard/envs/doudizhu.py). Users are also encouraged to include rule-based agents as opponents. The abstractions in the environment are as below. The detailed  mapping of action and its ID is in [rlcard/games/doudizhu/jsondata/action_space.json](rlcard/games/doudizhu/jsondata/action_space.json):

| Type             | Number of Actions | Number of Actions after Abstraction | Action ID         |
| ---------------- | :---------------: | :---------------------------------: | :---------------: | 
| Solo             |        15         |        15                           | 0-14              |
| pair             |        13         |        13                           | 15-27             |
| Trio             |        13         |        13                           | 28-40             |
| Trio with single |        182        |        13                           | 41-53             |
| Trio with pair   |        156        |        13                           | 54-66             |
| Chain of solo    |       36          |        36                           | 67-102            |
| Chain of pair    |       52          |        52                           | 103-154           |
| Chain of trio    |        45         |        45                           | 155-199           |
| Plane with solo  |        24721      |        38                           | 200-237           |
| Plane with pair  |        6552       |        30                           | 238-267           |
| Quad with solo   |       1339        |        13                           | 268-280           |
| Quad with pair   |       1014        |        13                           | 281-293           |
| Bomb             |        13         |        13                           | 294-306           |
| Rocket           |         1         |         1                           | 307               |
| Pass             |         1         |         1                           | 308               |
| Total            |       33676       |        309                          |                   |

### Payoff
Each player will receive a reward 0 (lose) or 1 (win) in the end of the game.

## Mahjong
Mahjong is a tile-based game developed in China, and has spread throughout the world since 20th century. It is commonly played
but 4 players. The game is played with a set of 136 tiles. In turn players draw and discard tiles until  
The goal of the game is to complete the leagal hand using the 14th drawn tile to form 4 sets and a pair. 
We revised the game into a simple version that all of the winning set are equal, and player will win as long as she complete 
forming 4 sets and a pair. Please refer the detail on [Wikipedia](https://en.wikipedia.org/wiki/Mahjong) or  [Baike](https://baike.baidu.com/item/麻将/215).

### State Representation of Mahjong 
The state representation of Mahjong is encoded as 6 feature planes, where each plane has 34 X 4 dimensions.
For each plane, the column of the plane indicates the number of the cards in the given cards set, and the
row of the plane represents each kind of cards (Please refer to the action space table). The information that
has been encoded can be refered as follows:

| Plane          |                            Feature       |
| -------------- | :--------------------------------------- |
| 0              | the cards in current player's hand       |
| 1              | the played cards on the table            |
| 2-5            | the public piles of each players         |

### Action Space of Mahjong
There are 38 actions in Mahjong.

| Action ID   |     Action                  |
| ----------- | :-------------------------: |
| 0 ~ 8       | Bamboo-1 ~ Bamboo-9         |
| 9 ~ 17      | Characters-1 ~ Character-9  |
| 18 ~ 26     | Dots-1 ~ Dots-9             |
| 27          | Dragons-green               |
| 28          | Dragons-red                 |
| 29          | Dragons-white               |
| 30          | Winds-east                  |
| 31          | Winds-west                  |
| 32          | Winds-north                 |
| 33          | Winds-south                 |
| 34          | Pong                        |
| 35          | Chow                        |
| 36          | Gong                        |
| 37          | Stand                       |

### Payoff of Mahjong 
The reward is calculated by the terminal state of the game, where winning player is awarded as 1, losing players are punished as -1.
And if no one win the game, then all players' reward will be 0.

## No-limit Texas Hold'em
No-limit Texas Hold'em has similar rule with Limit Texas Hold'em. But unlike in Limit Texas Hold'em game in which each player can only choose a fixed amount of raise and the number of raises is limited. In No-limit Texas Hold'em, The player may raise with at least the same amount as previous raised amount in the same round (or the minimum raise amount set before the game if none has raised), and up to the player's remaining stack. The number of raises is also unlimited.

## State Representation of No-Limit Texas Hold'em
The state representation is similar to Limit Hold'em game. The state is represented as 52 cards and 2 elements of the chips of the players as below:

| Index   | Meaning                 |
| ------- | :---------------------- |
| 0~12    | Spade A ~ Spade K       |
| 13~25   | Heart A ~ Heart K       |
| 26~38   | Diamond A ~ Diamond K   |
| 39~51   | Club A ~ Club K         |
| 52      | Chips of player 1       |
| 53      | Chips of player 2       |

### Action Encoding of No-Limit Texas Hold'em
There are 103 actions in No-limit Texas Hold'em. They are encoded as below.

<small><sup>\*</sup>Note: Starting from Action ID 3, the action means the amount player should put in the pot when chooses 'Raise'. The action ID from 3 to 102 corresponds to the bet amount from 1 to 100.<small>

| Action ID   |     Action         |
| ----------- | :----------------- |
| 0           | Call               |
| 1           | Fold               |
| 2           | Check              |
| 3 ~ 102     | <sup>\*</sup>Raise |

### Payoff of No-Limit Texas Hold'em
The reward is calculated based on big blinds per hand. For example, a reward of 0.5 (-0.5) means that the player wins (loses) 0.5 times of the amount of big blind.

## UNO

Uno is an American shedding-type card game that is played with a specially deck.The game is for 2-10 players. Every player starts with seven cards, and they are dealt face down. The rest of the cards are placed in a Draw Pile face down. Next to the pile a space should be designated for a Discard Pile. The top card should be placed in the Discard Pile, and the game begins. The first player is normally the player to the left of the dealer and gameplay usually follows a clockwise direction. Every player views his/her cards and tries to match the card in the Discard pile. Players have to match either by the number, color, or the symbol/action. If the player has no matches, they must draw a card. If that card can be played, play it. Otherwise, keep the card. The objective of the game is to be the first player to get rid of all the cards in hand. For detailed rules, please refer to [Wikipedia](https://en.wikipedia.org/wiki/Uno_(card_game)) or [Uno Rules](https://www.unorules.com/). And in our toolkit, the number of players is 2.

### State Representation of Uno

In state representation, each card is represented as a string of color and trait(number, symbol/action). 'r', 'b', 'y', 'g' represent red, blue, yellow and green respectively. And at each decision point of the game, the corresponding player will be able to observe the current state (or information set in imperfect information game). The state consists of all the information that the player can observe from his view. We encode the information into a readable Python dictionary. The following table shows the structure of the state:

| Key          | Description                                                             | Example value                                                          |
| ------------ | :---------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| hand         | A list of  the player's current hand.                                   | \['g-wild', 'b-0', 'g-draw_2', 'y-skip', 'r-draw_2', 'y-3', 'y-wild'\] |
| target       | The top card in the Discard pile                                        | 'g-wild'                                                               |
| played_cards | As the game progresses, the cards which have been played by the players | \['g-3', 'g-wild'\]                                                    |
| others_hand  | The union of the other player's current hand                            | \['b-0', 'g-draw_2', 'y-skip', 'r-draw_2', 'y-3', 'r-wild'\]           |

### State Encoding of Uno

In Uno environment, we encode the state into 7 feature planes. The size of each plane is 4*15. Each entry of a plane can be either 1 or 0. Note that the current encoding method is just an example to show how the feature can be encoded. Users are encouraged to encode the state for their own purposes by modifying `extract_state` function in [rlcard/envs/uno.py](rlcard/envs/uno.py). The example encoded planes are as below:

| Plane | Feature                  |
| ----- | :----------------------- |
| 0-2   | hand                     |
| 3     | target                   |
| 4-6   | the recent three actions |

### Action Encoding of Uno

There are 61 actions in Uno. They are encoded as below. The detailed  mapping of action and its ID is in [rlcard/games/uno/jsondata/action_space.json](rlcard/games/uno/jsondata/action_space.json):

| Action ID |                   Action                   |
| --------- | :----------------------------------------: |
| 0~9       |        Red number cards from 0 to 9        |
| 10~12     |  Red action cards: skip, reverse, draw 2   |
| 13        |               Red wild card                |
| 14        |          Red wild and draw 4 card          |
| 15~24     |       green number cards from 0 to 9       |
| 25~27     | green action cards: skip, reverse, draw 2  |
| 28        |              green wild card               |
| 29        |         green wild and draw 4 card         |
| 30~39     |       blue number cards from 0 to 9        |
| 40~42     |  blue action cards: skip, reverse, draw 2  |
| 43        |               blue wild card               |
| 44        |         blue wild and draw 4 card          |
| 45~54     |      yellow number cards from 0 to 9       |
| 55~57     | yellow action cards: skip, reverse, draw 2 |
| 58        |              yellow wild card              |
| 59        |        yellow wild and draw 4 card         |
| 60        |                    draw                    |

### Payoff of Uno

Each player will receive a reward -1 (lose) or 1 (win) in the end of the game.

## Sheng Ji
(Under construction)
