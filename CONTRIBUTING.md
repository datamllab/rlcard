# Contibuting Guide
Contribution to this project is greatly appreciated! If you find any bugs or have any feedback, please create an issue or send a pull request to fix the bug. If you want to contribute codes for new features, please contact [daochen.zha@tamu.edu](mailto:daochen.zha@tamu.edu) or [khlai@tamu.edu](mailto:khlai@tamu.edu). We currently have several plans. Please create an issue or contact us through emails if you have other suggestions.

## Roadmaps

*   **Game Specific Configurations.** Now we plan to gradually support game specific configurations. Currently we only support specifying the number of players in Blackjack
*   **Rule-based Agent and Pre-trained Models.** Provide more rule-based agents and pre-trained models to benchmark the evaluation. We currently have several models in `/models`.
*   **More Games and Algorithms.** Develop more games and algorithms.
*   **Hyperparameter Search** Search hyperparameters for each environment and update the best one in the example.

## How to Create a Pull Request

If this your first time to contribute to a project, kindly follow the following instructions. You may find [Creating a pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request) helpful. Mainly, you need to take the following steps to send a pull request:

*   Click **Fork** in the upper-right corner of the project main page to create a new branch in your local Github.
*   Clone the repo from your local repo in your Github.
*   Make changes in your computer.
*   Commit and push your local changes to your local repo.
*   Send a pull request to merge your local branch to the branches in RLCard project.

## Testing Your Code

We strongly encourage you to write the testing code in parallel with your development. We use `unittest` in RLCard. An example is [Blackjack environment testing](tests/envs/test_blackjack_env.py).

## Making Configurable Environments
We take Blackjack as an Example to show how we can define game specific configurations in RLCard. The key points are highlighted as follows:

*   We add a `DEFAULT_GAME_CONFIG` in [Blackjack Env](rlcard/envs/blackjack.py) to define the default values of the game configurations. Each field should start with `game_`
*   Modify the game and environment according to the configurations. For example, we need to support multiple players in Blackjack.
*	Modify [Env](rlcard/envs/env.py) to add your game to the `supported_envs`
*   When making the environment, we pass the newly defined fields in `config`. For example, we pass `config={'game_player_num': 2}` for Blackjack.

