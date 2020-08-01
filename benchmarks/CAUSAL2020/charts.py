import numpy as np
import matplotlib.pyplot as plt
import csv
import math

log_scale = False

data = {}

with open('benchmark-forking.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';')

    types = []
    modes = []

    x = {}
    y_mean = {}
    y_dev = {}

    for row in spamreader:
        type = row[0]
        mode = row[1]

        if type not in types:
            types.append(type)
        if mode not in modes:
            modes.append(mode)

        if type not in x:
            x[type] = {}
            y_mean[type] = {}
            y_dev[type] = {}

        if mode not in x[type]:
            x[type][mode] = []
            y_mean[type][mode] = []
            y_dev[type][mode] = []

        depth = int(row[2])

        values = []
        for i in range(3, len(row)-1):
            if log_scale is True:
                values.append(math.log(float(row[i]) * 1000))
            else:
                values.append(float(row[i]) * 1000)

        mean = np.average(values)
        dev = np.std(values)

        x[type][mode].append(depth)
        y_mean[type][mode].append(mean)
        y_dev[type][mode].append(dev)

    for type in types:
        for mode in modes:
            xx = x[type][mode]
            yy_mean = y_mean[type][mode]
            yy_dev = y_dev[type][mode]

            plt.errorbar(xx, yy_mean, yerr=yy_dev, label=type+" "+mode, elinewidth=1, capsize=0)

    plt.legend(loc='upper left')
    plt.show()