# Adding New Environments
To add a new environment to the toolkit, generally you should take the following steps:
*   **Implement a game.** Card games usually have similar structures so that they can be implemented with `Game`, `Round`, `Dealer`, `Judger`, `Player`, as in existing games. The easiest way is to inherit the classed in [rlcard/core.py](../rlcard/core.py) and implement the functions.
*   **Wrap the game with an environment.** The easiest way is to inherit `Env` in [rlcard/envs/env.py](../rlcard/env/env.py). You need to implement `_extract_state` which encodes the state, `_decode_action` which decodes actions from the id to the text string, and `get_payoffs` which calculates payoffs of the players.
*   **Register the game.** Now it is time to tell the toolkit where to locate the new environment. Go to [rlcard/envs/\_\_init\_\_.py](../rlcard/envs/__init__.py), and indicate the name of the game and its entry point.

To test whether the new environment is set up successfully:
```python
import rlcard
rlcard.make(#the new evironment#)
```
