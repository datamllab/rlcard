Overview
========

The toolkit wraps each game by ``Env`` with easy-to-use interfaces. The
goal of this toolkit is to enable the users to focus on algorithm design
on challenging card games instead of developping game engines. The
following design principles are applied: \* **Simple.** We make the
interfaces straightforward and simple. Users can easily run one game and
obtain the statistics of the game. \* **Consistent.** All the games are
implemented following the same logical pattern. The main
classes/functions of each game share the same class/function name. Users
can easily understand each game and modify the rules for research
purpose. \* **Reproducible.** The results can be seeded for
reproducibility purpose. \* **Minimum Dependency.** We minimize the
dependencies used in the toolkit so that the codes are easy to modify or
migrate. \* **Scalable.** New card environments can be added
conveniently into RLCard with the above design principles.

User Guide
==========

-  `Toy examples <toy-examples.md>`__
-  `RLCard high-level design <high-level-design.md>`__
-  `Games in RLCard <games.md>`__
-  `Algorithms in RLCard <algorithms.md>`__
-  `Developping new algorithms <developping-algorithms.md>`__

Developer Guide
===============

-  `Adding new environments <adding-new-environments.md>`__

Application Programming Interface (API)
=======================================

The API documents are and available in `github
page <https://rlcard.github.io/index.html>`__.
