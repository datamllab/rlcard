# Toy Examples
In this document, we provide some toy examples for getting started. For more examples, please refer to [examples/](examples).

# Playing with Random Agents
We have set up a random agent that can play randomly on each environment. An example of applying a random agent on Blackjack is as follow:
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
Note that the states and actions are wrapped by `env` in Blackjack. In this example, the `[20,3]` suggests the current player obtains score 20 while the card that faces up in the dealer's hand has score 5. Reward 1 suggests the player wins this game.

# Deep-Q Learning on Blackjack
The second example is to use Deep-Q learning to train an agent on Blackjack. We aim to use this example to show how reinforcement learning algorithms can be developed and applied in our toolkit. We design a `run` function which plays one complete game and provides the data for training RL agents. The example is shown below:
```python
import tensorflow as tf

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.utils.utils import *

# Make environment
env = rlcard.make('blackjack')

# Set the iterations numbers and how frequently we evaluate
evaluate_every = 100
evaluate_num = 1000
episode_num = 1000000

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 100
norm_step = 100

# Set a global seed
set_global_seed(1)

with tf.Session() as sess:
    # Set agents
    agent = DQNAgent(sess,
                       action_size=env.action_num,
                       replay_memory_init_size=memory_init_size,
                       norm_step=norm_step)
    env.set_agents([agent])

    # Count the number of steps
    step_counter = 0

    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent and update the agent
        for ts in trajectories[0]:
            agent.feed(ts)
            step_counter += 1

        # Train the agent
        if step_counter > memory_init_size + norm_step:
            agent.train()

        # Evaluate the performance
        if episode % evaluate_every == 0:
            reward = 0
            for eval_episode in range(evaluate_num):
                _, payoffs = env.run(is_training=False)
                reward += payoffs[0]

            print('\n########## Evaluation ##########')
            print('Average reward is {}'.format(float(reward)/evaluate_num))
```
The expected output is something like below:
```python
########## Evaluation ##########
Average reward is -0.377

########## Evaluation ##########
Average reward is -0.401
INFO - Step 0 loss: 0.8321959972381592
INFO - Copied model parameters to target network.
INFO - Step 48 loss: 0.7280950546264648
########## Evaluation ##########
Average reward is -0.357
INFO - Step 148 loss: 0.7298157811164856
########## Evaluation ##########
Average reward is -0.271
INFO - Step 248 loss: 0.6217592954635624
########## Evaluation ##########
Average reward is -0.123
INFO - Step 348 loss: 0.73691260814666755
########## Evaluation ##########
Average reward is -0.09
INFO - Step 448 loss: 0.77759009599685675
########## Evaluation ##########
Average reward is -0.091
```
In Blackjack, the player will get a payoff at the end of the game: 1 if the player wins, -1 if the player loses, and 0 if it is a tie. The performance is measured by the average payoff the player obtains by playing 1000 episodes. The above example shows that the agent achieves better and better performance during training.

# DeepCFR on Blackjack
test

