Getting Started
===============

In this document, we provide some toy examples for getting started. For
more examples, please refer to `examples/ <examples>`__.

Playing with Random Agents
~~~~~~~~~~~~~~~~~~~~~~~~~~

We have set up a random agent that can play randomly on each
environment. An example of applying a random agent on Blackjack is as
follow:

.. code:: python

    import rlcard
    from rlcard.agents.random_agent import RandomAgent
    from rlcard.utils.utils import *

    # Make environment
    env = rlcard.make('blackjack')
    episode_num = 2

    # Set a global seed
    set_global_seed(1)

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

The expected output should look like something as follows:

::

    Episode 0
    State: [19, 5], Action: 0, Reward: -1, Next State: [23, 15], Done: True

    Episode 1
    State: [8, 8], Action: 0, Reward: 0, Next State: [17, 8], Done: False
    State: [17, 8], Action: 1, Reward: 1, Next State: [17, 25], Done: True

Note that the states and actions are wrapped by ``env`` in Blackjack. In
this example, the ``[19, 5]`` suggests the current player obtains score
19 while the card that faces up in the dealer's hand has score 5. Action
0 means "hit" while action 1 means "stand". Reward 1 suggests the player
wins while reward -1 suggests the dealer wins. Reward 0 suggests a tie.
The above data can be directly fed into a RL algorithm for training.

Deep-Q Learning on Blackjack
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The second example is to use Deep-Q learning to train an agent on
Blackjack. We aim to use this example to show how reinforcement learning
algorithms can be developed and applied in our toolkit. We design a
``run`` function which plays one complete game and provides the data for
training RL agents. The example is shown below:

.. code:: python

    import tensorflow as tf

    import rlcard
    from rlcard.agents.dqn_agent import DQNAgent
    from rlcard.utils.utils import *
    from rlcard.utils.logger import Logger

    # Make environment
    env = rlcard.make('blackjack')

    # Set the iterations numbers and how frequently we evaluate/save plot
    evaluate_every = 100
    save_plot_every = 1000
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
                           action_num=env.action_num,
                           replay_memory_init_size=memory_init_size,
                           norm_step=norm_step,
                           mlp_layers=[10,10])
        env.set_agents([agent])

        # Count the number of steps
        step_counter = 0

        # Init a Logger to plot the learning curve
        logger = Logger(xlabel='eposide', ylabel='reward', legend='DQN on Blackjack', log_path='./experiments/blackjack_dqn_result/log.txt', csv_path='./experiments/blackjack_dqn_result/performance.csv')

        for episode in range(episode_num):

            # Generate data from the environment
            trajectories, _ = env.run(is_training=True)

            # Feed transitions into agent memory, and train
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

                logger.log('\n########## Evaluation ##########')
                logger.log('Episode: {} Average reward is {}'.format(episode, float(reward)/evaluate_num))

                # Add point to logger
                logger.add_point(x=episode, y=float(reward)/evaluate_num)

            # Make plot
            if episode % save_plot_every == 0 and episode > 0:
                logger.make_plot(save_path='./experiments/blackjack_dqn_result/'+str(episode)+'.png')
        
        # Make the final plot
        logger.make_plot(save_path='./experiments/blackjack_dqn_result/'+'final_'+str(episode)+'.png')

The expected output is something like below:

.. code:: python

    ########## Evaluation ##########
    Average reward is -0.377

    ########## Evaluation ##########
    Average reward is -0.401
    INFO - Step 0 loss: 0.8321959972381592
    INFO - Copied model parameters to target network.
    INFO - Step 60 loss: 0.7190936803817749
    ########## Evaluation ##########
    Average reward is -0.346
    INFO - Step 195 loss: 0.8851202726364136
    ########## Evaluation ##########
    Average reward is -0.211
    INFO - Step 335 loss: 0.7604773640632629
    ########## Evaluation ##########
    Average reward is -0.078
    INFO - Step 479 loss: 0.57902514934539855
    ########## Evaluation ##########
    Average reward is -0.056
    INFO - Step 616 loss: 0.77693158388137823

In Blackjack, the player will get a payoff at the end of the game: 1 if
the player wins, -1 if the player loses, and 0 if it is a tie. The
performance is measured by the average payoff the player obtains by
playing 1000 episodes. The above example shows that the agent achieves
better and better performance during training. The logs and learning
curves are saved in ``./experiments/blackjack_dqn_result/``.

DeepCFR on Blackjack
~~~~~~~~~~~~~~~~~~~~

The third example is to use Deep Counterfactual Regret Minimization to
train an agent on Blackjack. We aim to use this example to show how CFR
algorithms can be developed and applied in our toolkit. We design
``step`` and ``step_back`` function which allows CFR based algorithms
easily perform the game tree traversal for further optimization. The
example is shown below:

.. code:: python

    import rlcard
    from rlcard.agents.deep_cfr import DeepCFR
    from rlcard.utils.utils import *
    import tensorflow as tf
    import numpy as np

    # make environment
    set_global_seed(0)
    evaluate_every = 100
    evaluate_num = 1000
    num_iteration = 1000
    i = 0
    rewards = 0
    train_env = rlcard.make('blackjack') 
    test_env = rlcard.make('blackjack') 
    with tf.Session() as sess:
        deep_cfr = DeepCFR(sess, #
                    train_env, 
                    policy_network_layers=(32,32),
                    advantage_network_layers=(32,32),
                    num_traversals=40,
                    num_step=40
                    learning_rate=1e-4,
                    batch_size_advantage=16,
                    batch_size_strategy=16,
                    memory_capacity=1e7)

        for i in range(num_iteration):
            # Train the agent in training environment
            _, adv_loss, policy_loss = deep_cfr.train()

            # Evaluate the agent
            if i % evaluate_every == 0:
                rewards = 0
                for j in range(evaluate_num):
                    state, player = test_env.init_game()
                    while True:
                        action_prob = deep_cfr.action_probabilities(state)
                        action_prob /= action_prob.sum()
                        action = np.random.choice(np.arange(len(action_prob)), p=action_prob)
                        state, player = test_env.step(action)
                        if test_env.is_over():
                            payoffs = test_env.get_payoffs()
                            rewards += payoffs[0]
                            break
                print('############## Iteration '+str(i)+' #################')
                print('Reward: ', float(rewards)/evaluate_num)
                print('Advantage Loss: ', adv_loss)
                print('Policy Loss: ', policy_loss)

The expected output is shown as below:

.. code:: python

    ############## Iteration 0 #################
    Reward:  -1.0
    Advantage Loss:  3.872990369796753
    Policy Loss:  0.12022944
    ############## Iteration 100 #################
    Reward:  -0.214
    Advantage Loss:  32.23717498779297
    Policy Loss:  1.9331933
    ############## Iteration 200 #################
    Reward:  -0.128
    Advantage Loss:  55.274147033691406
    Policy Loss:  6.15625
    ############## Iteration 300 #################
    Reward:  -0.14
    Advantage Loss:  58.65533447265625
    Policy Loss:  4.0294237
    ############## Iteration 400 #################
    Reward:  -0.142
    Advantage Loss:  74.10326385498047
    Policy Loss:  14.68907
    ############## Iteration 500 #################
    Reward:  -0.172
    Advantage Loss:  165.66090393066406
    Policy Loss:  12.746856
    ############## Iteration 600 #################
    Reward:  -0.187
    Advantage Loss:  161.6951904296875
    Policy Loss:  26.703487
    ############## Iteration 700 #################
    Reward:  -0.083
    Advantage Loss:  220.24888610839844
    Policy Loss:  11.849184
    ############## Iteration 800 #################
    Reward:  -0.102
    Advantage Loss:  251.22244262695312
    Policy Loss:  23.548765
    ############## Iteration 900 #################
    Reward:  -0.093
    Advantage Loss:  159.9312286376953
    Policy Loss:  29.732689

