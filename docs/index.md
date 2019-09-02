# Overview
The toolkit wraps each game by `Env` with easy-to-use interfaces. Users can focus on algorithm design instead of game development. The following design principles are applied:
* **Simple.** We make the interfaces straightforward and simple. Users can easily run one game and obtain the statistics of the game.
* **Consistent.** All the games are implemented following the same logical pattern. The main classes/functions of each game share the same class/function name. Users can easily understand each game and modify the rules for research purpose.
* **Reproducible.** Each environment can be seeded for reproducibility purpose.
* **Scalable.** New card environments can be added conveniently into RLCard with the above design principles.

# User Guide
* [Running examples](docs/running-examples.md)
* [RLCard high-level design](docs/high-level-design.md)
* [Developping algorithms](docs/developping-algorithms.md)
* [Evaluation](docs/evaluation.md)
* [Blackjack API](docs/blackjack-api.md)
* [Dou Dizhu API](docs/dou-dizhu-api.md)
* [Texas Hold'em API](docs/texas-holdem-api.md)

# Developer Guide
* [Code structure](docs/code-structure.md)
* [Adding new environments](docs/adding-new-environments.md)