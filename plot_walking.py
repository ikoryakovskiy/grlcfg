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
    ljHipLeft, ljHipRight, ljKneeLeft, ljKneeRight, ljAnkleLeft, ljAnkleRight, ljShoulder, ljTorso = range(8)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='+')

    args = parser.parse_args()

    dd = []
    for i, f in enumerate(args.file):
      hd_sz = get_header_size(f)
      data = np.loadtxt(f, skiprows=hd_sz, delimiter=',')
      ts = data[:, 0]       # time
      xs = data[:, 1:17]    # states
      xn = data[:, 17:33]   # next states
      xc = data[:, 33:40]   # controls
      dd.append({'ts':ts, 'xs':xs, 'xn':xn, 'xc':xc})

    plt.close('all')

    bn = '' #os.path.splitext(basename(args.filename))[0]

    f, axarr = plt.subplots(8, sharex=True)
    for i in ELeoJoint:
      for d in dd:
        axarr[i.value].plot(d['ts'], d['xs'][:, i.value])
      #axarr[i.value].plot(ts, np.repeat(np.average(xs[:, i.value]), len(ts)))
      aname = str(i).rsplit('.', 1)[-1]
      axarr[i.value].set_ylabel(aname)
    axarr[0].set_title('pos-'+bn)
    fig = pylab.gcf()
    fig.canvas.set_window_title('pos-'+bn)

    f, axarr = plt.subplots(8, sharex=True)
    for i in ELeoJoint:
      for d in dd:
        axarr[i.value].plot(d['ts'], d['xs'][:, 8+i.value])
      aname = str(i).rsplit('.', 1)[-1]
      axarr[i.value].set_ylabel(aname)
    axarr[0].set_title('vel-'+bn)
    fig = pylab.gcf()
    fig.canvas.set_window_title('vel-'+bn)


    f, axarr = plt.subplots(7, sharex=True)
    for i in ELeoJoint:
      if i.value < 7:
        for d in dd:
          axarr[i.value].plot(d['ts'], d['xc'][:, i.value])
        aname = str(i).rsplit('.', 1)[-1]
        axarr[i.value].set_ylabel(aname)
    axarr[0].set_title('u-'+bn)
    fig = pylab.gcf()
    fig.canvas.set_window_title('u-'+bn)


    plt.show()

if __name__ == "__main__":
    main()




