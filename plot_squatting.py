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
from os.path import basename, isfile
import pdb
from butterworth import bw_tustin

sys.path.append('/home/ivan/work/scripts/py')
from my_csv.utils import *

class ELeoJoint(Enum):
    Ankle, Knee, Hip, Arm = range(4)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='+')

    args = parser.parse_args()

    dd = []
    rl = []
    for i, f in enumerate(args.file):
      hd_sz = get_header_size(f)
      data = np.loadtxt(f, skiprows=hd_sz, delimiter=',')
      ts = data[:, 0]       # time
      xs = data[:, 1:9]     # states
      tp = data[:, 10:11]   # temperature
      rz = data[:, 20:21]   # RootZ
      ss = data[:, 32:33]   # sma state
      xc = data[:, 44:48]   # controls
      dd.append({'ts':ts, 'xs':xs, 'xc':xc, 'ss':ss, 'tp':tp})

      rl_provided = True
      fe = re.sub('\-learn-0.csv$', '', f) + '_elements-all-1.csv'
      if not os.path.isfile(fe):
        fe = re.sub('\_play-learn-0.csv$', '', f) + '_elements_play-all-1.csv'
        if not os.path.isfile(fe):
          rl_provided = False
          print ('RL trajectories are not provided')

      if rl_provided:
        hd_sz = get_header_size(fe)

        data = np.loadtxt(fe, skiprows=hd_sz, delimiter=',')
        te = data[:, 0]
        xr = data[:, 5:9]     # rl controls
        eb = np.where(te == 0)[0] # starting times of rl+nmpc

        ss45 = np.diff(np.in1d(ss, [4, 5])) # learn or test episodes
        mb = np.where(ss45)[0] + 1  # begin and end indexes of learning
        mb = mb[::2] # begin only


        if eb.size != mb.size:
          pdb.set_trace()
      
        for k in range(0, eb[:-1].size):
          mbi0 = mb[k]
          mbi1 = mb[k+1]
          ebi0 = eb[k]
          ebi1 = eb[k+1]
          if mbi1-mbi0 < ebi1-ebi0:
            pdb.set_trace()
          rl.append({'ts':ts[mbi0:mbi0+ebi1-ebi0], 'rl':xr[ebi0:ebi1,:]})

    plt.close('all')

    f, axarr = plt.subplots(6, sharex=True)
    for i in ELeoJoint:
      for d in dd:
        axarr[i.value].plot(d['ts'], d['xs'][:, i.value])
      aname = str(i).rsplit('.', 1)[-1]
      axarr[i.value].set_ylabel(aname)
      axarr[i.value].grid(True)
    axarr[4].plot(d['ts'], rz)
    axarr[4].set_ylabel('Height')
    axarr[4].grid(True)
    axarr[5].plot(d['ts'], d['ss'])
    axarr[5].set_ylabel('SMA State')
    axarr[5].grid(True)
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


    f, axarr = plt.subplots(5, sharex=True)
    for i in ELeoJoint:
      for d in dd:
        axarr[i.value].plot(d['ts'], d['xc'][:, i.value])
        #filtered = bw_tustin(d['xc'][:, i.value], order = 2, cutoff = 3.0, fs = 1/0.03)
        #axarr[i.value].plot(d['ts'], filtered, color='green')
        if rl_provided:
          for r in rl:
            axarr[i.value].plot(r['ts'], r['rl'][:, i.value], color='red')
      aname = str(i).rsplit('.', 1)[-1]
      axarr[i.value].set_ylabel(aname)
      axarr[i.value].grid(True)
    axarr[4].plot(d['ts'], d['tp'])
    axarr[4].set_ylabel('Temperature')
    axarr[4].grid(True)
    axarr[0].set_title('u')
    fig = pylab.gcf()
    fig.canvas.set_window_title('u')


    plt.show()

if __name__ == "__main__":
    main()




