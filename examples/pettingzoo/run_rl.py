''' An example of training a reinforcement learning agent on the PettingZoo 
environments that wrap RLCard
'''
import os
import argparse

import torch

from pettingzoo.classic import (
    leduc_holdem_v4,
    texas_holdem_v4,
    dou_dizhu_v4,
    mahjong_v4,
    texas_holdem_no_limit_v6,
    uno_v4,
    gin_rummy_v4,
)
from rlcard.agents.pettingzoo_agents import RandomAgentPettingZoo
from rlcard.utils import (
    get_device,
    set_seed,
    Logger,
    plot_curve, 
    run_game_pettingzoo,
    reorganize_pettingzoo,
    tournament_pettingzoo,
)

env_name_to_env_func = {
    "leduc-holdem": leduc_holdem_v4,
    "limit-holdem": texas_holdem_v4,
    "doudizhu": dou_dizhu_v4,
    "mahjong": mahjong_v4,
    "no-limit-holdem": texas_holdem_no_limit_v6,
    "uno": uno_v4,
    "gin-rummy": gin_rummy_v4,
}


def train(args):

    # Check whether gpu is available
    device = get_device()
        
    # Seed numpy, torch, random
    set_seed(args.seed)

    # Make the environment with seed
    env_func = env_name_to_env_func[args.env]
    env = env_func.env()
    env.seed(args.seed)
    env.reset()

    # Initialize the agent and use random agents as opponents
    learning_agent_name = env.agents[0]
    if args.algorithm == 'dqn':
        from rlcard.agents.pettingzoo_agents import DQNAgentPettingZoo
        agent = DQNAgentPettingZoo(
            num_actions=env.action_space(learning_agent_name).n,
            state_shape=env.observation_space(learning_agent_name)["observation"].shape,
            mlp_layers=[64,64],
            device=device
        )
    elif args.algorithm == 'nfsp':
        from rlcard.agents.pettingzoo_agents import NFSPAgentPettingZoo
        agent = NFSPAgentPettingZoo(
            num_actions=env.action_space(learning_agent_name).n,
            state_shape=env.observation_space(learning_agent_name)["observation"].shape,
            hidden_layers_sizes=[64,64],
            q_mlp_layers=[64,64],
            device=device
        )

    agents = {learning_agent_name: agent}
    for i in range(1, env.num_agents):
        agents[env.agents[i]] = RandomAgentPettingZoo(num_actions=env.action_space(env.agents[i]).n)

    # Start training
    num_timesteps = 0
    with Logger(args.log_dir) as logger:
        for episode in range(args.num_episodes):

            if args.algorithm == 'nfsp':
                agent.sample_episode_policy()

            # Generate data from the environment
            trajectories = run_game_pettingzoo(env, agents, is_training=True)
            trajectories = reorganize_pettingzoo(trajectories)
            num_timesteps += sum([len(t) for t in trajectories.values()])

            for ts in trajectories[learning_agent_name]:
                agent.feed(ts)

            # Evaluate the performance. Play with random agents.
            if episode % args.evaluate_every == 0:
                average_rewards = tournament_pettingzoo(env, agents, args.num_eval_games)
                logger.log_performance(episode, average_rewards[learning_agent_name])

        # Get the paths
        csv_path, fig_path = logger.csv_path, logger.fig_path

    # Plot the learning curve
    plot_curve(csv_path, fig_path, args.algorithm)

    # Save model
    save_path = os.path.join(args.log_dir, 'model.pth')
    torch.save(agent, save_path)
    print('Model saved in', save_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser("DQN/NFSP example in RLCard")
    parser.add_argument(
        '--env',
        type=str,
        default='leduc-holdem',
        choices=[
            'leduc-holdem',
            'limit-holdem',
            'doudizhu',
            'mahjong',
            'no-limit-holdem',
            'uno',
            'gin-rummy',
        ],
    )
    parser.add_argument(
        '--algorithm',
        type=str,
        default='dqn',
        choices=[
            'dqn',
            'nfsp',
        ],
    )
    parser.add_argument(
        '--cuda',
        type=str,
        default='',
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
    )
    parser.add_argument(
        '--num_episodes',
        type=int,
        default=5000,
    )
    parser.add_argument(
        '--num_eval_games',
        type=int,
        default=2000,
    )
    parser.add_argument(
        '--evaluate_every',
        type=int,
        default=100,
    )
    parser.add_argument(
        '--log_dir',
        type=str,
        default='experiments/leduc_holdem_dqn_result/',
    )

    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    train(args)
