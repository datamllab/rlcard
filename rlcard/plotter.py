import matplotlib
import matplotlib.pyplot as plt
import os

class Plotter(object):
    """
    Plotter saves the running results and helps make plots from the results
    """

    def __init__(self, xlabel = '', ylabel = '', legend = ''):
        """

        Args:

        """
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend = legend
        self.xs = []
        self.ys = []

    def add_point(self, x = None, y = None):
        """
        
        """
        if x != None and y != None:
            self.xs.append(x)
            self.ys.append(y)
        else:
            raise "Invalid input point"

    def make_plot(self, save_path = ''):
        """

        """
        fig, ax = plt.subplots()
        ax.plot(self.xs, self.ys, label=self.legend)
        ax.set(xlabel=self.xlabel, ylabel=self.ylabel)
        ax.legend()
        ax.grid()

        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        fig.savefig(save_path)