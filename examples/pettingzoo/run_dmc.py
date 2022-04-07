''' An example of training a Deep Monte-Carlo (DMC) Agent on PettingZoo environments
wrapping RLCard
'''
import os
import argparse

from pettingzoo.classic import (
    leduc_holdem_v4,
    texas_holdem_v4,
    dou_dizhu_v4,
    mahjong_v4,
    texas_holdem_no_limit_v6,
    uno_v4,
    gin_rummy_v4,
)

from rlcard.agents.dmc_agent import DMCTrainer


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
    # Make the environment
    env_func = env_name_to_env_func[args.env]
    env = env_func.env()
    env.reset()

    # Initialize the DMC trainer
    trainer = DMCTrainer(
        env,
        is_pettingzoo_env=True,
        load_model=args.load_model,
        xpid=args.xpid,
        savedir=args.savedir,
        save_interval=args.save_interval,
        num_actor_devices=args.num_actor_devices,
        num_actors=args.num_actors,
        training_device=args.training_device,
        total_frames=args.total_frames,
    )

    # Train DMC Agents
    trainer.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser("DMC example in RLCard")
    parser.add_argument(
        '--env',
        type=str,
        default='leduc-holdem',
        choices=[
            'blackjack',
            'leduc-holdem',
            'limit-holdem',
            'doudizhu',
            'mahjong',
            'no-limit-holdem',
            'uno', 
            'gin-rummy',
        ]
    )
    parser.add_argument(
        '--cuda',
        type=str,
        default='',
    )
    parser.add_argument(
        '--load_model',
        action='store_true',
        help='Load an existing model',
    )
    parser.add_argument(
        '--xpid',
        default='leduc_holdem',
        help='Experiment id (default: leduc_holdem)',
    )
    parser.add_argument(
        '--savedir',
        default='experiments/dmc_result',
        help='Root dir where experiment data will be saved',
    )
    parser.add_argument(
        '--save_interval',
        default=30,
        type=int,
        help='Time interval (in minutes) at which to save the model',
    )
    parser.add_argument(
        '--num_actor_devices',
        default=1,
        type=int,
        help='The number of devices used for simulation',
    )
    parser.add_argument(
        '--num_actors',
        default=5,
        type=int,
        help='The number of actors for each simulation device',
    )
    parser.add_argument(
        '--total_frames',
        default=1e11,
        type=int,
        help='The total number of frames to train for',
    )
    parser.add_argument(
        '--training_device',
        default=0,
        type=int,
        help='The index of the GPU used for training models',
    )

    args = parser.parse_args()

    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda
    train(args)

