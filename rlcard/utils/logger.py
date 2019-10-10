import matplotlib.pyplot as plt
import os

class Logger(object):
    ''' Logger saves the running results and helps make plots from the results
    '''

    def __init__(self, xlabel = '', ylabel = '', legend = '', log_path = None, csv_path = None):
        ''' Initialize the labels, legend and paths of the plot and log file.

        Args:
            xlabel (string): label of x axis of the plot
            ylabel (string): label of y axis of the plot
            legend (string): name of the curve
            log_path (string): where to store the log file
            csv_path (string): where to store the csv file

        Note:
            1. log_path must be provided to use the log() method. If the log file already exists, it will be deleted when Logger is initialized.
            2. If csv_path is provided, then one record will be write to the file everytime add_point() method is called.
        '''
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend = legend
        self.xs = []
        self.ys = []
        self.log_path = log_path
        self.csv_path = csv_path
        self.log_file = None
        self.csv_file = None
        if log_path != None:
            log_dir = os.path.dirname(log_path)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            self.log_file = open(log_path, 'w')
        if csv_path != None:
            csv_dir = os.path.dirname(csv_path)
            if not os.path.exists(csv_dir):
                os.makedirs(csv_dir)
            self.csv_file = open(csv_path, 'w')
            self.csv_file.write(xlabel+','+ylabel+'\n')
            self.csv_file.flush()

    def log(self, text):
        ''' Write the text to log file then print it.

        Args:
            text(string): text to log
        '''
        self.log_file.write(text+'\n')
        self.log_file.flush()
        print(text)

    def add_point(self, x = None, y = None):
        ''' Add a point to the plot

        Args:
            x (Number): x coordinate value
            y (Number): y coordinate value
        '''
        if x != None and y != None:
            self.xs.append(x)
            self.ys.append(y)
        else:
            raise ValueError('x and y should not be None.')

        # If csv_path is not None then write x and y to file
        if self.csv_path != None:
            self.csv_file.write(str(x)+','+str(y)+'\n')
            self.csv_file.flush()

    def make_plot(self, save_path = ''):
        ''' Make plot using all stored points

        Args:
            save_path (string): where to store the plot
        '''
        fig, ax = plt.subplots()
        ax.plot(self.xs, self.ys, label=self.legend)
        ax.set(xlabel=self.xlabel, ylabel=self.ylabel)
        ax.legend()
        ax.grid()

        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        fig.savefig(save_path)

    def close_file(self):
        ''' Close the created file objects
        '''
        if self.log_path != None:
            self.log_file.close()
        if self.csv_path != None:
            self.csv_file.close()
