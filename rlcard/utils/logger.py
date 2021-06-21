import os
import csv

class Logger(object):
    ''' Logger saves the running results and helps make plots from the results
    '''

    def __init__(self, log_dir):
        ''' Initialize the labels, legend and paths of the plot and log file.

        Args:
            log_path (str): The path the log files
        '''
        self.log_dir = log_dir

    def __enter__(self):
        self.txt_path = os.path.join(self.log_dir, 'log.txt')
        self.csv_path = os.path.join(self.log_dir, 'performance.csv')
        self.fig_path = os.path.join(self.log_dir, 'fig.png')

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.txt_file = open(self.txt_path, 'w')
        self.csv_file = open(self.csv_path, 'w')
        fieldnames = ['timestep', 'reward']
        self.writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
        self.writer.writeheader()

        return self

    def log(self, text):
        ''' Write the text to log file then print it.
        Args:
            text(string): text to log
        '''
        self.txt_file.write(text+'\n')
        self.txt_file.flush()
        print(text)

    def log_performance(self, timestep, reward):
        ''' Log a point in the curve
        Args:
            timestep (int): the timestep of the current point
            reward (float): the reward of the current point
        '''
        self.writer.writerow({'timestep': timestep, 'reward': reward})
        print('')
        self.log('----------------------------------------')
        self.log('  timestep     |  ' + str(timestep))
        self.log('  reward       |  ' + str(reward))
        self.log('----------------------------------------')

    def __exit__(self, type, value, traceback):
        if self.txt_path is not None:
            self.txt_file.close()
        if self.csv_path is not None:
            self.csv_file.close()
        print('\nLogs saved in', self.log_dir)

def plot_curve(csv_path, save_path, algorithm):
    ''' Read data from csv file and plot the results
    '''
    import matplotlib.pyplot as plt
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile)
        xs = []
        ys = []
        for row in reader:
            xs.append(int(row['timestep']))
            ys.append(float(row['reward']))
        fig, ax = plt.subplots()
        ax.plot(xs, ys, label=algorithm)
        ax.set(xlabel='timestep', ylabel='reward')
        ax.legend()
        ax.grid()

        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        fig.savefig(save_path)
