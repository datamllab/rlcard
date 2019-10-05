# Toy Examples
In this document, we provide some toy examples for getting started. All the examples shown in this document and even more examples are available in [examples/](../examples).

## Playing with Random Agents
We have set up a random agent that can play randomly on each environment. An example of applying a random agent on Blackjack is as follow:
```python
import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed

# Make environment
env = rlcard.make('blackjack')
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
```shell
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

import rlcard
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.utils.utils import set_global_seed
from rlcard.utils.logger import Logger

# Make environment
env = rlcard.make('blackjack')
eval_env = rlcard.make('blackjack')

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 100
save_plot_every = 1000
evaluate_num = 10000
episode_num = 1000000

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 100
norm_step = 100

# The paths for saving the logs and learning curves
root_path = './experiments/blackjack_dqn_result/'
log_path = root_path + 'log.txt'
csv_path = root_path + 'performance.csv'
figure_path = root_path + 'figures/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:

    # Set agents
    global_step = tf.Variable(0, name='global_step', trainable=False)
    agent = DQNAgent(sess,
                     scope='dqn',
                     action_num=env.action_num,
                     replay_memory_init_size=memory_init_size,
                     norm_step=norm_step,
                     state_shape=env.state_shape,
                     mlp_layers=[10,10])
    env.set_agents([agent])
    eval_env.set_agents([agent])

    sess.run(tf.global_variables_initializer())

    # Count the number of steps
    step_counter = 0

    # Init a Logger to plot the learning curve
    logger = Logger(xlabel='timestep', ylabel='reward', legend='DQN on Blackjack', log_path=log_path, csv_path=csv_path)

    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train
        for ts in trajectories[0]:
            agent.feed(ts)
            step_counter += 1

            # Train the agent
            if step_counter > memory_init_size + norm_step:
                loss = agent.train()
                print('\rINFO - Step {}, loss: {}'.format(step_counter, loss), end='')

        # Evaluate the performance
        if episode % evaluate_every == 0:
            reward = 0
            for eval_episode in range(evaluate_num):
                _, payoffs = eval_env.run(is_training=False)
                reward += payoffs[0]

            logger.log('\n########## Evaluation ##########')
            logger.log('Timestep: {} Average reward is {}'.format(env.timestep, float(reward)/evaluate_num))

            # Add point to logger
            logger.add_point(x=env.timestep, y=float(reward)/evaluate_num)

        # Make plot
        if episode % save_plot_every == 0 and episode > 0:
            logger.make_plot(save_path=figure_path+str(episode)+'.png')

    # Make the final plot
    logger.make_plot(save_path=figure_path+'final_'+str(episode)+'.png')
```
The expected output is something like below:
```shell
########## Evaluation ##########
Timestep: 1 Average reward is -0.2868

########## Evaluation ##########
Timestep: 136 Average reward is -0.642

INFO - Copied model parameters to target network.
INFO - Step 271, loss: 0.6861089468002319
########## Evaluation ##########
Timestep: 271 Average reward is -0.5751
INFO - Step 402, loss: 0.7866340875625612
########## Evaluation ##########
Timestep: 402 Average reward is -0.5857
INFO - Step 537, loss: 0.7525347471237183
########## Evaluation ##########
Timestep: 537 Average reward is -0.5762
INFO - Step 681, loss: 0.7957633137702942
########## Evaluation ##########
Timestep: 681 Average reward is -0.4895
INFO - Step 824, loss: 0.8273138403892517
########## Evaluation ##########
Timestep: 824 Average reward is -0.4341
INFO - Step 958, loss: 0.7127346992492676
########## Evaluation ##########
Timestep: 958 Average reward is -0.3816
INFO - Step 1093, loss: 0.61426079273223884
########## Evaluation ##########
Timestep: 1093 Average reward is -0.2907
INFO - Step 1200, loss: 0.7053447961807251
INFO - Copied model parameters to target network.
INFO - Step 1221, loss: 0.7781758308410645
########## Evaluation ##########
Timestep: 1221 Average reward is -0.2197
```
In Blackjack, the player will get a payoff at the end of the game: 1 if the player wins, -1 if the player loses, and 0 if it is a tie. The performance is measured by the average payoff the player obtains by playing 1000 episodes. The above example shows that the agent achieves better and better performance during training. The logs and learning curves are saved in `./experiments/blackjack_dqn_result/`.

## Running Multiple Processes
(under construction)

## Having Fun with Pretrained Leduc Model
We have designed simple human interfaces to play against the pretrained model! Example of playing against Leduc Hold'em AI is as below: ()
```python
import rlcard

# Make environment and enable human mode
env = rlcard.make('leduc-holdem')

# Set it to human mode
env.set_mode(human_mode=True)

# Reset environment
env.reset()

while True:
    action = int(input(">> You choose action (integer): "))
    env.step(action)
```
Example output is as follow:
```shell
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

## Leduc Hold'em as Single-Agent Environment
We have wrraped the environment as single agent environment by assuming that other players play with pre-trained models. The interfaces are exactly same to OpenAI Gym. Thus, any single-agent algorithm can be connected to the environment. An example of Leduc Hold'em is as below:
```python
import tensorflow as tf
import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.agents.dqn_agent import DQNAgent
from rlcard.utils.utils import set_global_seed
from rlcard.utils.logger import Logger

# Make environment and enable single mode
env = rlcard.make('leduc-holdem')
eval_env = rlcard.make('leduc-holdem')
env.set_mode(single_agent_mode=True)
eval_env.set_mode(single_agent_mode=True)

# Set the iterations numbers and how frequently we evaluate/save plot
evaluate_every = 1000
save_plot_every = 1000
evaluate_num = 10000
timesteps = 1000000

# Set the the number of steps for collecting normalization statistics
# and intial memory size
memory_init_size = 1000
norm_step = 100

# The paths for saving the logs and learning curves
root_path = './experiments/leduc_holdem_single_agent_dqn_result/'
log_path = root_path + 'log.txt'
csv_path = root_path + 'performance.csv'
figure_path = root_path + 'figures/'

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:
    global_step = tf.Variable(0, name='global_step', trainable=False)
    agent = DQNAgent(sess,
                     scope='dqn',
                     action_num=env.action_num,
                     replay_memory_size=int(1e5),
                     replay_memory_init_size=memory_init_size,
                     norm_step=norm_step,
                     state_shape=env.state_shape,
                     mlp_layers=[128, 128])

    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(xlabel='timestep', ylabel='reward', legend='DQN on Leduc Holdem', log_path=log_path, csv_path=csv_path)

    state = env.reset()

    for timestep in range(timesteps):
        action = agent.step(state)
        next_state, reward, done = env.step(action)
        ts = (state, action, reward, next_state, done)
        agent.feed(ts)

        train_count = timestep - (memory_init_size + norm_step)
        if train_count > 0:
            loss = agent.train()
            print('\rINFO - Step {}, loss: {}'.format(timestep, loss), end='')

        if timestep % evaluate_every == 0:
            rewards = []
            state = eval_env.reset()
            for _ in range(evaluate_num):
                action = agent.eval_step(state)
                _, reward, done = env.step(action)
                if done:
                    rewards.append(reward)
            logger.log('\n########## Evaluation ##########')
            logger.log('Timestep: {} Average reward is {}'.format(timestep, np.mean(rewards)))

            # Add point to logger
            logger.add_point(x=env.timestep, y=float(reward)/evaluate_num)

        # Make plot
        if timestep % save_plot_every == 0:
            logger.make_plot(save_path=figure_path+str(timestep)+'.png')

    # Make the final plot
    logger.make_plot(save_path=figure_path+'final_'+str(timestep)+'.png')
```
