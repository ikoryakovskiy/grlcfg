# -*- coding: utf-8 -*-

""" Auto Encoder of Value Functions."""

from __future__ import division, print_function, absolute_import

#import tensorflow as tf
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import sys
import pickle


# local
from cmaes import *
from anneal import *
from extra import *
from optimize import *
sys.path.append('/home/ivan/work/scripts/py')
sys.path.append('/home/ikoryakovskiy/scripts/py')
from my_file.io import *
from my_plot.plot import *
from my_rl.gridworld import *
from my_csv.utils import *

# Import data
n = 2
size  = (125, 101, 3)
dsize = (5, 5, 3)

offset = size[0]*size[1]
num = np.prod(size)
dnum = np.prod(dsize)

train = np.zeros((n, num))
for i in range(0, n):
  train[i] = load_grid_representation("data/cfg_pendulum_sarsa_grid-{:03d}-mp0-run0-_experiment_agent_policy_representation.dat".format(i))
  #policy = calc_grid_policy(train[i], (0, 1), (125, 101, 3))
  #show_grid_representation(policy, (0, 1), (125, 101, 1))
  #plt.waitforbuttonpress()
  #show_grid_representation(train[i], (0, 1), (125, 101, 3))
  #plt.waitforbuttonpress()


tm = train.mean(0)
ts = train.std(0)
tv2 = 2*np.maximum( num * [0.0001], train.var(0))

save_grid_representation(tm, "policies/cfg_pendulum_sarsa_grid-it0-mp0-run0-_experiment_agent_policy_representation.dat")

cmaes = CMAES(size, dsize)

v = cmaes.optimize(tm)

with open('res.bin', 'wb') as file:
    file.write(v[0])

q_hat = cmaes.evaluate(v[0])

#q_hat = cmaes.evaluate(0.5*np.ones([dnum, 1]))

for i in range(0, 1):
  show_grid_representation(q_hat[offset*i:offset*(i+1)], (0, 1), (size[0], size[1], 1))
  plt.waitforbuttonpress()

a


csv_data = csv_read(["trajectories/pendulum_sarsa_grid_play-test-0.csv"])
tr = load_trajectories(csv_data)

targets = real_targets(tm, tr, 0.97)
#targets = np.zeros([1, 4])
#print("Targets ", targets)
#print(targets.shape[0])


#print(ts)
tsx = np.maximum(ts, 0.0000001)
init_state = tm#np.random.normal(tm, tsx)
#show_grid_representation(tm, (0, 1), (125, 101, 3))
#show_grid_representation(init_state, (0, 1), (125, 101, 3))
#plt.waitforbuttonpress()
print("Initial state", init_state)
print("Min of the state {}".format(np.amin(init_state)))

optimizer = OptimizerSA(init_state, targets, tm, ts, tv2)
state, e = optimizer.anneal()
print("Error {}".format(e))

show_grid_representation(state, (0, 1), (125, 101, 3))
plt.waitforbuttonpress()

save_grid_representation(state, "policies/cfg_pendulum_sarsa_grid-it1-mp0-run0-_experiment_agent_policy_representation.dat")

#for i in range(0, 3):
#  show_grid_representation(state[offset*i:offset*(i+1)], (0, 1), (125, 101, 1))
#  plt.waitforbuttonpress()



#policy = calc_grid_policy(tm, (0, 1), (125, 101, 3))
#show_grid_representation(policy, (0, 1), (125, 101, 1))
#plt.waitforbuttonpress()

#for i in range(0, 3):
#  show_grid_representation(tm[offset*i:offset*(i+1)], (0, 1), (125, 101, 1))
#  plt.waitforbuttonpress()
#  show_grid_representation(tv[offset*i:offset*(i+1)], (0, 1), (125, 101, 1))
#  plt.waitforbuttonpress()


  
  
