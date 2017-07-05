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
      xs = data[:, 1:3]     # states
      tt = data[:, 3:4]     # time with restarts
      xc = data[:, 7:8]     # controls
      dd.append({'ts':ts, 'xs':xs, 'xc':xc})

      rl_provided = True
      fe = re.sub('\-learn-0.csv$', '', f) + '_elements-learn-0.csv'
      if not os.path.isfile(fe):
        fe = re.sub('\-test-0.csv$', '', f) + '_elements-test-0.csv'
        if not os.path.isfile(fe):
          rl_provided = False
          print ('RL trajectories are not provided')

      if rl_provided:
        hd_sz = get_header_size(fe)

        data = np.loadtxt(fe, skiprows=hd_sz, delimiter=',')
        te = data[:, 0]       # time
        xr = data[:, 2:3]     # rl controls
        eb = np.where(te == 0)[0] # starting times of rl
        eb = np.append(eb, len(te))

        mb = np.where(tt == 0)[0] # starting times of rl+nmpc
        mb = np.append(mb, len(tt))

        if eb.size != mb.size:
          pdb.set_trace()
        
        for k in range(0, eb[:-1].size):
          mbi0 = mb[k]
          mbi1 = mb[k+1]
          ebi0 = eb[k]
          ebi1 = eb[k+1]-1
          if mbi1-mbi0 != ebi1-ebi0:
            continue
          rl.append({'ts':ts[mbi0:mbi0+ebi1-ebi0], 'rl':xr[ebi0:ebi1,:]})

    plt.close('all')

    f, axarr = plt.subplots(3, sharex=True)
    for d in dd:
      axarr[0].plot(d['ts'], d['xs'][:, 0])
      axarr[1].plot(d['ts'], d['xs'][:, 1])
      axarr[2].step(d['ts'], d['xc'][:, 0], where='post')
      if rl_provided:
        for r in rl:
          axarr[2].step(r['ts'], r['rl'][:, 0], color='red', where='post')

    axarr[0].set_ylabel("Pos")
    axarr[0].grid(True)
    axarr[1].set_ylabel("Vel")
    axarr[1].grid(True)
    axarr[2].set_ylabel("Control")
    axarr[2].grid(True)

    fig = pylab.gcf()
    fig.canvas.set_window_title('car')

    plt.show()

if __name__ == "__main__":
    main()




