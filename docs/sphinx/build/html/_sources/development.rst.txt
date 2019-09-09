Development
===========

Developping Algorithms
~~~~~~~~~~~~~~~~~~~~~~

Although users may do whatever they like to design and try their
algorithms. We recommend wrapping a new algorithm as an ``Agent`` class
as the `example agents <rlcard/agents>`__. To be compatible with the
toolkit, the agent should have the following functions: 
 * ``step``: Given the current state, predict the next action. 
 * ``eval_step``: Similar to ``step``, but for evaluation purpose. Reinforcement learning algorithms will usually add some noise for better exploration in training. In evaluation, no noise will be added to make predictions.

Adding New Environments
~~~~~~~~~~~~~~~~~~~~~~~

To add a new environment to the toolkit, generally you should take the
following steps: 
 * **Implement a game.** Card games usually have similar structures so that they can be implemented with ``Game``, ``Round``, ``Dealer``, ``Judger``, ``Player`` as in existing games. The easiest way is to inherit the classed in `rlcard/core.py <rlcard/core.py>`__ and implement the functions. 
 * **Wrap the game with an environment.** The easiest way is to inherit ``Env`` in `rlcard/envs/env.py <rlcard/env/env.py>`__. You need to implement ``extract_state`` which encodes the state, ``decode_action`` which decode actions from the id to the text string, and ``get_payoffs`` which calculate payoffs of the players. 
 * **Register the game.** Now it is time to tell the toolkit where to locate the new environment. Go to `rlcard/envs/\ **init**.py <rlcard/envs/__init__.py>`__, and indicate the name of the game and its entry point.

To test whether the new environment is set up successfully:

.. code:: python

    import rlcard
    env.make(#the new evironment#)

