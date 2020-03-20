# Customizing Environments
In addition to the default state representation and action encoding, we also allow customizing an environment. In this document, we use Limit Texas Hold'em as an example to describe how to modify state representation, action encoding, reward calculation, or even the game rules.

## State Representation
To define our own state representation, we can modify the ``_extract_state`` function in [/rlcard/envs/limitholdem.py](../rlcard/envs/limitholdem.py#L33).

## Action Encoding
To define our own action encoding, we can modify the ``_decode_action`` function in [/rlcard/envs/limitholdem.py](../rlcard/envs/limitholdem.py#L75).

## Reward Calculation
To define our own reward calculation, we can modify the ``get_payoffs`` function in [/rlcard/envs/limitholdem.py](../rlcard/envs/limitholdem.py#L67).

## Modifying Game
We can change the parameters of a game to adjust its difficulty. For example, we can change the number of players, the number of allowed raises in Limit Texas Hold'em in the ``__init__`` function in [rlcard/games/limitholdem/game.py](../rlcard/games/limitholdem/game.py#L11).
