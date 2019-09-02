# RLCard High-level Design
This document introduces the high-level design for the environments, the games, and the agents (algorithms).

### Environments
We wrap each game with an `Env` class. The reponsibility of `Env` is to generate trajectories of games. The `Env` for each game has common interfaces:
* `set_agents`: This function tells the `Env` what agents will be used to perfrom actions in the game. Different games may have different number of agents. The input of the function is a list of `Agent` class. For example, `env.set_agent([RandomAgent(), RandomAgent()])` says two random agents will be used to generate the trajectories.
* `set_seed`: To enable reprocucibility of the results, this function seed everything including the game and the algorithm to ensure that the same result can be reproduced with the same seed. The input of this function is an `int`.
* `run`: This function will return a complete trajectories of the game **TODO: MULTIPROCESS**

### Games
Card games usually have similar structures. We abstract some concepts in card games and follow the same design pattern. In this way, users/developers can easily dig into the code and change the rules for research purpose. Specifically, the following classes are used in all the games:
* `Game`: A game is defined as a complete sequence starting from one of the non-terminal states to a terminal state. The key function is `step`, with the action taken by the current player as input, and the the ID and the obervation of the next_player as output.
* `Round`: A round is a part of the sequence of a game. Most card games can be naturally divided into multiple rounds.
* `Dealer`: A dealer is responsible for shuffling and allocating a deck of cards.
* `Judger`: A judger is responsible for making major decisions in the end of a round or a game.
* `Player`: A player is a role who plays cards following a strategy.

To summarize, in one `Game`, a `Dealer` deals the cards for each `Player`. In each `Round` of the game, a `Judger` will make major decisions about the next round and the the payoffs in the end of the game.

### Agents
An agent will wrap a user-defined algorithm and play the game. Card games are usually played in sequence, which means the action performed by the current player will lead to the observation of the next player. To make things easier, we introduce `Agent` into the environment. The environment then generates a complete trajectory of the game rather than taking one step at a time. The key function in `Agent` is `step` whose input is the current observation and the output is the action.