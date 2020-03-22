# Gin Rummy Guidelines
## Gin Rummy
Gin Rummy is a popular two person card game using a regular 52 card deck (ace being low).
The dealer deals 11 cards to his opponent and 10 cards to himself.
Each player tries to form melds of 3+ cards of the same rank or 3+ cards of the same suit in sequence.
If the deadwood count of the non-melded cards is 10 or less, the player can knock.
If all cards can be melded, the player can gin.
Please refer the detail on [Wikipedia](https://en.wikipedia.org/wiki/Gin_rummy).

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
The losing player is punished by the negative of their deadwood count.

If the hand is declared dead, both players are punished by the negative of their deadwood count.

### Settings

The following options can be set.

| Option                                |    Default value          |
| ------------------------------------- | :-----------------------: |
| dealer_for_round                      | DealerForRound.Random     |
| stockpile_dead_card_count             | 2                         |
| going_out_deadwood_count              | 10                        |
| max_drawn_card_count                  | 52                        |
| is_allowed_knock                      | True                      |
| is_allowed_gin                        | True                      |
| is_allowed_pick_up_discard            | True                      |
| is_allowed_to_discard_picked_up_card  | False                     |
| is_always_knock                       | False                     |
| is_south_never_knocks                 | False                     |

### Variations

One can create variations that are easier to train
by changing the options and specifying different scoring methods.
