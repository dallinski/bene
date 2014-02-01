import optparse
import sys

import matplotlib
matplotlib.use('Agg')
from pylab import *

# Class that parses a file and plots several graphs
class Plotter:
    def __init__(self):
        self.x = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.98]
        self.y = []
        self.all = []
        for load in self.x:
            vals = []
            filename = "./delay_output/%s.txt" % load
            f = open(filename)
            for line in f.readlines():
                delay = float(line)
                vals.append(delay)
                self.all.append(delay)
            self.y.append(vals)
        self.averages = []
        for array in self.y:
            self.averages.append(average(array))

    def barPlot(self):
        """ Create a graph that includes an equation plot and a boxplot. """
        clf()
        # plot the equation
        x = np.arange(0.01,0.99,0.01)
        plot(x,8000*x/(2000000*(1-x)), label='Theoretical')
        # plot the boxplot
        boxplot(self.y,positions=self.x,widths=0.05)
        legend(loc=2)
        xlim(0,1)
        xlabel('Utilization')
        ylabel('Queueing Delay')
        savefig('bar.png')

    def averagePlot(self):
        """ Create a graph that includes a line plot of averages and the theoretical line plot"""
        clf()
        # plot the averages
        plot(self.x,self.averages, label='Simulation Averages')
        # plot the equation
        x = np.arange(0.01,0.99,0.01)
        plot(x,8000*x/(2000000*(1-x)), label='Theoretical')
        legend(loc=2)
        xlim(0,1)
        xlabel('Utilization')
        ylabel('Queueing Delay')
        savefig('average.png')


if __name__ == '__main__':
    p = Plotter()
    p.barPlot()
    p.averagePlot()
