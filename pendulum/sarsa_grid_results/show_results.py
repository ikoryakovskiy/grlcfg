# -*- coding: utf-8 -*-

""" Auto Encoder of Value Functions."""

from __future__ import division, print_function, absolute_import

#import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import sys
import pickle

# local
from anneal import *
from extra import *
from optimize import *
sys.path.append('/home/ivan/work/scripts/py')
from my_file.io import *
from my_plot.plot import *
from my_rl.gridworld import *
from my_csv.utils import *

dim = (125, 101, 3)
offset = dim[0]*dim[1]

# Experimnet with 500 iterations
# Temperature        Energy    Accept   Improve     Elapsed   Remaining
#     0.00100        572.16     2.88%     1.81%     0:14:06     0:00:00

#with open("2017-03-27T22h48m49s_energy_610.201649024.state", 'rb') as fh:
#    state1 = pickle.load(fh)
    
#with open("2017-03-27T23h22m16s_energy_572.163801119.state", 'rb') as fh:       # no cond
 #   state1 = pickle.load(fh)

#with open("2017-03-27T23h04m28s_energy_572.832753648.state", 'rb') as fh:       # no cond
#    state2 = pickle.load(fh)

# Temperature        Energy    Accept   Improve     Elapsed   Remaining
#     0.00100        548.64     2.43%     1.39%     0:29:59     0:00:00
#with open("2017-03-28T08h58m54s_energy_548.635027241.state", 'rb') as fh:       # no cond
#    state1 = pickle.load(fh)

#with open("2017-03-28T10h06m24s_energy_548.773715401.state", 'rb') as fh:       # no cond
#    state2 = pickle.load(fh)

# Temperature        Energy    Accept   Improve     Elapsed   Remaining
#     0.00001        527.93     0.46%     0.41%     0:28:08     0:00:00
#with open("2017-03-28T11h51m57s_energy_527.65603926.state", 'rb') as fh:       # no cond
#    state1 = pickle.load(fh)

#with open("2017-03-28T12h31m50s_energy_527.933218316.state", 'rb') as fh:       # no cond
#    state2 = pickle.load(fh)


#with open("2017-03-28T15h59m55s_energy_2959.65632801.state", 'rb') as fh:       # no cond
#    state1 = pickle.load(fh)

#with open("2017-03-28T16h59m08s_energy_2968.9286122.state", 'rb') as fh:       # no cond
#    state2 = pickle.load(fh)


with open("2017-03-28T19h12m30s_energy_518.56423151.state", 'rb') as fh:       # no cond
    state1 = pickle.load(fh)

with open("2017-03-28T20h19m45s_energy_516.746097874.state", 'rb') as fh:       # no cond
    state2 = pickle.load(fh)

csv_data = csv_read(["trajectories/pendulum_sarsa_grid_play-test-0.csv"])
tr = load_trajectories(csv_data)
#targets = real_targets(tm, tr, 0.97)

policy1 = calc_grid_policy(state1, (0, 1), (125, 101, 3))
show_grid_representation(policy1, (0, 1), (125, 101, 1))
plt.scatter(tr[:,0], tr[:,1], c='w', s=40, marker='+')
plt.waitforbuttonpress()

policy2 = calc_grid_policy(state2, (0, 1), (125, 101, 3))
show_grid_representation(policy2, (0, 1), (125, 101, 1))
plt.scatter(tr[:,0], tr[:,1], c='w', s=40, marker='+')
plt.waitforbuttonpress()

policy = policy1-policy2
show_grid_representation(policy, (0, 1), (125, 101, 1))
plt.scatter(tr[:,0], tr[:,1], c='w', s=40, marker='+')
plt.waitforbuttonpress() 


'''
state = state1-state2

show_grid_representation(state, (0, 1), (125, 101, 3))
plt.scatter(tr[:,0], tr[:,1], c='k', s=40, marker='+')
plt.waitforbuttonpress()
'''

'''
show_grid_representation(state2, (0, 1), (125, 101, 3))
plt.scatter(tr[:,0], tr[:,1], c='k', s=40, marker='+')
plt.waitforbuttonpress()

for i in range(0, 3):
    show_grid_representation(state[offset*i:offset*(i+1)], (0, 1), (125, 101, 1))
    plt.scatter(tr[:,0], tr[:,1], c='k', s=40, marker='+')
    plt.waitforbuttonpress()
'''
