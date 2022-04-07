# Index

*   [Blackjack](games.md#blackjack)
*   [Leduc Hold'em](games.md#leduc-holdem)
*   [Limit Texas Hold'em](games.md#limit-texas-holdem)
*   [Dou Dizhu](games.md#dou-dizhu)
*   [Mahjong](games.md#mahjong)
*   [No-limit Texas Hold'em](games.md#no-limit-texas-holdem)
*   [UNO](games.md#uno)
*   [Gin Rummy](games.md#gin-rummy)
*   [Bridge](games.md#bridge)

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
introduced in [Bayes' Bluff: Opponent Modeling in Poker](http://poker.cs.ualberta.ca/publications/UAI05.pdf)). The deck consists only two pairs of King, Queen and Jack, six cards in total. Each game is fixed with two players, two rounds, two-bet maximum and raise amounts of 2 and 4 in the first and second round. In the first round, one player is randomly choosed to put 1 unit in pot as small blind while the other puts 2 unit as big blind, and each player is dealt one card, then starts betting. The player with small blind acts first. In the second round, one public card is revealed first, then the players bet again. Finally, the player whose hand has the same rank as the public card is the winner. If neither, then the one with higher rank wins. Other rules such as 'fold' can refer to Limit Texas hold'em.

### State Representation of Leduc Hold'em
The state is encoded as a vector of length 36. The first 3 elements correspond to hand card. The next 3 elements correspond to public card. The last 30 elements correspond the chips of the current player and the opponent (the chips could be in range 0~14) The correspondence between the index and the card is as below.

| Index   | Meaning                              |
| --------| :-----------------------------------:|
| 0~2     | J ~ K in hand                        |
| 3~5     | J ~ K as public card                 |
| 6~20    | 0 ~ 14 chips for the current player  |
| 21~35   | 0 ~ 14 chips for the opponent        |

### Action Encoding of Leduc Hold'em
The action encoding is the same as Limit Hold'em game.

### Payoff of Leduc Hold'em
The payoff is calculated similarly with Limit Hold'em game.

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
| seen\_cards   | Three face-down cards distributed to the landlord after bidding. Then these cards will be made public to all players.                                | TQA                                                                                                 |
| landlord      | An integer of landlord's id                                                                                                                          | 0                                                                                                   |
| self          | An integer of current player's id                                                                                                                    | 2                                                                                                   |
| trace         | A list of tuples which records every actions in one game. The first entry of  the tuple is player's id, the second is corresponding player's action. | \[(0, '8222'), (1, 'pass'), (2, 'pass'), (0 '6KKK'), (1, 'pass'), (2, 'pass'), (0, '8'), (1, 'Q')\] |
| played\_cards | As the game progresses, the cards which have been played by the three players and sorted from low to high.                                           | \['6', '8', '8', 'Q', 'K', 'K', 'K', '2', '2', '2'\]                                                |
| others\_hand  | The union of the other two player's current hand                                                                                                     | 333444555678899TTTJJJQQAA2R                                                                         |
| current\_hand | The current hand of current player                                                                                                                   | 3456677799TJQKAAB                                                                                   |
| actions       | The legal actions the current player could do                                                                                                        | \['pass', 'K', 'A', 'B'\]                                                                           |

### State Encoding of Dou Dizhu
Any given combination of cards, e.g., 55 or 3JJJ, is encoded as a 54-dimensional one-hot vector as follows. First, we construct a 4*15 matrix, where each column represents the rank (and two jokers), and each row represents the number of cards. We use one-hot encoding to construct such a matrix. Second, we remove the six entries that are always zero (i.e., the six entries in the columns of the jokers since there are only two jokers in the deck). Finally, we flatten the matrix, which leads to a 54-dimensional one-hot vector.
For the landlord, we encode the following features: current hand, the union of the others' hands, the most recent action, the most recent nine actions (9 is arbitrarily chosen), the union of all the cards played by the landlord up (i.e., the player acts before the landlord), the union of all the cards played by landlord down (i.e., the player acts after the landlord). We also use one-hot encoding to represent the number of cards left for the two peasants player.
For the peasant players, we similarly encode the following features: current hand, the union of the others' hands, the most recent action, the most recent nine actions, the union of all the cards played by the landlord, the union of all the cards played by the teammate, the most recent action performed by the landlord, the most recent action performed by the teammate. We also use one-hot encoding to represent the number of cards left for the other two players.

### Action Encoding of Dou Dizhu

The size of the action space of Dou Dizhu is 27472 summarized in the following table. In older version of RLCard, we abstract the action space. Specifically, we make abstractions to the original action space and obtain 309 actions. We note that some recent studies also use similar abstraction techniques. The main idea of the abstraction is to make the kicker fuzzy and only focus on the major part of the combination. For example, "33344" is abstracted as "333
\*\*".

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
| Plane with solo  |        21822      |        38                           | 200-237           |
| Plane with pair  |        2939       |        30                           | 238-267           |
| Quad with solo   |       1326        |        13                           | 268-280           |
| Quad with pair   |       858        |        13                           | 281-293           |
| Bomb             |        13         |        13                           | 294-306           |
| Rocket           |         1         |         1                           | 307               |
| Pass             |         1         |         1                           | 308               |
| Total            |       27472       |        309                          |                   |

In the new version of RLCard, we realize the actions do not need to be abstracted. Instead, we can extract action features and make the action feature as input. In this way, the agent can effectively reason about the large action space. Similar to the state encoding, each action is encodes into a 54 dimensional one-hot vector.

### Payoff
If the landlord first get rid of all the cards in his hand, he will win and receive a reward 1. The two peasants will lose and receive a reward 0. Similarly, if one of the peasant first get rid of all the cards in hand, both peasants will win and receive a reward 1. The landlord will lose and receive a reward 0.

## Mahjong
Mahjong is a tile-based game developed in China, and has spread throughout the world since 20th century. It is commonly played
by 4 players. The game is played with a set of 136 tiles. In turn players draw and discard tiles until  
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

| Index   | Meaning                            |
| ------- | :--------------------------------- |
| 0~12    | Spade A ~ Spade K                  |
| 13~25   | Heart A ~ Heart K                  |
| 26~38   | Diamond A ~ Diamond K              |
| 39~51   | Club A ~ Club K                    |
| 52      | Chips of player 1                  |
| 53      | Chips that all players have put in |

### Action Encoding of No-Limit Texas Hold'em
There are 103 actions in No-limit Texas Hold'em. They are encoded as below.

<small><sup>*</sup>Note: Starting from Action ID 3, the action means the amount player should put in the pot when chooses 'Raise'. The action ID from 3 to 5 corresponds to the bet amount from half amount of the pot, full amount of the pot to all in.</small>

| Action ID   |     Action         |
| ----------- | :----------------- |
| 0           | Fold               |
| 1           | Check              |
| 2           | Call               |
| 3           | Raise Half Pot     |
| 4           | Raise Full Pot     |
| 5           | All In             |

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

### State Encoding of Uno

In Uno environment, we encode the state into 4 feature planes. The size of each plane is 4*15. Row number 4 means four colors. Column number 15 means 10 number cards from 0 to 9 and 5 special cards—"Wild", "Wild Draw Four", "Skip", "Draw Two", and "Reverse". Each entry of a plane can be either 1 or 0. Note that the current encoding method is just an example to show how the feature can be encoded. The example encoded planes are as below:

| Plane | Feature                  |
| ----- | :----------------------- |
| 0-2   | hand                     |
| 3     | target                   |

We use 3 planes to represnt players' hand. Specifically, planes 0-2 represent 0 card, 1 card, 2 cards, respectively. Planes 4-6 are the same.

### Action Encoding of Uno

There are 61 actions in Uno. They are encoded as below. The detailed  mapping of action and its ID is in [rlcard/games/uno/jsondata/action_space.json](../rlcard/games/uno/jsondata/action_space.json):

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

## Gin Rummy
Gin Rummy is a popular two person card game using a regular 52 card deck (ace being low).
The dealer deals 11 cards to his opponent and 10 cards to himself.
Each player tries to form melds of 3+ cards of the same rank or 3+ cards of the same suit in sequence.
If the deadwood count of the non-melded cards is 10 or less, the player can knock.
If all cards can be melded, the player can gin.
Please refer to the details on [Wikipedia](https://en.wikipedia.org/wiki/Gin_rummy).

If a player knocks or gins, the hand ends, each player put down their melds, and their scores are determined.
If a player knocks, the opponent can layoff some of his deadwood cards if they extend melds of the knocker.
The score is the difference between the two deadwood counts of the players.
If the score is positive, the player going out receives it.
Otherwise, if the score is zero or negative, the opponent has undercut the player going out
and receives the value of the score plus a 25 point undercut bonus.

The non-dealer discards first (or knocks or gins if he can).
If the player has not knocked or ginned, the next player can pick up the discard or draw a card from the face down stockpile.
He can knock or gin and the hand ends.
Otherwise, he must discard and the next player continues in the same fashion.
If the stockpile is reduced to two cards only, then the hand is declared dead and no points are scored.

### State Representation of Gin Rummy 
The state representation of Gin Rummy is encoded as 5 feature planes, where each plane is of dimension 52.
For each plane, the column of the plane indicates the presence of the card (ordered from AS to KC).
The information that has been encoded can be referred as follows:

| Plane          |              Feature                                                         |
| :------------: | ---------------------------------------------------------------------------- |
| 0              | the cards in current player's hand                                           |
| 1              | the top card of the discard pile                                             |
| 2              | the dead cards: cards in discard pile (excluding the top card)               |
| 3              | opponent known cards: cards picked up from discard pile, but not discarded   |
| 4              | the unknown cards: cards in stockpile or in opponent hand (but not known)    |

### Action Space of Gin Rummy
There are 110 actions in Gin Rummy.

| Action ID     |     Action                 |
| :-----------: | -------------------------- |
| 0             | score_player_0_action      |
| 1             | score_player_1_action      |
| 2             | draw_card_action           |
| 3             | pick_up_discard_action     |
| 4             | declare_dead_hand_action   |
| 5             | gin_action                 |
| 6 - 57        | discard_action             |
| 58 - 109      | knock_action               |

### Payoff of Gin Rummy 
The reward is calculated by the terminal state of the game.
Note that the reward is different from that of the standard game.
A player who gins is awarded 1 point.
A player who knocks is awarded 0.2 points.
The losing player is punished by the negative of their deadwood count divided by 100.

If the hand is declared dead, both players are punished by the negative of their deadwood count divided by 100.

### Settings

The following options can be set.

| Option                                |    Default value          |
| ------------------------------------- | :-----------------------: |
| dealer_for_round                      | DealerForRound.Random     |
| stockpile_dead_card_count             | 2                         |
| going_out_deadwood_count              | 10                        |
| max_drawn_card_count                  | 52                        |
| max_move_count                        | 200                       |
| is_allowed_knock                      | True                      |
| is_allowed_gin                        | True                      |
| is_allowed_pick_up_discard            | True                      |
| is_allowed_to_discard_picked_up_card  | False                     |
| is_always_knock                       | False                     |
| is_south_never_knocks                 | False                     |

Note: max_move_count prevents an unlimited number of moves in a game.

### Variations

One can create variations that are easier to train
by changing the options and specifying different scoring methods.

## Bridge
Bridge is a popular four-person card game using a regular 52 card deck (ace being high).
The North and South players are partners against the partnership of the East and West players.
The dealer deals 13 cards to all four players.
There is a round of bidding to determine the contract for the amount of tricks to win by the declarer
with a specified trump suit (or no trump).
After the bidding concludes, 13 tricks are played to see if the contract is made.
During the trick playing, the dummy (the partner of the declarer) exposes his hand for all to see.
The declarer plays the cards from the dummy hand.

Please refer to the details on [Wikipedia](https://en.wikipedia.org/wiki/Contract_bridge).

I prefer the Chicago variation rather than Rubber Bridge.
Please refer to the details on [Pagat site](https://www.pagat.com/auctionwhist/bridge.html).

### State Representation of Bridge 
The state representation of Bridge is encoded as follows:

|   Key              | Size   |              Description                                                     |
| :------------:     | :---:  | ---------------------------------------------------------------------------- |
| hands_rep          | 4 * 52 | 1 if rep_index is card_id in hand and visible else 0 (for held card of player_id)                                         
| trick_rep          | 4 * 52 | 1 if rep_index is card_id in trick_pile else 0 (for trick card of player_id)                                    
| hidden_cards_rep   | 52     | 1 if rep_index is card_id of hidden card else 0 
| vul_rep            | 4      | 1 if rep_index is player_id of vulnerable player else 0
| dealer_rep         | 4      | 1 if rep_index is dealer_id else 0
| current_player_rep | 4      | 1 if rep_index is current_player_id else 0
| is_bidding_rep     | 1      | 1 if bidding else 0
| bidding_rep        | 40     | list of action_id of call actions in order (up to a max of 40)
| last_bid_rep       | 39     | 1 if rep_index is index of last call action else 0
| bid_amount_rep     | 8      | 1 if rep_index is bid_amount else 0
| trump_suit_rep     | 5      | 1 if rep_index is trump_suit_id else 0 (NT has id of 4)

Examples:
* vul_rep = [0 1 0 1] means E-W are vulnerable.
* dealer_rep = [0 0 0 1] means West is the dealer and bids first.
* current_player_rep = [0 0 1 0] means South is the current player.
* is_bidding_rep = [1] means the current player must make a call (bidding phase).
* bidding_rep = [0 0 0 36 13 36 34 0 0 0 ...] means West pass, North bids 3H, East pass, South bids 7S.
* last_bid_rep = [0 0 0 1 0 0 0 ...] means the last bid is 1H.
* bid_amount_rep = [0 0 0 0 1 0 0 0] means the bid amount is 4.
* trump_suit_rep = [0 0 0 1 0] means the trump suit is Spades.

### Action Space of Bridge
There are 91 actions in Bridge.

| Action ID     |     Action                 |
| :-----------: | -------------------------- |
| 0             | no_bid_action
| 1 - 35        | bid_action (bid amount by suit or NT)
| 36            | pass_action
| 37            | dbl_action
| 38            | rdbl_action
| 39 - 90       | play_card_action (card_id + 39)

Note: The no_bid_action is never presented as an option to a player.
It is used to allow the bidding_rep to always have North as the first bidder
(where no_bid_actions are taken until the dealer is reached, who then makes the first real call).

### Payoff of Bridge 
The payoff is calculated by the terminal state of the game.
Note that the payoff is different from that of the standard game.

The payoff for the defender side is the number of tricks taken by the defender side.

The payoff for the declarer side depends upon whether the bid amount of the contract is made or not.
If the contract is made (ignoring over tricks),
the payoff for the declarer side is the bid amount + 6 + a bonus for making the contract (defaults to 2).
If the contract is set, the payoff for the declarer side is the number of under tricks by the declarer side.

This payoff for the defender side encourages them to make as many tricks as possible.
Thus, the declarer side will be more likely to be set.

This payoff for the declarer side encourages them to bid as high as possible
and to choose the best trump suit or to pass when they have poor hands.
