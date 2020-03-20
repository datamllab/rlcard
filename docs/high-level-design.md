# RLCard High-level Design
This document introduces the high-level design for the environments, the games, and the agents (algorithms).

## Environments
We wrap each game with an `Env` class. The responsibility of `Env` is to help you generate trajectories of the games. For developing Reinforcement Learning (RL) algorithms, we recommend to use the following interfaces:

*   `set_agents`: This function tells the `Env` what agents will be used to perform actions in the game. Different games may have a different number of agents. The input of the function is a list of `Agent` class. For example, `env.set_agent([RandomAgent(action_num=env.action_num) for _ in range(2)])` indicates that two random agents will be used to generate the trajectories.
*   `run`: After setting the agents, this interface will run a complete trajectory of the game, calculate the reward for each transition, and reorganize the data so that it can be directly fed into a RL algorithm.

For advanced access to the environment, such as traversal of the game tree, we provide the following interfaces:

*   `step`: Given the current state, the environment takes one step forward, and returns the next state and the next player.
*   `step_back`: Takes one step backward. The environment will restore to the last state. The `step_back` is defaultly turned off since it requires expensively recoeding previous states. To turn it on, set `allow_step_back = True` when `make` environments.
*   `get_payoffs`: At the end of the game, this function can be called to obtain the payoffs for each player.

We also support single-agent mode and human mode. Examples can be found in [examples/](../examples).

*   Single agent mode: single-agent environments are developped by simulating other players with pre-trained models or rule-based models. You can enable single-agent mode by `rlcard.make(ENV_ID, config={'single_agent_mode':True})`. Then the `step` function will return `(next_state, reward, done)` just as common single-agent environments. `env.reset()` will reset the game and return the first state.

## Games
Card games usually have similar structures. We abstract some concepts in card games and follow the same design pattern. In this way, users/developers can easily dig into the code and change the rules for research purpose. Specifically, the following classes are used in all the games:

*   `Game`: A game is defined as a complete sequence starting from one of the non-terminal states to a terminal state. 
*   `Round`: A round is a part of the sequence of a game. Most card games can be naturally divided into multiple rounds.
*   `Dealer`: A dealer is responsible for shuffling and allocating a deck of cards.
*   `Judger`: A judger is responsible for making major decisions at the end of a round or a game.
*   `Player`: A player is a role who plays cards following a strategy.

To summarize, in one `Game`, a `Dealer` deals the cards for each `Player`. In each `Round` of the game, a `Judger` will make major decisions about the next round and the payoffs in the end of the game.

## Agents
We provide examples of several representative algorithms and wrap them as `Agent` to show how a learning algorithm can be connected to the toolkit. The first example is DQN which is a representative of the Reinforcement Learning (RL) algorithms category. The second example is NFSP which is a representative of the Reinforcement Learning (RL) with self-play. We also provide CFR and DeepCFR which belong to Conterfactual Regret Minimization (CFR) category. Other algorithms from these three categories can be connected in similar ways.
