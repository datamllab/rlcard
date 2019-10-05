''' A toy example of playing against rule-based bot on Leduc Hold'em
'''

import rlcard

# Make environment and enable human mode
env = rlcard.make('uno')

# Set it to human mode
env.set_mode(human_mode=True)

print(">> UNO rule model V1")

# Reset environment
state = env.reset()

while True:
    action = input('>> You choose action (integer): ')
    while not action.isdigit() or int(action) not in state['legal_actions']:
        print('Action illegel...')
        action = input('>> Re-choose action (integer): ')
         
    state, _, _ = env.step(int(action))
