'''
A wrapper for running multiple environments with multiple processes
Reference: https://github.com/openai/baselines/blob/master/baselines/common/vec_env/subproc_vec_env.py
'''
import multiprocessing as mp

from rlcard.utils import reorganize

class VecEnv(object):
    '''
    The wrraper for a vector of environments. Here, only the
    basic interfaces of `env` are implemented. The vec environment
    does not support going backward in the game tree.
    '''

    def __init__(self, env_id, config):
        ''' Initialize the VecEnv class

        Args:
            env_id (string): The id of the environment, e.g., 'blackjack'
            config (dict): The same as the config in Env
        '''
        self.num = config['env_num']

        # For multiprocessing
        ctx = mp.get_context('spawn')
        self.remotes, self.work_remotes = zip(*[ctx.Pipe() for _ in range(self.num)])
        self.ps = [ctx.Process(target=worker, args=(work_remote, remote, env_id, config))
                    for (work_remote, remote) in zip(self.work_remotes, self.remotes)]
        for p in self.ps:
            p.daemon = True  # if the main process crashes, we should not cause things to hang
            p.start()
        for remote in self.work_remotes:
            remote.close()

        # A counter for the timesteps
        self.timestep = 0

        # Get the number of players/actions/state_shape in this game
        self.remotes[0].send(('info', None))
        self.player_num, self.action_num, self.state_shape = self.remotes[0].recv()

        self._seed(config['seed'])

    def set_agents(self, agents):
        self.agents = agents

    def run(self, is_training=False):
        ''' Run X complete games, where X is the number of environemnts.
            The input/output are similar to Env. The difference is that
            The transitions for each player are stacked over the environments
        '''
        trajectories = [[[] for _ in range(self.player_num)] for _ in range(self.num)]
        ready_trajectories = [None for _ in range(self.num)]
        active_remotes = [remote for remote in self.remotes]
        mapping = [i for i in range(self.num)]
        active_num = self.num

        # Reset
        states = []
        player_ids = []
        for state, player_id in send_command_to_all(active_remotes, ('reset', None)):
            states.append(state)
            player_ids.append(player_id)
        for i in range(active_num):
            trajectories[i][player_ids[i]].append(states[i])

        # Loop until all the environments are over
        while active_num > 0:
            # Agent playes
            # TODO: Currently we naively feed one obs to the agent. This can be improved via batch
            commands = []
            actions = []
            for i in range(active_num):
                opt = 'raw_step' if self.agents[player_ids[i]].use_raw else 'step'
                if not is_training:
                    action, _ = self.agents[player_ids[i]].eval_step(states[i])
                else:
                    action = self.agents[player_ids[i]].step(states[i])
                commands.append((opt, action))
                actions.append(action)

            # Environment steps
            next_states, next_player_ids, dones = [], [], []
            for next_state, next_player_id, done in send_commands_to_all(active_remotes, commands):
                next_states.append(next_state)
                next_player_ids.append(next_player_id)
                dones.append(done)

            # Save action
            for i in range(active_num):
                trajectories[i][player_ids[i]].append(actions[i])

            # Set the state and player
            states = next_states
            player_ids = next_player_ids

            # Save state
            finished = []
            for i in range(active_num):
                if dones[i]:
                    # Add a final state to all the players
                    for j in range(self.player_num):
                        active_remotes[i].send(('get_state', j))
                        trajectories[i][j].append(active_remotes[i].recv())

                    # Save the ready trajectories and mark them as finished
                    ready_trajectories[mapping[i]] = trajectories[i]
                    finished.append(i)
                else:
                    trajectories[i][player_ids[i]].append(states[i])


            # Pop out the finished ones
            trajectories = [trajectories[i] for i in range(active_num) if i not in finished]
            mapping = [mapping[i] for i in range(active_num) if i not in finished]
            active_remotes = [active_remotes[i] for i in range(active_num) if i not in finished]
            states = [states[i] for i in range(active_num) if i not in finished]
            player_ids = [player_ids[i] for i in range(active_num) if i not in finished]

            self.timestep += active_num
            active_num -= len(finished)

        # Payoffs
        payoffs = send_command_to_all(self.remotes, ('get_payoffs', None))

        for i in range(self.num):
            ready_trajectories[i] = reorganize(ready_trajectories[i], payoffs[i])

        trajectories = [[] for _ in range(self.player_num)]
        for trs in ready_trajectories:
            for i in range(self.player_num):
                trajectories[i].extend(trs[i])
        return trajectories, payoffs

    def _seed(self, seed=None):
        seeds = [None for _ in range(self.num)]
        if seed is not None:
            commands = [('seed', seed+i*1000) for i in range(self.num)]
            seeds = send_commands_to_all(self.remotes, commands)
        return seeds

def send_commands_to_all(remotes, commands):
    results = []
    for i, remote in enumerate(remotes):
        remote.send(commands[i])
    for remote in remotes:
        results.append(remote.recv())
    return results

def send_command_to_all(remotes, command):
    results = []
    for remote in remotes:
        remote.send(command)
    for remote in remotes:
        results.append(remote.recv())
    return results

def worker(remote, parent_remote, env_id, config):
    def step_env(env, action, use_raw):
        state, player_id = env.step(action, use_raw)
        done = env.is_over()
        return state, player_id, done
    from rlcard.envs.registration import registry
    env = registry.make(env_id, config)
    parent_remote.close()
    try:
        while True:
            cmd, data = remote.recv()
            if cmd == 'reset':
                remote.send(env.reset())
            elif cmd == 'step_raw':
                remote.send(step_env(env, data, True))
            elif cmd == 'step':
                remote.send(step_env(env, data, False))
            elif cmd == 'seed':
                remote.send(env._seed(data))
            elif cmd == 'get_state':
                remote.send(env.get_state(data))
            elif cmd == 'get_payoffs':
                remote.send(env.get_payoffs())
            elif cmd == 'info':
                remote.send((env.player_num, env.action_num, env.state_shape))
            elif cmd == 'close':
                remote.close()
                break
            else:
                raise NotImplementedError
    except KeyboardInterrupt:
        print('SubprocVecEnv worker: got KeyboardInterrupt')
    finally:
        del env
