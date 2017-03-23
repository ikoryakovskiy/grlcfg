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

counter = None
counter_lock = multiprocessing.Lock()
proc_per_processor = 0;

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
    runs = 10
    #p = np.linspace(0.000, 0.010, 2)
    #p = 0.0001*np.logspace(0, 4, num=5, base=10.0)
    #p = np.append(0,p)
    p = [0.0, 0.1]
    #print(p)

    # Main
    rl_run_param(args, ["leo/squat_rl/rbdl_ac_tc_squat_fb_sl_fa.yaml"], range(runs), p)

######################################################################################
def rl_run_param(args, list_of_cfgs, runs, params):
    """Playing RL on a slope of x.xxx which were learnt for slope 0.004"""
    list_of_new_cfgs = []

    loc = "tmp"
    if not os.path.exists(loc):
        os.makedirs(loc)

    for cfg in list_of_cfgs:
        conf = read_cfg(cfg)

        # after reading cfg can do anything with the name
        fname, fext = os.path.splitext( cfg.replace("/", "_") )

        for p in params:
            str_param = int(round(10000*p))

            for run in runs:
                # create local filename
                list_of_new_cfgs.append( "{}/{}-{:05d}-mp{}{}".format(loc, fname, str_param, run, fext) )

                # modify options
                conf['experiment']['environment']['task']['weight2'] = 0.0001
                conf['experiment']['environment']['task']['weight2'] = float(p)
                conf['experiment']['output'] = "{}-{:05d}-mp{}".format(fname, str_param, run)
                if "exporter" in conf['experiment']['environment']:
                  conf['experiment']['environment']['exporter']['file'] = "{}-{:05d}-mp{}".format(fname, str_param, run)

                conf = remove_viz(conf)
                write_cfg(list_of_new_cfgs[-1], conf)

    #print list_of_new_cfgs

    do_multiprocessing_pool(args, list_of_new_cfgs)

######################################################################################
def mp_run(cfg):
    # Multiple copies can be run on one computer at the same time, which results in the same seed for a random generator.
    # Thus we need to wait for a second or so between runs
    global counter
    global proc_per_processor
    with counter_lock:
        wait = counter.value
        counter.value += 2
    # wait for the specified number of seconds
    #print 'floor {0}'.format(math.floor(wait / multiprocessing.cpu_count()))
    #wait = wait % multiprocessing.cpu_count() + (1.0/proc_per_processor.value) * math.floor(wait / multiprocessing.cpu_count())
    #print 'wait {0}'.format(wait)
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
    global proc_per_processor
    counter = cnt
    proc_per_processor = num

######################################################################################
def do_multiprocessing_pool(args, list_of_new_cfgs):
    """Do multiprocesing"""
    counter = multiprocessing.Value('i', 0)
    proc_per_processor = multiprocessing.Value('d', math.ceil(len(list_of_new_cfgs)/args.cores))
    print 'proc_per_processor {0}'.format(proc_per_processor.value)
    pool = multiprocessing.Pool(args.cores, initializer = init, initargs = (counter, proc_per_processor))
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

