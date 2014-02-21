import optparse
import sys

import matplotlib
matplotlib.use('Agg')
from pylab import *

# Class that parses a file and plots several graphs
class Plotter:
    def __init__(self):
        self.window_sizes = []
        self.averages = []
        self.throughputs = []
        filename = "./experimentresults.txt"
        f = open(filename)
        linecount = 0
        for line in f.readlines():
            if linecount == 2: # "Window Size, Loss Rate"
                self.window_sizes.append(line.split(" ")[2])
            elif linecount == 4: # "Average queueing delay"
                self.averages.append(line.split(" ")[4].strip())
            elif linecount == 5: # "Throughput"
                self.throughputs.append(line.split(" ")[2].strip())
            elif linecount == 7: # "File transfer correct!"
                if line != "File transfer correct!\n":
                    print "Diffs did not match up!"
            linecount = (linecount + 1) % 9

    def delayPlot(self):
        """A line plot of average queueing delay"""
        clf()
        # plot the averages
        plot(self.window_sizes,self.averages, label='Average Queueing Delay')
        legend(loc=2)
        xlabel('Window Size (bytes)')
        ylabel('Queueing Delay (seconds)')
        savefig('delay.png')

    def throughputPlot(self):
        """A line plot of throughput"""
        clf()
        # plot the averages
        plot(self.window_sizes,self.throughputs, label='Throughput')
        legend(loc=2)
        xlabel('Window Size (bytes)')
        ylabel('Throughput (bits/second)')
        savefig('throughputs.png')


if __name__ == '__main__':
    p = Plotter()
    p.delayPlot()
    p.throughputPlot()
