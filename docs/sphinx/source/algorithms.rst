Algorithms
==========

Deep-Q Learning
~~~~~~~~~~~~~~~

Deep-Q Learning (DQN) is a basic reinforcement learning (RL) algorithm. We wrap DQN
as an example to show how RL algorithms can be connected to the
environments. In the DQN agent, the following classes are
implemented:
 * ``DQNAgent``: The agent class that interacts with the environment.
 * ``Normalizer``: The responsibility of this class is to keep a running
   mean and std. The Normalizer will first preprocess the state before
   feeding the state into the model.
 * ``Memory``: A memory buffer that manages the storing and sampling of
   transitions.
 * ``Estimator``: The neural network that is used to make predictions.

DeepCFR
~~~~~~~

test

