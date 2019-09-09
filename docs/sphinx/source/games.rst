Games in RLCard
===============

Blackjack
~~~~~~~~~

Blackjack is a
globally popular banking game known as Twenty-One. The objective is
to beat the dealer by reaching a higher score than the dealer without
exceeding 21. In the toolkit, we implement a simple version of
Blackjack. In each round, the player only has two options: "hit"
which will take a card, and 'stand' which end the turn. The player
will "bust" if his hands exceed 21 points. 
   
State Encoding In this
----------------------

toy environment, we encode the state as an array
``[player_score, dealer_score]`` where ``player_score`` is the score
currently obtained by the player, and the ``dealer_score`` is derived
from the card that faces up from the dealer. 

Action Encoding 
---------------

There are two actions in the simple Blackjack. They are encoded as follows:

+-------------+----------+
| Action ID   | Action   |
+=============+==========+
| 0           | hit      |
+-------------+----------+
| 1           | stand    |
+-------------+----------+

Limit Texas Hold'em
~~~~~~~~~~~~~~~~~~~

test 

No-limit Texas Hold'em
~~~~~~~~~~~~~~~~~~~~~~

test 

Dou Dizhu
~~~~~~~~~

test