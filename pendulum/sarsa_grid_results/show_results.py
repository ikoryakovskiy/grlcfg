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

q0 = np.fromfile("policies/cfg_pendulum_sarsa_grid-it0-mp0-run0-_experiment_agent_policy_representation.dat")

csv_data = csv_read(["trajectories/pendulum_sarsa_grid_play-test-0.csv"])
tr = load_trajectories(csv_data)

for i in range(0, 3):
  show_grid_representation(q0[offset*i:offset*(i+1)], (0, 1), (125, 101, 1))
  plt.scatter(tr[:,0], tr[:,1], c='k', s=40, marker='+')
  plt.waitforbuttonpress()

p0 = calc_grid_policy(q0, (0, 1), (125, 101, 3))
show_grid_representation(p0, (0, 1), (125, 101, 1))
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
