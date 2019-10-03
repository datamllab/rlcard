''' A toy example of playing against pretrianed AI on Leduc Hold'em
'''

import rlcard

# Make environment and enable human mode
env = rlcard.make('leduc-holdem')

# Set it to human mode
env.set_mode(human_mode=True)

# Reset environment
env.reset()

while True:
    action = int(input(">> You choose action (integer): "))
    env.step(action)
