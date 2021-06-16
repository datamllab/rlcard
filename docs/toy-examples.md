# Toy Examples
In this document, we provide some toy examples for getting started. All the examples are available in [examples/](../examples).

*   [Playing with random agents](toy-examples.md#playing-with-random-agents)
*   [Deep-Q learning on Blackjack](toy-examples.md#deep-q-learning-on-blackjack)
*   [Training CFR (chance sampling) on Leduc Hold'em](toy-examples.md#training-cfr-on-leduc-holdem)
*   [Having fun with pretrained Leduc model](toy-examples.md#having-fun-with-pretrained-leduc-model)
*   [Training DMC on Dou Dizhu](toy-examples.md#training-dmc-on-dou-dizhu)
*   [Evaluating Agents](toy-examples.md#evaluating-agents)

## Playing with Random Agents
We provide a random agent that can play randomly on each environment. Example code is as follows. You can also find the code in [examples/run\_random.py](../examples/run_random.py)
```python
import argparse

import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import set_seed

def run(args):
    # Make environment
    env = rlcard.make(args.env, config={'seed': 42})
    num_episodes = 1

    # Seed numpy, torch, random
    set_seed(42)

    # Set agents
    agent = RandomAgent(num_actions=env.num_actions)
    env.set_agents([agent for _ in range(env.num_players)])

    for episode in range(num_episodes):

        # Generate data from the environment
        trajectories, player_wins = env.run(is_training=False)
        # Print out the trajectories
        print('\nEpisode {}'.format(episode))
        print(trajectories)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Random example in RLCard")
    parser.add_argument('--env', type=str, default='leduc-holdem')

    args = parser.parse_args()

    run(args)
```
Run the code to randomly generate data from Leduc Hold'em with
```
python3 examples/run_random.py --env leduc-holdem
```
The expected output should look like something as follows:

```

Trajectories:
[[{'legal_actions': {1: None, 2: None, 3: None}, 'obs': array([0., 1., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0.]), 'raw_obs': {'hand': 'HQ', 'public_card': None, 'all_chips': [2, 1], 'my_chips': 2, 'legal_actions': ['raise', 'fold', 'check'], 'current_player': 0}, 'raw_legal_actions': ['raise', 'fold', 'check'], 'action_record': [(1, 'fold')]}], [{'legal_actions': {0: None, 1: None, 2: None}, 'obs': array([1., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0.]), 'raw_obs': {'hand': 'HJ', 'public_card': None, 'all_chips': [2, 1], 'my_chips': 1, 'legal_actions': ['call', 'raise', 'fold'], 'current_player': 1}, 'raw_legal_actions': ['call', 'raise', 'fold'], 'action_record': [(1, 'fold')]}, 2, {'legal_actions': {1: None, 2: None, 3: None}, 'obs': array([1., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
       0., 0.]), 'raw_obs': {'hand': 'HJ', 'public_card': None, 'all_chips': [2, 1], 'my_chips': 1, 'legal_actions': ['raise', 'fold', 'check'], 'current_player': 0}, 'raw_legal_actions': ['raise', 'fold', 'check'], 'action_record': [(1, 'fold')]}]]

Sample raw observation:
{'all_chips': [2, 1],
 'current_player': 0,
 'hand': 'HQ',
 'legal_actions': ['raise', 'fold', 'check'],
 'my_chips': 2,
 'public_card': None}

Sample raw legal_actions:
['raise', 'fold', 'check']
```

## Deep-Q Learning on Blackjack
The second example is to use Deep-Q learning to train an agent on Blackjack. We aim to use this example to show how reinforcement learning algorithms can be developed and applied in our toolkit. We design a `run` function which plays one complete game and provides the data for training RL agents. The example is shown below. You can also find the code in [examples/run\_rl.py](../examples/run_rl.py).
```python
import os
import argparse

import torch

import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import get_device, set_seed, tournament, reorganize, Logger

def train(args):

    # Check whether gpu is available
    device = get_device()
        
    # Seed numpy, torch, random
    set_seed(args.seed)

    # Make the environment with seed
    env = rlcard.make(args.env, config={'seed': args.seed})

    # Initialize the agent and use random agents as opponents
    if args.algorithm == 'dqn':
        from rlcard.agents import DQNAgent
        agent = DQNAgent(num_actions=env.num_actions,
                         state_shape=env.state_shape[0],
                         mlp_layers=[64,64],
                         device=device)
    elif args.algorithm == 'nfsp':
        from rlcard.agents import NFSPAgent
        agent = NFSPAgent(num_actions=env.num_actions,
                          state_shape=env.state_shape[0],
                          hidden_layers_sizes=[64,64],
                          q_mlp_layers=[64,64],
                          device=device)
    agents = [agent]
    for _ in range(env.num_players):
        agents.append(RandomAgent(num_actions=env.num_actions))
    env.set_agents(agents)

    # Start training
    with Logger(args.log_dir) as logger:
        for episode in range(args.num_episodes):

            if args.algorithm == 'nfsp':
                agents[0].sample_episode_policy()

            # Generate data from the environment
            trajectories, payoffs = env.run(is_training=True)

            # Reorganaize the data to be state, action, reward, next_state, done
            trajectories = reorganize(trajectories, payoffs)

            # Feed transitions into agent memory, and train the agent
            # Here, we assume that DQN always plays the first position
            # and the other players play randomly (if any)
            for ts in trajectories[0]:
                agent.feed(ts)

            # Evaluate the performance. Play with random agents.
            if episode % args.evaluate_every == 0:
                logger.log_performance(env.timestep, tournament(env, args.num_games)[0])

        # Plot the learning curve
        logger.plot(args.algorithm)

    # Save model
    save_path = os.path.join(args.log_dir, 'model.pth')
    torch.save(agent, save_path)
    print('Model saved in', save_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("DQN example in RLCard")
    parser.add_argument('--env', type=str, default='leduc-holdem')
    parser.add_argument('--algorithm', type=str, default='dqn', choices=['dqn', 'nfsp'])
    parser.add_argument('--cuda', type=str, default='')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--num_episodes', type=int, default=5000)
    parser.add_argument('--num_games', type=int, default=2000)
    parser.add_argument('--evaluate_every', type=int, default=100)
    parser.add_argument('--log_dir', type=str, default='experiments/leduc_holdem_dqn_result/')

    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    train(args)
```
Train DQN on Blackjack with
```
python3 examples/run_rl.py --env blackjack --algorithm dqn
```
The expected output is something like below:

```
--> Running on the CPU

----------------------------------------
  timestep     |  2
  reward       |  -0.213
----------------------------------------
INFO - Step 100, rl-loss: 1.2863489389419556
INFO - Copied model parameters to target network.
INFO - Step 153, rl-loss: 0.68201494216918955
----------------------------------------
  timestep     |  2153
  reward       |  -0.2855
----------------------------------------
INFO - Step 274, rl-loss: 0.48299887776374817
----------------------------------------
  timestep     |  5133
  reward       |  -0.105
----------------------------------------
INFO - Step 412, rl-loss: 0.41647660732269287
----------------------------------------
  timestep     |  7615
  reward       |  -0.1375
----------------------------------------
INFO - Step 545, rl-loss: 0.48143920302391055
----------------------------------------
```

In Blackjack, the player will get a payoff at the end of the game: 1 if the player wins, -1 if the player loses, and 0 if it is a tie. The performance is measured by the average payoff the player obtains by playing 10000 episodes. The above example shows that the agent achieves better and better performance during training. The logs and learning curves are saved in `experiments/blackjack_dqn_result/`.

You can also freely try nfsp algorithm or other environments by simply changing the arguments.

## Training CFR (chance sampling) on Leduc Hold'em
To show how we can use `step` and `step_back` to traverse the game tree, we provide an example of solving Leduc Hold'em with CFR (chance sampling). You can also find the code in [examples/run_cfr.py](../examples/run_cfr.py).
```python
import os
import argparse

import rlcard
from rlcard.agents import CFRAgent, RandomAgent
from rlcard.utils import set_seed, tournament, Logger

def train(args):
    # Make environments, CFR only supports Leduc Holdem
    env = rlcard.make('leduc-holdem', config={'seed': 0, 'allow_step_back':True})
    eval_env = rlcard.make('leduc-holdem', config={'seed': 0})

    # Seed numpy, torch, random
    set_seed(args.seed)

    # Initilize CFR Agent
    agent = CFRAgent(env, os.path.join(args.log_dir, 'cfr_model'))
    agent.load()  # If we have saved model, we first load the model

    # Evaluate CFR against random
    eval_env.set_agents([agent, RandomAgent(num_actions=env.num_actions)])

    # Start training
    with Logger(args.log_dir) as logger:
        for episode in range(args.num_episodes):
            agent.train()
            print('\rIteration {}'.format(episode), end='')
            # Evaluate the performance. Play with Random agents.
            if episode % args.evaluate_every == 0:
                agent.save() # Save model
                logger.log_performance(env.timestep, tournament(eval_env, args.num_games)[0])

        # Plot the learning curve
        logger.plot('CFR')

if __name__ == '__main__':
    parser = argparse.ArgumentParser("DQN example in RLCard")
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--num_episodes', type=int, default=5000)
    parser.add_argument('--num_games', type=int, default=2000)
    parser.add_argument('--evaluate_every', type=int, default=100)
    parser.add_argument('--log_dir', type=str, default='experiments/leduc_holdem_cfr_result/')

    args = parser.parse_args()

    train(args)
```
Run the code with
```
python3 examples/run_cfr.py
```
The expected output is as below:
```
Iteration 0
----------------------------------------
  timestep     |  192
  reward       |  0.80175
----------------------------------------
Iteration 100
----------------------------------------
  timestep     |  19392
  reward       |  0.75675
----------------------------------------
Iteration 200
----------------------------------------
  timestep     |  38592
  reward       |  0.8145
----------------------------------------
Iteration 300
----------------------------------------
  timestep     |  57792
  reward       |  0.66375
----------------------------------------
```

## Having Fun with Pretrained Leduc Model
We have designed simple human interfaces to play against the pretrained model. Leduc Hold'em is a simplified version of Texas Hold'em. Rules can be found [here](games.md#leduc-holdem). Example of playing against Leduc Hold'em CFR (chance sampling) model is as below. You can find the code in [examples/human/leduc\_holdem\_human.py](../examples/human/leduc_holdem_human.py)
```python
import rlcard
from rlcard import models
from rlcard.agents import LeducholdemHumanAgent as HumanAgent
from rlcard.utils import print_card

# Make environment
# Set 'record_action' to True because we need it to print results
env = rlcard.make('leduc-holdem', config={'record_action': True})
human_agent = HumanAgent(env.num_actions)
cfr_agent = models.load('leduc-holdem-cfr').agents[0]
env.set_agents([human_agent, cfr_agent])

print(">> Leduc Hold'em pre-trained model")

while (True):
    print(">> Start a new game")

    trajectories, payoffs = env.run(is_training=False)
    # If the human does not take the final action, we need to
    # print other players action
    final_state = trajectories[0][-1]
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

## Training DMC on Dou Dizhu
Finally, we provide an example to traing Deep Monte-Carlo (DMC) on the large-scale game Dou Dizhu. You can also find the code in [examples/run\_dmc.py](../examples/run_dmc.py).
```python
import os
import argparse

import torch

import rlcard
from rlcard.agents.dmc_agent import DMCTrainer

def train(args):

    # Make the environment
    env = rlcard.make(args.env)

    # Initialize the DMC trainer
    trainer = DMCTrainer(env,
                         load_model=args.load_model,
                         xpid=args.xpid,
                         savedir=args.savedir,
                         save_interval=args.save_interval,
                         num_actor_devices=args.num_actor_devices,
                         num_actors=args.num_actors,
                         training_device=args.training_device)

    # Train DMC Agents
    trainer.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser("DQN example in RLCard")
    parser.add_argument('--env', type=str, default='doudizhu')
    parser.add_argument('--cuda', type=str, default='1')
    parser.add_argument('--load_model', action='store_true',
                    help='Load an existing model')
    parser.add_argument('--xpid', default='doudizhu',
                        help='Experiment id (default: doudizhu)')
    parser.add_argument('--savedir', default='experiments/dmc_result',
                        help='Root dir where experiment data will be saved')
    parser.add_argument('--save_interval', default=30, type=int,
                        help='Time interval (in minutes) at which to save the model')
    parser.add_argument('--num_actor_devices', default=1, type=int,
                        help='The number of devices used for simulation')
    parser.add_argument('--num_actors', default=5, type=int,
                        help='The number of actors for each simulation device')
    parser.add_argument('--training_device', default=0, type=int,
                        help='The index of the GPU used for training models')

    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    train(args)
```
Run DMC with
```
python3 examples/run_dmc.py
```
The expected output is as below:
```
Creating log directory: experiments/dmc_result/doudizhu
Saving arguments to experiments/dmc_result/doudizhu/meta.json
Saving messages to experiments/dmc_result/doudizhu/out.log
Saving logs data to experiments/dmc_result/doudizhu/logs.csv
Saving logs' fields to experiments/dmc_result/doudizhu/fields.csv
[INFO:8880 utils:66 2021-05-15 20:41:21,447] Device 0 Actor 0 started.
[INFO:8957 utils:66 2021-05-15 20:41:25,990] Device 0 Actor 1 started.
[INFO:9033 utils:66 2021-05-15 20:41:30,504] Device 0 Actor 2 started.
[INFO:9111 utils:66 2021-05-15 20:41:34,976] Device 0 Actor 3 started.
[INFO:9185 utils:66 2021-05-15 20:41:39,535] Device 0 Actor 4 started.
Updated log fields: ['_tick', '_time', 'frames', 'mean_episode_return_0', 'loss_0', 'mean_episode_return_1', 'loss_1', 'mean_episode_return_2', 'loss_2']
[INFO:8802 trainer:244 2021-05-15 20:41:44,550] Saving checkpoint to experiments/dmc_result/doudizhu/model.tar
[INFO:8802 trainer:276 2021-05-15 20:41:44,668] After 9600 frames: @ 1873.8 fps Stats:
{'loss_0': 0.27473658323287964,
 'loss_1': 0.8208091259002686,
 'loss_2': 0.7109626531600952,
 'mean_episode_return_0': 0.24358974397182465,
 'mean_episode_return_1': 0.7515923976898193,
 'mean_episode_return_2': 0.762499988079071}
[INFO:8802 trainer:276 2021-05-15 20:41:49,674] After 19200 frames: @ 1918.0 fps Stats:
{'loss_0': 0.4458627700805664,
 'loss_1': 0.5232920050621033,
 'loss_2': 0.43021461367607117,
 'mean_episode_return_0': 0.3717948794364929,
 'mean_episode_return_1': 0.6348323225975037,
 'mean_episode_return_2': 0.6357409954071045}
```
The models will by defult be saved in `experiments/dmc_result/doudizhu`. I have provide some scripts to run DMC in single/multiple GPUs in [examples/scripts/](../examples/scripts/). To evaluate the performance, see [here](toy-examples.md#evaluating-dmc-on-dou-dizhu).

## Evaluating Agents
We also provide an example to compare agents. You can find the code in [examples/evaluate.py](examples/evaluate.py)
```python
import os
import argparse

import rlcard
from rlcard.agents import DQNAgent, RandomAgent
from rlcard.utils import get_device, set_seed, tournament, reorganize, Logger

def load_model(model_path, env=None, position=None, device=None):
    if os.path.isfile(model_path):  # Torch model
        import torch
        agent = torch.load(model_path, map_location=device)
        agent.set_device(device)
    elif os.path.isdir(model_path):  # CFR model
        from rlcard.agents import CFRAgent
        agent = CFRAgent(env, model_path)
        agent.load()
    elif model_path == 'random':  # Random model
        from rlcard.agents import RandomAgent
        agent = RandomAgent(num_actions=env.num_actions)
    else:  # A model in the model zoo
        from rlcard import models
        agent = models.load(model_path).agents[position]
    
    return agent

def evaluate(args):

    # Check whether gpu is available
    device = get_device()
        
    # Seed numpy, torch, random
    set_seed(args.seed)

    # Make the environment with seed
    env = rlcard.make(args.env, config={'seed': args.seed})

    # Load models
    agents = []
    for position, model_path in enumerate(args.models):
        agents.append(load_model(model_path, env, position, device))
    env.set_agents(agents)

    # Evaluate
    rewards = tournament(env, args.num_games)
    for position, reward in enumerate(rewards):
        print(position, args.models[position], reward)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("Evaluation example in RLCard")
    parser.add_argument('--env', type=str, default='leduc-holdem')
    parser.add_argument('--models', nargs='*', default=['experiments/leduc_holdem_dqn_result/model.pth', 'random'])
    parser.add_argument('--cuda', type=str, default='')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--num_games', type=int, default=10000)

    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    evaluate(args)
```
We assume that you have already trained a DQN agent on Leduc Hold'em. Run the following command to compare the agent with random agent:
```
python3 examples/evaluate.py
```
The expected output is as below:
```
--> Running on the CPU
0 experiments/leduc_holdem_dqn_result/model.pth 1.21185
1 random -1.21185
```

### Evaluating DMC on Dou Dizhu
DMC models can be similarly loaded with the evaluation script. To achieve this, you need to first specify which checkpoint you would like to load. Then you can eveluate DMC by similarly passing the model paths to the script. For example, you may evaluate DMC landlord against rule peasants with (the exact timestep could differ):
```
python3 examples/evaluate.py --env doudizhu --models experiments/dmc_result/doudizhu/0_432758400.pth doudizhu-rule-v1 doudizhu-rule-v1 --cuda 0 --num_games 1000
```
You may also do it reversely by running
```
python3 examples/evaluate.py --env doudizhu --models doudizhu-rule-v1 experiments/dmc_result/doudizhu/1_432758400.pth experiments/dmc_result/doudizhu/2_432758400.pth --cuda 0 --num_games 1000
```
