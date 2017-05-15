"""RL data container."""

import os
import re
import sys
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
import argparse
from enum import Enum
import pylab
from os.path import basename

sys.path.append('/home/ivan/work/scripts/py')
from my_csv.utils import *

class ELeoJoint(Enum):
    Ankle, Knee, Hip, Arm = range(4)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='+')

    args = parser.parse_args()

    dd = []
    for i, f in enumerate(args.file):
      data = np.loadtxt(f, skiprows=0, delimiter=',')
      ts = data[:, 0]       # time
      xs = data[:, 1:]      # states

      # load controls
      f = f.replace('sd_', 'u_')
      data = np.loadtxt(f, skiprows=0, delimiter=',')
      xu = data[:, 1:]      # controls
      dd.append({'ts':ts, 'xs':xs, 'xu':xu})

    plt.close('all')

    f, axarr = plt.subplots(4, sharex=True)
    for i in ELeoJoint:
      for d in dd:
        axarr[i.value].plot(d['ts'], d['xs'][:, i.value])
      aname = str(i).rsplit('.', 1)[-1]
      axarr[i.value].set_ylabel(aname)
      axarr[i.value].grid(True)
    axarr[0].set_title('pos')
    fig = pylab.gcf()
    fig.canvas.set_window_title('pos')


    f, axarr = plt.subplots(4, sharex=True)
    for i in ELeoJoint:
      for d in dd:
        axarr[i.value].plot(d['ts'], d['xs'][:, 4+i.value])
      aname = str(i).rsplit('.', 1)[-1]
      axarr[i.value].set_ylabel(aname)
      axarr[i.value].grid(True)
    axarr[0].set_title('vel')
    fig = pylab.gcf()
    fig.canvas.set_window_title('vel')

    f, axarr = plt.subplots(4, sharex=True)
    for i in ELeoJoint:
      for d in dd:
        axarr[i.value].plot(d['ts'], d['xu'][:, i.value])
      aname = str(i).rsplit('.', 1)[-1]
      axarr[i.value].set_ylabel(aname)
      axarr[i.value].grid(True)
    axarr[0].set_title('u')
    fig = pylab.gcf()
    fig.canvas.set_window_title('u')

    plt.show()

if __name__ == "__main__":
    main()




