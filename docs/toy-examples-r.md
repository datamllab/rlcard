# Toy Examples in R
In this document, we provide some toy examples in R for getting started. Parallel Python examples are [here](toy-examples.md).

*   [Training DQN on Blackjack](toy-examples-r.md#deep-q-learning-on-blackjack)
*   [Training CFR on Leduc Hold'em](toy-examples-r.md#training-cfr-on-leduc-holdem)
*   [Leduc Hold'em as single-agent environment](toy-examples-r.md#leduc-holdem-as-single-agent-environment)
*   [Texas Hold'em nolimit](toy-examples-r.md#having-fun-with-no-limit-leduc-model)
*   [Running Random agent on Blackjack](toy-examples-r.md#playing-with-random-agents)

## Playing with Random Agents
We have set up a random agent that can play randomly on each environment. An example of applying a random agent on Blackjack is as follow:
```R
# Install packages
py_install('rlcard', pip=TRUE)
py_install('rlcard[tensorflow]', pip=TRUE)
rlcard <- import('rlcard')
tf <- import('tensorflow')

# Import the modules
os <- import('os')
tf$"__version__"
RandomAgent <- rlcard$agents$RandomAgent
set_global_seed <- rlcard$utils$set_global_seed

# Make environment
config <- list(seed = 0L)
env = rlcard$make('blackjack', config)
episode_num = 2L

# Set a global seed.
set_global_seed(0L)

# Set up agents
agent_0 <- RandomAgent(action_num=env$action_num)
env$set_agents(list(agent_0))

# Train.py
for episode in range(episode_num):

    # Generate data friom the environment
    trajectories, _ = env.run(is_training=False)

    # Print out the trajectories
    print('\nEpisode {}'.format(episode))
    for ts in trajectories[0]:
        print('State: {}, Action: {}, Reward: {}, Next State: {}, Done: {}'.format(ts[0], ts[1], ts[2], ts[3], ts[4]))

# Train the model       
reticulate::source_python("train.py")
train(episode_num, env, agent_0)
```
The expected output should look like something as follows:

```
Episode 0
State: {'obs': array([12, 7]), 'legal_actions': [0, 1]}, Action: 0, Reward: 0, Next State: {'obs': array([21, 7]), 'legal_actions': [0, 1]}, Done: False
State: {'obs': array([21, 7]), 'legal_actions': [0, 1]}, Action: 0, Reward: -1, Next State: {'obs': array([22, 18]), 'legal_actions': [0, 1]}, Done: True

Episode 1
State: {'obs': array([16, 10]), 'legal_actions': [0, 1]}, Action: 1, Reward: -1, Next State: {'obs': array([16, 21]), 'legal_actions': [0, 1]}, Done: True
```

Note that the states and actions are wrapped by env in Blackjack. In this example, the [12, 7] suggests the current player obtains score 12 while the card that faces up in the dealer's hand has score 7. Action 0 means "hit" while action 1 means "stand". Reward 1 suggests the player wins while reward -1 suggests the dealer wins. Reward 0 suggests a tie. The above data can be directly fed into a RL algorithm for training.

## Deep-Q Learning on Blackjack
The second example is to use Deep-Q learning to train an agent on Blackjack. We aim to use this example to show how reinforcement learning algorithms can be developed and applied in our toolkit. We design a `run` function which plays one complete game and provides the data for training RL agents. The example is shown below:
```R
# Install packages
py_install('rlcard', pip=TRUE)
py_install('rlcard[tensorflow]', pip=TRUE)
rlcard <- import('rlcard')
tf <- import('tensorflow')

# Import the modules.
DQNAgent <- rlcard$agents$DQNAgent
set_global_seed <- rlcard$utils$set_global_seed
tournament <- rlcard$utils$tournament
Logger <- rlcard$utils$Logger

# Make environment
config <- list(seed = 0L)
env = rlcard$make('blackjack', config)
eval_env = rlcard$make('blackjack', config)

# Set the iterations numbers and how frequently we evaluate the performance.
evaluate_every = 100L
evaluate_num = 10000L
episode_num = 5000L

# Set the intial memory size.
memory_init_size = 100L

# Train the agent every X steps.
train_every = 1

# Set the paths for saving the logs and learning curves. We save it on our current path.
log_dir = './blackjack_dqn_result/'

# Set a global seed.
set_global_seed(0L)
sess <- tf$Session()

# Initialize a global step.
global_step = tf$Variable(0L, name='global_step', trainable=F)

# Set up the DQN agents.
agent = DQNAgent(
  sess,
  scope='dqn',
  action_num=env$action_num,
  replay_memory_init_size = memory_init_size,
  train_every=train_every,
  state_shape=env$state_shape,
  mlp_layers=c(10, 10)
)
env$set_agents(list(agent))
eval_env$set_agents(list(agent))

# Initialize global variables and a Logger to plot the learning curve.
sess$run(tf$global_variables_initializer())
logger = Logger(log_dir)

# train.py
def train(episode_num, env, eval_env, evaluate_every, evaluate_num, agent, logger, tournament):
    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent
        for ts in trajectories[0]:
            agent.feed(ts)

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])
# Train the model
reticulate::source_python("train.py")
train(episode_num, env, eval_env, evaluate_every, evaluate_num, agent, logger, tournament)

# Close files in the logger
logger$close_files()
logger$plot('DQN')

# Plot the learning curve
logger$close_files()
logger$plot('DQN')

# Save model
save_dir = 'models/blackjack_dqn'
if (!dir.exists(save_dir)){
    os$makedirs(save_dir)}
saver = tf$train$Saver()
saver$save(sess, os$path$join(save_dir, 'model'))
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

## Training CFR on Leduc Hold'em
To show how we can use `step` and `step_back` to traverse the game tree, we provide an example of solving Leduc Hold'em with CFR:
```R
# Install packages
py_install('rlcard', pip=TRUE)
py_install('rlcard[tensorflow]', pip=TRUE)
rlcard <- import('rlcard')
tf <- import('tensorflow')
os <- import('os')
tf$"__version__"

# Import the modules.
CFRAgent <- rlcard$agents$CFRAgent
models <- rlcard$models
set_global_seed <- rlcard$utils$set_global_seed
tournament <- rlcard$utils$tournament
Logger <- rlcard$utils$Logger

# Make environment
config1 <- list(seed = 0L, allow_step_back = TRUE)
config2 <- list(seed = 0L)
env = rlcard$make('leduc-holdem', config1)
eval_env = rlcard$make('leduc-holdem', config2)

# Set the iterations numbers and how frequently we evaluate the performance.
evaluate_every = 10L
save_plot_every = 1000L
evaluate_num = 10000L
episode_num = 300L

# Set the paths for saving the logs and learning curves. We save it on our current path.
log_dir = './Leduc_holdem_cfr_result/'

# Set a global seed.
set_global_seed(0L)

# Initilize CFR Agent
agent = CFRAgent(env)
agent$load()  # If we have saved model, we first load the model
agents <- models$load('leduc-holdem-nfsp')$agents
agents[[1]] <- agent

# Evaluate CFR against pre-trained NFSP
eval_env$set_agents(agents)

# Initialize global variables and a Logger to plot the learning curve.
logger = Logger(log_dir)

# train.py
def train(episode_num, env, eval_env, evaluate_every, evaluate_num, agent, logger, tournament):
for episode in range(episode_num):
    agent.train()
    print('\rIteration {}'.format(episode), end='')
    # Evaluate the performance. Play with NFSP agents.
    if episode % evaluate_every == 0:
        agent.save() # Save model
        logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])
        
# Train the model
reticulate::source_python("train.py")
train(episode_num, env, eval_env, evaluate_every, evaluate_num, agent, logger, tournament)

# Close files in the logger
logger$close_files()

# Plot the learning curve
logger$plot('CFR')
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

## Having Fun with no-limit Leduc Model
Leduc Hold'em is a simplified version of Texas Hold'em. Rules can be found [here](games.md#leduc-holdem). Example of playing against Leduc Hold'em CFR model is as below:
```R
# Install packages
py_install('rlcard', pip=TRUE)
py_install('rlcard[tensorflow]', pip=TRUE)
rlcard <- import('rlcard')
tf <- import('tensorflow')
os <- import('os')

# Import the modules.
DQNAgent <- rlcard$agents$DQNAgent
RandomAgent <- rlcard$agents$RandomAgent
set_global_seed <- rlcard$utils$set_global_seed
tournament <- rlcard$utils$tournament
Logger <- rlcard$utils$Logger

# Make environment
env = rlcard$make('no-limit-holdem')
eval_env = rlcard$make('no-limit-holdem')

# Set the iterations numbers and how frequently we evaluate the performance.
evaluate_every = 100L
evaluate_num = 1000L
episode_num = 10000L

# Set the intial memory size.
memory_init_size = 1000L

# Train the agent every X steps.
train_every = 1

# Set the paths for saving the logs and learning curves. We save it on our current path.
log_dir = './log'

# Set a global seed.
set_global_seed(0L)
sess <- tf$Session()

# Initialize a global step.
global_step = tf$Variable(0L, name='global_step', trainable=F)

# Set up the DQN agents.
agent = DQNAgent(
  sess,
  scope='dqn',
  action_num=env$action_num,
  replay_memory_init_size = memory_init_size,
  train_every=train_every,
  state_shape=env$state_shape,
  mlp_layers=c(512, 512)
)

random_agent = RandomAgent(action_num=eval_env$action_num)
env$set_agents(list(agent, random_agent))
eval_env$set_agents(list(agent, random_agent))

# Initialize global variables and a Logger to plot the learning curve.
sess$run(tf$global_variables_initializer())
logger = Logger(log_dir)

# train.py
def train(episode_num, env, eval_env, evaluate_every, evaluate_num, agent, logger, tournament):
   for episode in range(episode_num):

     # Generate data from the environment
     trajectories, _ = env.run(is_training = True)

     # Feed transitions into agent memory, and train the agent
     for ts in trajectories[0]:
         agent.feed(ts)

     # Evaluate the performance. Play with random agents.
     if episode % evaluate_every == 0:
         logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

# Train the model
reticulate::source_python("train.py")
train(episode_num, env, eval_env, evaluate_every, evaluate_num, agent, logger, tournament)
  
 # Close files in the logger
logger$close_files()
```

## Leduc Hold'em as Single-Agent Environment
We have wrraped the environment as single agent environment by assuming that other players play with pre-trained models. The interfaces are exactly the same to OpenAI Gym. Thus, any single-agent algorithm can be connected to the environment. An example of Leduc Hold'em is as below:
```R
# Install packages
py_install('rlcard', pip=TRUE)
py_install('rlcard[tensorflow]', pip=TRUE)
py_install('numpy', pip=TRUE)

rlcard <- import('rlcard')
tf <- import('tensorflow')
os <- import('os')
np <- import('numpy')

# Import the modules.
DQNAgent <- rlcard$agents$DQNAgent
RandomAgent <- rlcard$agents$RandomAgent
set_global_seed <- rlcard$utils$set_global_seed
tournament <- rlcard$utils$tournament
Logger <- rlcard$utils$Logger

# Make environment
config <- list(seed = 0L, single_agent_mode = TRUE)
env = rlcard$make('leduc-holdem', config)
eval_env = rlcard$make('leduc-holdem', config)

# Set the iterations numbers and how frequently we evaluate the performance.
evaluate_every = 1000L
evaluate_num = 10000L
timesteps = 20000L

# Set the intial memory size.
memory_init_size = 1000L

# Train the agent every X steps.
train_every = 1

# Set the paths for saving the logs and learning curves. We save it on our current path.
log_dir = './Leduc_holdem_dqn_result/'

# Set a global seed.
set_global_seed(0L)
sess <- tf$Session()

# Initialize a global step.
global_step = tf$Variable(0L, name='global_step', trainable=F)

# Set up the DQN agents.
agent = DQNAgent(
  sess,
  scope='dqn',
  action_num=env$action_num,
  replay_memory_init_size = memory_init_size,
  train_every=train_every,
  state_shape=env$state_shape,
  mlp_layers=c(128, 128)
)
# Initialize global variables and a Logger to plot the learning curve.
sess$run(tf$global_variables_initializer())


# Init a Logger to plot the learning curve
logger = Logger(log_dir)
state = env$reset()

# train.py
def train(timesteps, action, state, next_state, evaluate_num):
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

# Train the model
reticulate::source_python("train.py")
train(timesteps, env, eval_env, evaluate_every, evaluate_num, agent, logger, state)    

# Close files in the logger
logger$close_files()


# Plot the learning curve
logger$plot('DQN')
    
# Save model
save_dir = 'models/leduc_holdem_single_dqn'
if (!dir.exists(save_dir)){
    os$makedirs(save_dir)}
saver = tf$train$Saver()
saver$save(sess, os$path$join(save_dir, 'model'))
```


