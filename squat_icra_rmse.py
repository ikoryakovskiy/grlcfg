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
import glob
import pdb

counter_lock = multiprocessing.Lock()
cores = 0
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

    configs = [
                "leo/icra/rbdl_nmpc_simulate_ideal.yaml",
                "leo/icra/rbdl_nmpc_simulate_coulomb.yaml",
              ]

    L = rl_run_param1(args, configs)

    do_multiprocessing_pool(args, L)

######################################################################################
def rl_run_param1(args, list_of_cfgs):
    list_of_new_cfgs = []

    loc = "tmp"
    if not os.path.exists(loc):
        os.makedirs(loc)

    in_csvs = glob.glob('../qt-build/cfg/data/icra2018_in_rmse/*.csv')
    
    for csv in in_csvs:
      print(csv)
      
      for cfg in list_of_cfgs:
          conf = read_cfg(cfg)

          # after reading cfg can do anything with the name
          _, fname_yaml = os.path.split( cfg )
          fpath_csv, fullname_csv = os.path.split(csv)
          fname_csv, fext_csv = os.path.splitext( fullname_csv )

          if 'ideal' in fname_yaml:
            model = 'ideal'
          else:
            model = 'coulomb'

          # create local filename
          list_of_new_cfgs.append( "{}/{}-{}{}".format(loc, fname_csv, model, '.yaml') )

          conf['experiment']['environment']['environment']['importer']['file'] = "{}/{}".format(fpath_csv, fname_csv)
          conf['experiment']['output'] = "{}-{}".format(fname_csv, model)
          if "exporter" in conf['experiment']['environment']:
            conf['experiment']['environment']['exporter']['file'] = "{}-{}".format(fname_csv, model)

          conf = remove_viz(conf)
          write_cfg(list_of_new_cfgs[-1], conf)

      #print list_of_new_cfgs

    return list_of_new_cfgs

######################################################################################
def mp_run(cfg):
    # Multiple copies can be run on one computer at the same time, which results in the same seed for a random generator.
    # Thus we need to wait for a second or so between runs
    global counter
    global cores
    with counter_lock:
        wait = counter.value
        counter.value += 2
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
def init(cnt, num):
    ''' store the counter for later use '''
    global counter
    global cores
    counter = cnt
    cores = num

######################################################################################
def do_multiprocessing_pool(args, list_of_new_cfgs):
    """Do multiprocesing"""
    counter = multiprocessing.Value('i', 0)
    cores = multiprocessing.Value('i', args.cores)
    print 'cores {0}'.format(cores.value)
    pool = multiprocessing.Pool(args.cores, initializer = init, initargs = (counter, cores))
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

