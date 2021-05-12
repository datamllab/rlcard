''' An example of learning a Deep-Q Agent on the environments in RLCard
'''
import os
import argparse

import torch

import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import get_device, set_seed, tournament, reorganize, Logger

def train(args):

    # Check whether gpu is available
    device = get_device()
        
    # Seed nmupy, torch, random
    set_seed(args.seed)

    # Make the environment with seed
    env = rlcard.make(args.env, config={'seed': args.seed})

    # Initialize the agent and use random agents as opponents
    if args.algorithm == 'dqn':
        from rlcard.agents import DQNAgent
        agent = DQNAgent(action_num=env.action_num,
                         state_shape=env.state_shape,
                         mlp_layers=[64,64])
    elif args.algorithm == 'nfsp':
        from rlcard.agents import NFSPAgent
        agent = NFSPAgent(action_num=env.action_num,
                          state_shape=env.state_shape,
                          hidden_layers_sizes=[64,64],
                          q_mlp_layers=[64,64])
    agents = [agent]
    for _ in range(env.player_num):
        agents.append(RandomAgent(action_num=env.action_num))
    env.set_agents(agents)

    # Start training
    with Logger(args.log_dir) as logger:
        for episode in range(args.episode_num):

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
                logger.log_performance(env.timestep, tournament(env, args.evaluate_num)[0])

        # Plot the learning curve
        logger.plot(args.algorithm)

    # Save model
    save_path = os.path.join(args.log_dir, 'model.pth')
    torch.save(agent, save_path)
    #agent.save(save_path)
    print('Model saved in', save_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("DQN example in RLCard")
    parser.add_argument('--env', type=str, default='leduc-holdem')
    parser.add_argument('--algorithm', type=str, default='dqn', choices=['dqn', 'nfsp'])
    parser.add_argument('--cuda', type=str, default='')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--episode_num', type=int, default=5000)
    parser.add_argument('--evaluate_num', type=int, default=2000)
    parser.add_argument('--evaluate_every', type=int, default=100)
    parser.add_argument('--log_dir', type=str, default='experiments/leduc_holdem_dqn_result/')

    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    train(args)

