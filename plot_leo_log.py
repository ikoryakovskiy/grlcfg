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
from scipy.signal import butter, lfilter
import math

sys.path.append('/home/ivan/work/scripts/py')
from my_csv.utils import *

class ELeoState(Enum):
    ID, Time, \
    hipleftAngle, hipleftSpeedRaw, hipleftSpeed, hipleftActuationAngle, hipleftActuationSpeed, hipleftActuationVoltage, hipleftActuationVoltageTempComp, hipleftActuationCurrent, \
    hiprightAngle, hiprightSpeedRaw, hiprightSpeed, hiprightActuationAngle, hiprightActuationSpeed, hiprightActuationVoltage, hiprightActuationVoltageTempComp, hiprightActuationCurrent, \
    kneeleftAngle, kneeleftSpeedRaw, kneeleftSpeed, kneeleftActuationAngle, kneeleftActuationSpeed, kneeleftActuationVoltage, kneeleftActuationVoltageTempComp, kneeleftActuationCurrent, \
    kneerightAngle, kneerightSpeedRaw, kneerightSpeed, kneerightActuationAngle, kneerightActuationSpeed, kneerightActuationVoltage, kneerightActuationVoltageTempComp, kneerightActuationCurrent, \
    ankleleftAngle, ankleleftSpeedRaw, ankleleftSpeed, ankleleftActuationAngle, ankleleftActuationSpeed, ankleleftActuationVoltage, ankleleftActuationVoltageTempComp, ankleleftActuationCurrent, \
    anklerightAngle, anklerightSpeedRaw, anklerightSpeed, anklerightActuationAngle, anklerightActuationSpeed, anklerightActuationVoltage, anklerightActuationVoltageTempComp, anklerightActuationCurrent, \
    shoulderAngle, shoulderSpeedRaw, shoulderSpeed, shoulderActuationAngle, shoulderActuationSpeed, shoulderActuationVoltage, shoulderActuationVoltageTempComp, shoulderActuationCurrent, \
    torsoAngle, torsoSpeedRaw, torsoSpeed, \
    RightToeSensor, RightToeContact, RightHeelSensor, RightHeelContact, LeftToeSensor, LeftToeContact, LeftHeelSensor, LeftHeelContact \
        = range(69)

    angles = [hipleftAngle, hiprightAngle, kneeleftAngle, kneerightAngle, ankleleftAngle, anklerightAngle, shoulderAngle, torsoAngle]
    sangles = ['hipleftAngle', 'hiprightAngle', 'kneeleftAngle', 'kneerightAngle', 'ankleleftAngle', 'anklerightAngle', 'shoulderAngle', 'torsoAngle']
    speeds = [hipleftSpeed, hiprightSpeed, kneeleftSpeed, kneerightSpeed, ankleleftSpeed, anklerightSpeed, shoulderSpeed, torsoSpeed]
    sspeeds = ['hipleftSpeed', 'hiprightSpeed', 'kneeleftSpeed', 'kneerightSpeed', 'ankleleftSpeed', 'anklerightSpeed', 'shoulderSpeed', 'torsoSpeed']
    speedsRaw = [hipleftSpeedRaw, hiprightSpeedRaw, kneeleftSpeedRaw, kneerightSpeedRaw, ankleleftSpeedRaw, anklerightSpeedRaw, shoulderSpeedRaw, torsoSpeedRaw]
    sspeedsRaw = ['hipleftSpeedRaw', 'hiprightSpeedRaw', 'kneeleftSpeedRaw', 'kneerightSpeedRaw', 'ankleleftSpeedRaw', 'anklerightSpeedRaw', 'shoulderSpeedRaw', 'torsoSpeedRaw']
    voltages = [hipleftActuationVoltage, hiprightActuationVoltage, kneeleftActuationVoltage, kneerightActuationVoltage, ankleleftActuationVoltage, anklerightActuationVoltage, shoulderActuationVoltage]
    svoltages = ['hipleftVoltage', 'hiprightVoltage', 'kneeleftVoltage', 'kneerightVoltage', 'ankleleftVoltage', 'anklerightVoltage', 'shoulderVoltage']
    voltagesC = [hipleftActuationVoltageTempComp, hiprightActuationVoltageTempComp, kneeleftActuationVoltageTempComp, kneerightActuationVoltageTempComp, ankleleftActuationVoltageTempComp, anklerightActuationVoltageTempComp, shoulderActuationVoltageTempComp]
    svoltagesC = ['hipleftVoltageC', 'hiprightVoltageC', 'kneeleftVoltageC', 'kneerightVoltageC', 'ankleleftVoltageC', 'anklerightVoltageC', 'shoulderVoltageC']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='+')
    args = parser.parse_args()

    for i, f in enumerate(args.file):
      data = np.loadtxt(f)
      ts  = data[:, 1]       # time
      xx  = data[:, ELeoState.angles.value]
      xd  = data[:, ELeoState.speedsRaw.value]
      xdf = data[:, ELeoState.speeds.value]
      xu  = data[:, ELeoState.voltages.value]
      xuc = data[:, ELeoState.voltagesC.value]
      dd = \
          {
            'ts'  :ts, 
            'xx'  :(xx,  ELeoState.sangles.value), 
            'xd'  :(xd,  ELeoState.sspeedsRaw.value), 
            'xdf' :(xdf, ELeoState.sspeeds.value),
            'xu'  :(xu,  ELeoState.svoltages.value), 
            'xuc' :(xuc, ELeoState.svoltagesC.value)
          }

    plt.close('all')

    cutoff = 5.0

    # Regular Butterworth filtering
    dd['bw1'] = (bw(dd['xd'][0], 1, cutoff), dd['xd'][1])
    dd['bw2'] = (bw(dd['xd'][0], 2, cutoff), dd['xd'][1])
    dd['bw3'] = (bw(dd['xd'][0], 3, cutoff), dd['xd'][1])

    # Tustin Butterworth filtering, as in Leo
    dd['tbw1'] = (bw_tustin(dd['xd'][0], 1, cutoff), dd['xd'][1])
    dd['tbw2'] = (bw_tustin(dd['xd'][0], 2, cutoff), dd['xd'][1])
    dd['tbw3'] = (bw_tustin(dd['xd'][0], 3, cutoff), dd['xd'][1])

    # effect of fitlering
    plot_separate(dd, ['xd', 'xdf', 'tbw2', 'tbw3'], [0, 2, 4, 6, 7])

    # effect of smoothing xd before calculating velocities
    ts = dd['ts']
    xx = dd['xx'][0]
    xx = bw(xx, 1, cutoff = 10)
    dts = np.diff(ts, axis=0)
    dxx = np.diff(xx, axis=0)
    xdm = np.divide( dxx, dts[:, np.newaxis] )

    xdm = np.append(xdm[np.newaxis, -1, :], xdm, 0)

    dd['xdm'] = (xdm, ELeoState.sspeeds.value)
    plot_separate(dd, ['xd', 'xdf', 'xdm'], [0, 2])

    plt.show()


def plot_separate(dd, seqs, subs = []):

    subs_num = []
    for seq in seqs:
      subs_num.append( dd[seq][0].shape[1] )
    subs_max = max(subs_num)
    
    if isinstance(subs, list) and len(subs) != 0:
        subs_max = min(subs_max, len(subs))
    elif not isinstance(subs, list):
        subs_max = 1

    f, axarr = plt.subplots(subs_max, sharex=True)

    def plotting(ax, x, y, ylabel):
        lh, = ax.plot(x, y)
        ls = seqs[s]
        ax.set_ylabel(ylabel)
        ax.grid(True)
        return lh, ls

    lh = [0]*len(seqs)
    ls = [0]*len(seqs)

    for s in range(len(seqs)):
      if isinstance(subs, list) and len(subs) != 0:
        i = 0
        for subi in subs:
          #print ( dd[seqs[s]][0][:, subi] )
          lh[s], ls[s] = plotting(axarr[i], dd['ts'], dd[seqs[s]][0][:, subi], dd[seqs[s]][1][subi])
          i = i + 1
        axarr[0].set_title(seqs)
      elif not isinstance(subs, list):
        i = subs
        lh[s], ls[s] = plotting(axarr, dd['ts'], dd[seqs[s]][0][:, i], dd[seqs[s]][1][i])
        axarr.set_title(seqs)
      else:
        for i in range(subs_num[s]):
          lh[s], ls[s] = plotting(axarr[i], dd['ts'], dd[seqs[s]][0][:, i], dd[seqs[s]][1][i])
        axarr[0].set_title(seqs)
    
    fig = pylab.gcf()
    fig.canvas.set_window_title(seqs)

    lgd = plt.legend(lh, ls)



def plot_joint(dd, s):
    subs = dd[0][s][0].shape[1]-3
    f, axarr = plt.subplots(subs, sharex=True)
    for d in dd:
      for i in range(subs):
        if i < 3:
          axarr[i].plot(d['ts'], d[s][0][:, 2*i], d['ts'], d[s][0][:, 2*i+1])
        else:
          axarr[i].plot(d['ts'], d[s][0][:, i+3])
        aname = d[s][1][i]
        axarr[i].set_ylabel(aname)
        axarr[i].grid(True)
    axarr[0].set_title(s)
    fig = pylab.gcf()
    fig.canvas.set_window_title(s)


def bw(signal, order, cutoff = 10.0):
  fs = 30.0
  #print(signal)
  B, A = butter(order, cutoff / (fs / 2), analog=False, btype='low') # 1st order Butterworth low-pass
  #B, A = [0.51, 0.51], [1, 0.045]
  #print (B, A)
  filtered_signal = lfilter(B, A, signal, axis=0)
  return filtered_signal

def bw_tustin(signal, order, cutoff = 10.0):
  
  fs = 30.0
  T = 2.0*math.pi*cutoff/fs;

  if order == 1:
    normalizeOutput = T + 2.0;
    A = [1.0, (T - 2.0)/normalizeOutput]
    B = [T/normalizeOutput, T/normalizeOutput]
  elif order == 2:
    normalizeOutput = T*T + 2.0*math.sqrt(2.0)*T + 4.0;
    A = [ 1.0, (2.0*T*T                   - 8.0)/normalizeOutput, (    T*T - 2.0*math.sqrt(2.0)*T + 4.0)/normalizeOutput ]
    B = [T*T/normalizeOutput, 2.0*T*T/normalizeOutput, T*T/normalizeOutput]
  elif order == 3:
    normalizeOutput = T*T*T + 4.0*T*T + 8.0*T + 8.0;
    A = [ 1.0, (3.0*T*T*T + 4.0*T*T - 8.0*T - 24.0)/normalizeOutput, (3.0*T*T*T - 4.0*T*T - 8.0*T + 24.0)/normalizeOutput, (    T*T*T - 4.0*T*T + 8.0*T -  8.0)/normalizeOutput ]
    B = [T*T*T/normalizeOutput, 3*T*T*T/normalizeOutput, 3*T*T*T/normalizeOutput, T*T*T/normalizeOutput]

  filtered_signal = lfilter(B, A, signal, axis=0)
  return filtered_signal

if __name__ == "__main__":
    main()




