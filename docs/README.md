# Documents of RLCard

## Overview
The toolkit wraps each game by `Env` class with easy-to-use interfaces. The goal of this toolkit is to enable the users to focus on algorithm development without caring about the environment. The following design principles are applied when developing the toolkit:
*   **Reproducible.** Results on the environments can be reproduced. The same result should be obtained with the same random seed in different runs.
*   **Accessible.** The experiences are collected and well organized after each game with easy-to-use interfaces. Uses can conveniently configure state representation, action encoding, reward design, or even the game rules.
*   **Scalable.** New card environments can be added conveniently into the toolkit with the above design principles. We also try to minimize the dependencies in the toolkit so that the codes can be easily maintained.

## User Guide

*   [Toy examples](toy-examples.md)
*   [RLCard high-level design](high-level-design.md)
*   [Games in RLCard](games.md)
*   [Algorithms in RLCard](algorithms.md)

## Developer Guide

*   [Developping new algorithms](developping-algorithms.md)
*   [Adding new environments](adding-new-environments.md)
*   [Customizing environments](customizing-environments.md)
*   [Adding pre-trained/rule-based models](adding-models.md)

## Application Programming Interface (API)
The API documents are and available at [Official Website](http://www.rlcard.org).
