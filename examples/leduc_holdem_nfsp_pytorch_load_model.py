''' An example of loading pre-trained NFSP model on Leduc Holdem
'''
import os
import torch

import rlcard
from rlcard.agents.nfsp_agent_pytorch import NFSPAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.utils.utils import set_global_seed, tournament

# Make environment
env = rlcard.make('leduc-holdem')

# Set a global seed
set_global_seed(0)

# Load pretrained model
nfsp_agents = []
for i in range(env.player_num):
    agent = NFSPAgent(scope='nfsp' + str(i),
                      action_num=env.action_num,
                      state_shape=env.state_shape,
                      hidden_layers_sizes=[128,128],
                      q_mlp_layers=[128,128],
                      device=torch.device('cpu'))
    nfsp_agents.append(agent)

# We have a pretrained model here. Change the path for your model.
check_point_path = os.path.join(rlcard.__path__[0], 'models/pretrained/leduc_holdem_nfsp_pytorch/model.pth')
checkpoint = torch.load(check_point_path)
for agent in nfsp_agents:
    agent.load(checkpoint)

# Evaluate the performance. Play with random agents.
evaluate_num = 10000
random_agent = RandomAgent(env.action_num)
env.set_agents([nfsp_agents[0], random_agent])
reward = tournament(env, evaluate_num)[0]
print('Average reward against random agent: ', reward)

