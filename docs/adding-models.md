# Adding Pre-trained/Rule-based models
You can add your own pre-trained/rule-based models to the toolkit by following several steps:

*   **Develop models.** You can either design a rule-based model or save a neural network model. For each game, you need to develop agents for all the players at the same time. You need to wrap each agent as a `Agent` class and make sure that `step`, `eval_step` and `use_raw` can work correctly.
*   **Wrap models.** You need to inherit the `Model` class in `rlcard/models/model.py`. Then put all the agents into a list. Rewrite `agent` property to return this list.
*   **Register the model.** Register the model in `rlcard/models/__init__.py`.
*   **Load the model in environment.** An example of loading `leduc-holdem-nfsp` model is as follows:
```python
from rlcard import models
leduc_nfsp_model = models.load('leduc-holdem-nfsp')
```
Then use `leduc_nfsp_model.agents` to obtain all the agents for the game.
