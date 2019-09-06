# Toy Examples
In this document, we provide some toy examples for getting started. For more examples, please refer to [examples/](examples).

# Playing with Random Agents
We have set up a random agent thats can play randomly on each environment. An example of applying a random agent on Blackjack is as follow:
```python
import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import *

# Make environment
env = rlcard.make('blackjack')
episode_num = 2

# Set global seed to 0
set_global_seed(1)

# Set up agents
agent_0 = RandomAgent(action_size=env.action_num)
env.set_agents([agent_0])

for episode in range(episode_num):

    # Generate data from the environment
    trajectories, _ = env.run(is_training=False)

    # Print out the trajectories
    print('\nEpisode {}'.format(episode))
    for ts in trajectories[0]:
        print('State: {}, Action: {}, Reward: {}, Next State, {}, Done: {}'.format(ts[0], ts[1], ts[2], ts[3], ts[4])) 
```
The expected output should look like something as follows:
** TODO: debug blackjack **
```
Episode 0
State: [20, 3], Action: 1, Reward: 1, Next State: [20, 7], Done: True

Episode 1
State: [17, 10], Action: 1, Reward: 0, Next State: [17, 12], Done: True
```
Note that the states and actions are wrapped by `env` in Blackjack. In this example, the `[20,3]` suggests the current player obtains score 20 while the card that faces up in dealer's hand has score 5. Reward 1 suggests the player wins this game.

# Deep-Q Learning on Blackjack
The second example is to use Deep-Q learning to train an agent on Blackjack. We aim to use this example to show how reinforcement learning algorithms can be developped and applied in our toolkit. The example is shown below:
```python
import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.utils.utils import *
import tensorflow as tf

# Make environment
env = rlcard.make('blackjack')

# Set the iterations numbers and how frequently we evaluate
evaluate_every = 100
evaluate_num = 1000
episode_num = 1000000

# Set a gloabel seed
set_global_seed(1)

with tf.Session() as sess:
    # Set agents
    agent_0 = DQNAgent(sess, action_size=env.action_num)
    env.set_agents([agent_0])

    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent and update the agent
        for ts in trajectories[0]:
            is_training = agent_0.feed(ts)

        if is_training and (episode) % evaluate_every == 0:
            reward = 0
            for eval_episode in range(evaluate_num):
                _, payoffs = env.run()
                reward += payoffs[0]

            print('INFO - Average reward is {}'.format(float(reward)/evaluate_num))
```
The expected output is something like below:
```python
INFO - Populating replay memory...

INFO - Step 0 loss: 0.9071584939956665
INFO - Copied model parameters to target network.
INFO - Step 98 loss: 0.6962372660636902INFO - Average reward is -0.468
INFO - Step 242 loss: 0.5883776545524597INFO - Average reward is -0.446
INFO - Step 389 loss: 0.6218322515487671INFO - Average reward is -0.133
INFO - Step 517 loss: 0.4988301992416382INFO - Average reward is -0.146
INFO - Step 631 loss: 0.6635352373123169INFO - Average reward is -0.192
INFO - Step 748 loss: 0.5455094575881958INFO - Average reward is -0.15
INFO - Step 860 loss: 0.6445329785346985INFO - Average reward is -0.204
INFO - Step 973 loss: 0.5738863348960876INFO - Average reward is -0.113
```
In Blackjack, the player will get a payoff in the end of the game: 1 if the player wins, -1 if the player loses, and 0 if it is a tie. The performance is measured by the average payoff the player obtains by playing 1000 episodes. The above example shows that the agent achieves better and better performance during training.

# DeepCFR on Blackjack
test

