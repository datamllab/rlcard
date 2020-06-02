# Toy Examples
In this document, we provide some toy examples for getting started. All the examples in this document and even more examples are available in [examples/](../examples).

*   [Playing with random agents](toy-examples.md#playing-with-random-agents)
*   [Deep-Q learning on Blackjack](toy-examples.md#deep-q-learning-on-blackjack)
*   [Training CFR on Leduc Hold'em](toy-examples.md#training-cfr-on-leduc-holdem)
*   [Having fun with pretrained Leduc model](toy-examples.md#having-fun-with-pretrained-leduc-model)
*   [Leduc Hold'em as single-agent environment](toy-examples.md#leduc-holdem-as-single-agent-environment)
*   [Running multiple processes](toy-examples.md#running-multiple-processes)

## Playing with Random Agents
We have set up a random agent that can play randomly on each environment. An example of applying a random agent on Blackjack is as follow:
```python
import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import set_global_seed

# Make environment
env = rlcard.make('blackjack', config={'seed': 0})
episode_num = 2

# Set a global seed
set_global_seed(0)

# Set up agents
agent_0 = RandomAgent(action_num=env.action_num)
env.set_agents([agent_0])

for episode in range(episode_num):

    # Generate data from the environment
    trajectories, _ = env.run(is_training=False)

    # Print out the trajectories
    print('\nEpisode {}'.format(episode))
    for ts in trajectories[0]:
        print('State: {}, Action: {}, Reward: {}, Next State: {}, Done: {}'.format(ts[0], ts[1], ts[2], ts[3], ts[4]))
```
The expected output should look like something as follows:

```
Episode 0
State: {'obs': array([20,  3]), 'legal_actions': [0, 1]}, Action: 0, Reward: 0, Next State: {'obs': array([15,  3]), 'legal_actions': [0, 1]}, Done: False
State: {'obs': array([15,  3]), 'legal_actions': [0, 1]}, Action: 1, Reward: -1, Next State: {'obs': array([15, 20]), 'legal_actions': [0, 1]}, Done: True

Episode 1
State: {'obs': array([15,  5]), 'legal_actions': [0, 1]}, Action: 1, Reward: 1, Next State: {'obs': array([15, 23]), 'legal_actions': [0, 1]}, Done: True
```

Note that the states and actions are wrapped by `env` in Blackjack. In this example, the `[20, 3]` suggests the current player obtains score 20 while the card that faces up in the dealer's hand has score 3. Action 0 means "hit" while action 1 means "stand". Reward 1 suggests the player wins while reward -1 suggests the dealer wins. Reward 0 suggests a tie. The above data can be directly fed into a RL algorithm for training.

## Deep-Q Learning on Blackjack
The second example is to use Deep-Q learning to train an agent on Blackjack. We aim to use this example to show how reinforcement learning algorithms can be developed and applied in our toolkit. We design a `run` function which plays one complete game and provides the data for training RL agents. The example is shown below:
```python
import tensorflow as tf
import os

import rlcard
from rlcard.agents import DQNAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

# Make environment
env = rlcard.make('blackjack', config={'seed': 0})
eval_env = rlcard.make('blackjack', config={'seed': 0})

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
evaluate_num = 10000
episode_num = 100000

# The intial memory size
memory_init_size = 100

# Train the agent every X steps
train_every = 1

# The paths for saving the logs and learning curves
log_dir = './experiments/blackjack_dqn_result/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:

    # Initialize a global step
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # Set up the agents
    agent = DQNAgent(sess,
                     scope='dqn',
                     action_num=env.action_num,
                     replay_memory_init_size=memory_init_size,
                     train_every=train_every,
                     state_shape=env.state_shape,
                     mlp_layers=[10,10])
    env.set_agents([agent])
    eval_env.set_agents([agent])

    # Initialize global variables
    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)

    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent
        for ts in trajectories[0]:
            agent.feed(ts)

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('DQN')
    
    # Save model
    save_dir = 'models/blackjack_dqn'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(save_dir, 'model'))
```
The expected output is something like below:

```
----------------------------------------
  timestep     |  1
  reward       |  -0.7342
----------------------------------------
INFO - Agent dqn, step 100, rl-loss: 1.0042707920074463
INFO - Copied model parameters to target network.
INFO - Agent dqn, step 136, rl-loss: 0.7888197302818298
----------------------------------------
  timestep     |  136
  reward       |  -0.1406
----------------------------------------
INFO - Agent dqn, step 278, rl-loss: 0.6946825981140137
----------------------------------------
  timestep     |  278
  reward       |  -0.1523
----------------------------------------
INFO - Agent dqn, step 412, rl-loss: 0.62268990278244025
----------------------------------------
  timestep     |  412
  reward       |  -0.088
----------------------------------------
INFO - Agent dqn, step 544, rl-loss: 0.69050502777099616
----------------------------------------
  timestep     |  544
  reward       |  -0.08
----------------------------------------
INFO - Agent dqn, step 681, rl-loss: 0.61789089441299444
----------------------------------------
  timestep     |  681
  reward       |  -0.0793
----------------------------------------
```
In Blackjack, the player will get a payoff at the end of the game: 1 if the player wins, -1 if the player loses, and 0 if it is a tie. The performance is measured by the average payoff the player obtains by playing 10000 episodes. The above example shows that the agent achieves better and better performance during training. The logs and learning curves are saved in `./experiments/blackjack_dqn_result/`.

## Running Multiple Processes
The environments can be run with multiple processes to accelerate the training. Below is an example to train DQN on Blackjack with multiple processes.
```python
''' An example of learning a Deep-Q Agent on Blackjack with multiple processes
Note that we must use if __name__ == '__main__' for multiprocessing
'''

import tensorflow as tf
import os

import rlcard
from rlcard.agents import DQNAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

def main():
    # Make environment
    env = rlcard.make('blackjack', config={'seed': 0, 'env_num': 4})
    eval_env = rlcard.make('blackjack', config={'seed': 0, 'env_num': 4})

    # Set the iterations numbers and how frequently we evaluate performance
    evaluate_every = 100
    evaluate_num = 10000
    iteration_num = 100000

    # The intial memory size
    memory_init_size = 100

    # Train the agent every X steps
    train_every = 1

    # The paths for saving the logs and learning curves
    log_dir = './experiments/blackjack_dqn_result/'

    # Set a global seed
    set_global_seed(0)

    with tf.Session() as sess:

        # Initialize a global step
        global_step = tf.Variable(0, name='global_step', trainable=False)

        # Set up the agents
        agent = DQNAgent(sess,
                         scope='dqn',
                         action_num=env.action_num,
                         replay_memory_init_size=memory_init_size,
                         train_every=train_every,
                         state_shape=env.state_shape,
                         mlp_layers=[10,10])
        env.set_agents([agent])
        eval_env.set_agents([agent])

        # Initialize global variables
        sess.run(tf.global_variables_initializer())

        # Initialize a Logger to plot the learning curve
        logger = Logger(log_dir)

        for iteration in range(iteration_num):

            # Generate data from the environment
            trajectories, _ = env.run(is_training=True)

            # Feed transitions into agent memory, and train the agent
            for ts in trajectories[0]:
                agent.feed(ts)

            # Evaluate the performance. Play with random agents.
            if iteration % evaluate_every == 0:
                logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

        # Close files in the logger
        logger.close_files()

        # Plot the learning curve
        logger.plot('DQN')
        
        # Save model
        save_dir = 'models/blackjack_dqn'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        saver = tf.train.Saver()
        saver.save(sess, os.path.join(save_dir, 'model'))

if __name__ == '__main__':
    main()
```
Example output is as follow:

```
----------------------------------------
  timestep     |  17
  reward       |  -0.7378
----------------------------------------

INFO - Copied model parameters to target network.
INFO - Agent dqn, step 1100, rl-loss: 0.40940183401107797
INFO - Copied model parameters to target network.
INFO - Agent dqn, step 2100, rl-loss: 0.44971221685409546
INFO - Copied model parameters to target network.
INFO - Agent dqn, step 2225, rl-loss: 0.65466868877410897
----------------------------------------
  timestep     |  2225
  reward       |  -0.0658
----------------------------------------
INFO - Agent dqn, step 3100, rl-loss: 0.48663979768753053
INFO - Copied model parameters to target network.
INFO - Agent dqn, step 4100, rl-loss: 0.71293979883193974
INFO - Copied model parameters to target network.
INFO - Agent dqn, step 4440, rl-loss: 0.55871248245239263
----------------------------------------
  timestep     |  4440
  reward       |  -0.0736
----------------------------------------
```

## Training CFR on Leduc Hold'em
To show how we can use `step` and `step_back` to traverse the game tree, we provide an example of solving Leduc Hold'em with CFR:
```python
import numpy as np

import rlcard
from rlcard.agents import CFRAgent
from rlcard import models
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

# Make environment and enable human mode
env = rlcard.make('leduc-holdem', config={'seed': 0, 'allow_step_back':True})
eval_env = rlcard.make('leduc-holdem', config={'seed': 0})

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
save_plot_every = 1000
evaluate_num = 10000
episode_num = 10000

# The paths for saving the logs and learning curves
log_dir = './experiments/leduc_holdem_cfr_result/'

# Set a global seed
set_global_seed(0)

# Initilize CFR Agent
agent = CFRAgent(env)
agent.load()  # If we have saved model, we first load the model

# Evaluate CFR against pre-trained NFSP
eval_env.set_agents([agent, models.load('leduc-holdem-nfsp').agents[0]])

# Init a Logger to plot the learning curve
logger = Logger(log_dir)

for episode in range(episode_num):
    agent.train()
    print('\rIteration {}'.format(episode), end='')
    # Evaluate the performance. Play with NFSP agents.
    if episode % evaluate_every == 0:
        agent.save() # Save model
        logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

# Close files in the logger
logger.close_files()

# Plot the learning curve
logger.plot('CFR')
```
In the above example, the performance is measured by playing against a pre-trained NFSP model. The expected output is as below:
```
Iteration 0
----------------------------------------
  timestep     |  192
  reward       |  -1.3662
----------------------------------------
Iteration 100
----------------------------------------
  timestep     |  19392
  reward       |  0.9462
----------------------------------------
Iteration 200
----------------------------------------
  timestep     |  38592
  reward       |  0.8591
----------------------------------------
Iteration 300
----------------------------------------
  timestep     |  57792
  reward       |  0.7861
----------------------------------------
Iteration 400
----------------------------------------
  timestep     |  76992
  reward       |  0.7752
----------------------------------------
Iteration 500
----------------------------------------
  timestep     |  96192
  reward       |  0.7215
----------------------------------------
```
We observe that CFR achieves better performance as NFSP. However, CFR requires traversal of the game tree, which is infeasible in large environments.

## Having Fun with Pretrained Leduc Model
We have designed simple human interfaces to play against the pretrained model. Leduc Hold'em is a simplified version of Texas Hold'em. Rules can be found [here](games.md#leduc-holdem). Example of playing against Leduc Hold'em CFR model is as below:
```python
import rlcard
from rlcard import models
from rlcard.agents import LeducholdemHumanAgent as HumanAgent
from rlcard.utils import print_card

# Make environment
# Set 'record_action' to True because we need it to print results
env = rlcard.make('leduc-holdem', config={'record_action': True})
human_agent = HumanAgent(env.action_num)
cfr_agent = models.load('leduc-holdem-cfr').agents[0]
env.set_agents([human_agent, cfr_agent])

print(">> Leduc Hold'em pre-trained model")

while (True):
    print(">> Start a new game")

    trajectories, payoffs = env.run(is_training=False)
    # If the human does not take the final action, we need to
    # print other players action
    final_state = trajectories[0][-1][-2]
    action_record = final_state['action_record']
    state = final_state['raw_obs']
    _action_list = []
    for i in range(1, len(action_record)+1):
        if action_record[-i][0] == state['current_player']:
            break
        _action_list.insert(0, action_record[-i])
    for pair in _action_list:
        print('>> Player', pair[0], 'chooses', pair[1])

    # Let's take a look at what the agent card is
    print('===============     CFR Agent    ===============')
    print_card(env.get_perfect_information()['hand_cards'][1])

    print('===============     Result     ===============')
    if payoffs[0] > 0:
        print('You win {} chips!'.format(payoffs[0]))
    elif payoffs[0] == 0:
        print('It is a tie.')
    else:
        print('You lose {} chips!'.format(-payoffs[0]))
    print('')

    input("Press any key to continue...")
```
Example output is as follow:

```
>> Leduc Hold'em pre-trained model

>> Start a new game!
>> Agent 1 chooses raise

=============== Community Card ===============
┌─────────┐
│░░░░░░░░░│
│░░░░░░░░░│
│░░░░░░░░░│
│░░░░░░░░░│
│░░░░░░░░░│
│░░░░░░░░░│
│░░░░░░░░░│
└─────────┘
===============   Your Hand    ===============
┌─────────┐
│J        │
│         │
│         │
│    ♥    │
│         │
│         │
│        J│
└─────────┘
===============     Chips      ===============
Yours:   +
Agent 1: +++
=========== Actions You Can Choose ===========
0: call, 1: raise, 2: fold

>> You choose action (integer):
```
We also provide a running demo of a rule-based agent for UNO. Try it by running `examples/uno_human.py`.

## Leduc Hold'em as Single-Agent Environment
We have wrraped the environment as single agent environment by assuming that other players play with pre-trained models. The interfaces are exactly the same to OpenAI Gym. Thus, any single-agent algorithm can be connected to the environment. An example of Leduc Hold'em is as below:
```python
import tensorflow as tf
import os
import numpy as np

import rlcard
from rlcard.agents import DQNAgent
from rlcard.agents import RandomAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

# Make environment
env = rlcard.make('leduc-holdem', config={'seed': 0, 'single_agent_mode':True})
eval_env = rlcard.make('leduc-holdem', config={'seed': 0, 'single_agent_mode':True})

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 1000
evaluate_num = 10000
timesteps = 100000

# The intial memory size
memory_init_size = 1000

# Train the agent every X steps
train_every = 1

# The paths for saving the logs and learning curves
log_dir = './experiments/leduc_holdem_single_dqn_result/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:

    # Initialize a global step
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # Set up the agents
    agent = DQNAgent(sess,
                     scope='dqn',
                     action_num=env.action_num,
                     replay_memory_init_size=memory_init_size,
                     train_every=train_every,
                     state_shape=env.state_shape,
                     mlp_layers=[128,128])
    # Initialize global variables
    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)

    state = env.reset()

    for timestep in range(timesteps):
        action = agent.step(state)
        next_state, reward, done = env.step(action)
        ts = (state, action, reward, next_state, done)
        agent.feed(ts)

        if timestep % evaluate_every == 0:
            rewards = []
            state = eval_env.reset()
            for _ in range(evaluate_num):
                action, _ = agent.eval_step(state)
                _, reward, done = env.step(action)
                if done:
                    rewards.append(reward)
            logger.log_performance(env.timestep, np.mean(rewards))

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('DQN')
    
    # Save model
    save_dir = 'models/leduc_holdem_single_dqn'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    saver.save(sess, os.path.join(save_dir, 'model'))
```
