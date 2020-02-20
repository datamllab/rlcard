# Developping Algorithms
Although users may do whatever they like to design and try their algorithms. We recommend wrapping a new algorithm as an `Agent` class as the [example agents](../rlcard/agents). To be compatible with the toolkit, the agent should have the following functions and attribute:
*   `step`: Given the current state, predict the next action.
*   `eval_step`: Similar to `step`, but for evaluation purpose. Reinforcement learning algorithms will usually add some noise for better exploration in training. In evaluation, no noise will be added to make predictions.
*   `use_raw`: A boolean attribute. `True` if the agent uses raw states to do reasoning; `False` if the agent uses numerical values to play (such as neural networks).
