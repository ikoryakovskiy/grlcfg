from __future__ import division
import multiprocessing
import os
import os.path
import sys
import yaml, collections
import numpy as np
from time import sleep
import math
import argparse
import itertools
from random import shuffle
import random
from datetime import datetime

counter_lock = multiprocessing.Lock()
cores = 0;
random.seed(datetime.now())

def flatten(x):
    if isinstance(x, collections.Iterable):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]

def main():
    # parse arguments
    parser = argparse.ArgumentParser(description="Parser")
    parser.add_argument('-c', '--cores', type=int, help='specify maximum number of cores')
    args = parser.parse_args()
    if args.cores:
        args.cores = min(multiprocessing.cpu_count(), args.cores)
    else:
        args.cores = min(multiprocessing.cpu_count(), 32)
    print 'Using {} cores.'.format(args.cores)

    prepare_multiprocessing()
    # for walking with yaml files
    _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
    yaml.add_representer(collections.OrderedDict, dict_representer)
    yaml.add_constructor(_mapping_tag, dict_constructor)

    # Parameters
    runs    = range(10)
    sigma   = [0.01] #map(lambda x : 0.01*(1+x), range(0, 51, 10))
    theta   = [0.10] #map(lambda x : 0.01*(1+x), range(0, 51, 10))

    alpha   = map(lambda x : 0.00001*x, range(8, 10, 1)) + map(lambda x : 0.0001*x, range(1, 10, 1)) + map(lambda x : 0.001*x, range(1, 10, 1))
    #map(lambda x : 0.00001*x, range(1, 10, 2)) + map(lambda x : 0.00005*(1+x), range(1, 20, 2)) + map(lambda x : 0.001*(1+x), range(1, 5, 2))

    beta_v  = [0.05, 0.1, 0.5 ] # 0.005, 0.01, 
    x_beta_a  = [ 0.5, 0.2, 0.1] # 0.05 
    beta_va = []
    for x in x_beta_a:
      for y in beta_v:
        beta_va.append((y, x*y))

    gamma   = [ 0.97, 0.99 ]
    lm      = [ 0.65 ]

    #print (alpha)
    #return

    options = []
    for r in itertools.product(sigma, theta, alpha, beta_va, gamma, lm, runs): options.append(r)
    options = [flatten(tupl) for tupl in options]

    # Main
    L = rl_run_param(args, ["cfg/cart_pole/icra/rbdl_dpg_ou.yaml"], options)
    #print L

    shuffle(L)
    do_multiprocessing_pool(args, L)

######################################################################################
def rl_run_param(args, list_of_cfgs, options):
    list_of_new_cfgs = []

    loc = "tmp"
    if not os.path.exists(loc):
        os.makedirs(loc)

    for cfg in list_of_cfgs:
        conf = read_cfg(cfg)

        # after reading cfg can do anything with the name
        fname, fext = os.path.splitext( cfg.replace("/", "_") )

        for o in options:
            str_o = "-".join(map(lambda x : "{:06d}".format(int(round(100000*x))), o[:-1]))  # last element in 'o' is reserved for mp
            str_o += "-mp{}".format(o[-1])
            print "Generating parameters: {}".format(str_o)

            # create local filename
            list_of_new_cfgs.append( "{}/{}-{}{}".format(loc, fname, str_o, fext) )

            # modify options
            conf['experiment']['agent']['policy']['sigma']      = [ o[0] ]
            conf['experiment']['agent']['policy']['theta']      = [ o[1] ]
            conf['experiment']['agent']['predictor']['alpha']   = o[2]
            conf['experiment']['agent']['predictor']['beta_v']  = o[3]
            conf['experiment']['agent']['predictor']['beta_a']  = o[4]
            conf['experiment']['agent']['predictor']['gamma']   = o[5]
            conf['experiment']['agent']['predictor']['lambda']  = o[6]

            # rest
            conf['experiment']['output'] = "{}-{}".format(fname, str_o)
            if "exporter" in conf['experiment']['environment']:
              conf['experiment']['environment']['exporter']['file'] = "{}-{}".format(fname, str_o)

            conf = remove_viz(conf)
            write_cfg(list_of_new_cfgs[-1], conf)

    return list_of_new_cfgs

######################################################################################
def mp_run(cfg):
    # Multiple copies can be run on one computer at the same time, which results in the same seed for a random generator.
    # Thus we need to wait for a second or so between runs
    global cores
    with counter_lock:
        wait = cores.value*random.random()
    sleep(wait)
    print 'wait finished {0}'.format(wait)
    # Run the experiment
    code = os.system('./grld %s' % cfg)
    if not code == 0:
        errorString = "Exit code is '{0}' ({1})".format(code, cfg)
        print errorString
        f = open("bailing.out", "a")
        try:
            f.write(errorString + "\n")
        finally:
            f.close()

######################################################################################
def init(num):
    ''' store the counter for later use '''
    global cores
    cores = num

######################################################################################
def do_multiprocessing_pool(args, list_of_new_cfgs):
    """Do multiprocesing"""
    cores = multiprocessing.Value('i', args.cores)
    print 'cores {0}'.format(cores.value)
    pool = multiprocessing.Pool(args.cores, initializer = init, initargs = (cores,))
    pool.map(mp_run, list_of_new_cfgs)
    pool.close()
######################################################################################

def prepare_multiprocessing():
    # clean bailing.out file
    f = open("bailing.out", "w")
    f.close()
######################################################################################

def read_cfg(cfg):
    """Read configuration file"""
    # check if file exists  
    yfile = '../qt-build/cfg/%s' % cfg
    if os.path.isfile(yfile) == False:
        print 'File %s not found' % yfile
        sys.exit()

    # open configuration
    stream = file(yfile, 'r')
    conf = yaml.load(stream)
    stream.close()
    return conf
######################################################################################

def write_cfg(outCfg, conf):
    """Write configuration file"""
    # create local yaml configuration file
    outfile = file(outCfg, 'w')
    yaml.dump(conf, outfile)
    outfile.close()
######################################################################################

def remove_viz(conf):
    """Remove everything in conf related to visualization"""
    if "visualize" in conf['experiment']['environment']:
        conf['experiment']['environment']['visualize'] = 0
    if "target_env" in conf['experiment']['environment']:
    	if "visualize" in conf['experiment']['environment']['target_env']:
        	conf['experiment']['environment']['target_env']['visualize'] = 0
    if "visualizer" in conf:
            del conf["visualizer"]
    if "visualization" in conf:
            del conf["visualization"]
    if "visualization2" in conf:
            del conf["visualization2"]
    return conf
######################################################################################

def dict_representer(dumper, data):
  return dumper.represent_dict(data.iteritems())
######################################################################################
 
def dict_constructor(loader, node):
  return collections.OrderedDict(loader.construct_pairs(node))
######################################################################################

if __name__ == "__main__":
    main()

