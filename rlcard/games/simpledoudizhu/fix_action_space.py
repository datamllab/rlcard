

import os
import json
from collections import OrderedDict
import numpy as np
import threading
import collections

import rlcard

# Read required docs
ROOT_PATH = rlcard.__path__[0]

# a map of abstract action to its index and a list of abstract action
with open(os.path.join(ROOT_PATH, 'games/doudizhu/jsondata/action_space.json'), 'r') as file:
    ACTION_SPACE = json.load(file, object_pairs_hook=OrderedDict)
    ACTION_LIST = list(ACTION_SPACE.keys())

legal = '89TJQKA*'

for action in ACTION_LIST[:]:
    for card in action:
        if card not in legal:
            ACTION_LIST.remove(action)
            break
ACTION_SPACE = {}
index = 0
for action in ACTION_LIST:
    ACTION_SPACE[action] = index
    index += 1

print(ACTION_SPACE)
ACTION_SPACE = json.dumps(ACTION_SPACE)
with open(os.path.join(ROOT_PATH, 'games/simpledoudizhu/jsondata/action_space.json'), 'w') as file:
    file.write(ACTION_SPACE)