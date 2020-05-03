import subprocess
import sys

reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

if 'tensorflow' in installed_packages:
    from rlcard.agents.deep_cfr_agent import DeepCFR
    from rlcard.agents.dqn_agent import DQNAgent
    from rlcard.agents.nfsp_agent import NFSPAgent
if 'torch' in installed_packages:
    from rlcard.agents.dqn_agent_pytorch import DQNAgent as DQNAgentPytorch
    from rlcard.agents.nfsp_agent_pytorch import NFSPAgent as NFSPAgentPytorch

from rlcard.agents.cfr_agent import CFRAgent
from rlcard.agents.holdem_nl_human_agent import HumanAgent as NolimitholdemHumanAgent
from rlcard.agents.leduc_holdem_human_agent import HumanAgent as LeducholdemHumanAgent
from rlcard.agents.random_agent import RandomAgent
from rlcard.agents.uno_human_agent import HumanAgent as UnoHumanAgent
