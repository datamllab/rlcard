# Train agents on PettingZoo Environments

RLCard environments are also wrapped by [PettingZoo](https://www.pettingzoo.ml/) which
implements the Agent Environment Cycle (AEC) games model. PettingZoo is a library with 
diverse sets of multi-agent environments, developed with the goal of accelerating
research in Multi-Agent Reinforcement Learning (MARL).

## Setup

First install PettingZoo with classic games. 

```bash
pip3 install pettingzoo[classic]
```

PettingZoo has RLCard as a dependency, so if you already have RLCard installed in your 
Python environment, it may get replaced by the version required by PettingZoo, so
you may need to re-install it.

## Train Agents

Training scripts for DQN, NFSP, and DMC are provided. The following trains a DQN agent
on the Leduc Holdem environment:

```bash
python run_rl.py
```
