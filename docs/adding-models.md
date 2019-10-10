# Adding Pre-trained/Rule-based models
You can add your own pre-trained/rule-based models to the toolkit by following several steps:

*   **Develop models.** You can either design a rule-based model save a neural network model. For each game, you need to develop models for all the players at the same time. You need to wrap each model as a class and make sure that `step` and `eval_step` can work correctly.
*   **Wrap models.** You need to inherit the `Model` class in `rlcard/models.model.py`. Then put all the models for the players into a list. Rewrite `get_agent` function and return this list.
*   **Register the model.** Register the model in `rlcard/models/__init__.py`.
*   **Load the model in environment.** To load the model, modify `load_pretrained_models` in the corresponding game environment in `rlcard/envs`. Use the resgistered name to load the model.
