import os
import csv


class Logger(object):
    """Logger saves the running results and helps make plots from the results"""

    def __init__(self, log_dir):
        """Initialize the labels, legend and paths of the plot and log file.

        Args:
            log_dir (str): The log directory for the log files
        """
        self.log_dir = log_dir

    def __enter__(self):
        self.txt_path = os.path.join(self.log_dir, 'log.txt')
        self.csv_path = os.path.join(self.log_dir, 'performance.csv')
        self.fig_path = os.path.join(self.log_dir, 'fig.png')

        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.txt_file = open(self.txt_path, 'w')
        self.csv_file = open(self.csv_path, 'w')
        fieldnames = ['episode', 'reward']
        self.writer = csv.DictWriter(self.csv_file, fieldnames=fieldnames)
        self.writer.writeheader()

        return self

    def log(self, text):
        """Write the text to log file then print it.
        Args:
            text(string): text to log
        """
        self.txt_file.write(text + '\n')
        self.txt_file.flush()
        print(text)

    def log_performance(self, episode, reward):
        """Log a point in the curve
        Args:
            episode (int): the episode of the current point
            reward (float): the reward of the current point
        """
        self.writer.writerow({'episode': episode, 'reward': reward})
        print('')
        self.log('----------------------------------------')
        self.log('  episode      |  ' + str(episode))
        self.log('  reward       |  ' + str(reward))
        self.log('----------------------------------------')

    def __exit__(self, type, value, traceback):
        if self.txt_path is not None:
            self.txt_file.close()
        if self.csv_path is not None:
            self.csv_file.close()
        print('\nLogs saved in', self.log_dir)
