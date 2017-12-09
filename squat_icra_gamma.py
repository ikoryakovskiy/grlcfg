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

    # for walking with yaml files
    _mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
    yaml.add_representer(collections.OrderedDict, dict_representer)
    yaml.add_constructor(_mapping_tag, dict_constructor)

    # Parameters
    runs = range(6, 11)
    power = [2]
    weight_nmpc = [0.001]
    weight_nmpc_aux = [1]
    weight_nmpc_qd = [1.0]
    weight_shaping = [0]
    sim_filtered = [0] # 0 - simulate normal, 1 - simulated filtered velocities
    gamma = [0.97, 0.00]
    model_types = [3] #, 4] #[0, 2, 3] # 0 -ideal, 1 - real, 2 - coulomb, 3 - torso torsion spring
    stiffness = [7] #, 30, 50, 70, 90] # [14, 18, 22, 26, 30] # turned out to be pretty good!
    
    # Spring at the hip
    options = []
    for r in itertools.product(power, weight_nmpc, weight_nmpc_aux, weight_nmpc_qd, weight_shaping, sim_filtered, gamma, model_types, stiffness, runs): options.append(r)
    options = [flatten(tupl) for tupl in options]

    configs = [
                "leo/icra/rbdl_nmpc_2dpg_ou_squat_fb_sl_vc_mef_spring.yaml",
              ]
    
    L1 = rl_run_param1(args, configs, options)
    
    '''
    # 2
    runs = [3, 0, 10, 2, 4]
    gamma = [0.00]
    model_types = [2] #[0, 2, 3] # 0 -ideal, 1 - real, 2 - coulomb, 3 - torso torsion spring
    options = []
    for r in itertools.product(power, weight_nmpc, weight_nmpc_aux, weight_nmpc_qd, weight_shaping, sim_filtered, gamma, model_types, runs): options.append(r)
    options = [flatten(tupl) for tupl in options]
    configs = [ "leo/icra/rbdl_nmpc_2dpg_ou_squat_fb_sl_vc_mef_all_019.yaml" ]
    L2 = rl_run_param2(args, configs, options)

    #3
    runs = [5, 3, 4, 7, 0]
    gamma = [0.97]
    model_types = [2] #[0, 2, 3] # 0 -ideal, 1 - real, 2 - coulomb, 3 - torso torsion spring
    options = []
    for r in itertools.product(power, weight_nmpc, weight_nmpc_aux, weight_nmpc_qd, weight_shaping, sim_filtered, gamma, model_types, runs): options.append(r)
    options = [flatten(tupl) for tupl in options]
    configs = [ "leo/icra/rbdl_nmpc_2dpg_ou_squat_fb_sl_vc_mef_all_019.yaml" ]
    L3 = rl_run_param2(args, configs, options)
    '''
    
    #L = L2 + L3
    do_multiprocessing_pool(args, L1)

######################################################################################
def rl_run_param1(args, list_of_cfgs, options):
    list_of_new_cfgs = []

    loc = "tmp"
    if not os.path.exists(loc):
        os.makedirs(loc)

    for cfg in list_of_cfgs:
        conf = read_cfg(cfg)

        # after reading cfg can do anything with the name
        fname, fext = os.path.splitext( cfg.replace("/", "_") )

        for o in options:
            str_o = "-".join(map(lambda x : "{:05d}".format(int(round(10000*x))), o[:-1]))  # last element in 'o' is reserved for mp
            str_o += "-mp{}".format(o[-1])
            print "Generating parameters: {}".format(str_o)

            # create local filename
            list_of_new_cfgs.append( "{}/{}-{}{}".format(loc, fname, str_o, fext) )

            # modify options
            conf['experiment']['steps'] = 1000000
            conf['experiment']['test_interval'] = 30
            conf['experiment']['environment']['task']['power'] = o[0]
            conf['experiment']['environment']['task']['weight_nmpc'] = o[1]
            conf['experiment']['environment']['task']['weight_nmpc_aux'] = o[2]
            conf['experiment']['environment']['task']['weight_nmpc_qd'] = o[3]
            conf['experiment']['environment']['task']['weight_shaping'] = o[4]

            conf['experiment']['environment']['sim_filtered'] = o[5]

            conf['experiment']['environment']['task']['gamma'] = o[6]

            if o[7] == 0:
                conf['experiment']['environment']['model']['dynamics']['file'] = "leo_vc/leo_fb_sl.lua"
            elif o[7] == 1:
                conf['experiment']['environment']['model']['dynamics']['file'] = "leo_vc/leo_fb_sl_real.lua"
            elif o[7] == 2:
                conf['experiment']['environment']['model']['dynamics']['file'] = "leo_vc/leo_fb_sl_coulomb.lua"
            elif o[7] == 3:
                conf['experiment']['environment']['model']['dynamics']['file'] = "leo_vc/leo_fb_sl_spring_{}.lua".format(o[8])
            elif o[7] == 4:
                conf['experiment']['environment']['model']['dynamics']['file'] = "leo_vc/leo_fb_sl_springB_{}.lua".format(o[8])
                
            conf['experiment']['output'] = "{}-{}".format(fname, str_o)
            if "exporter" in conf['experiment']['environment']:
              conf['experiment']['environment']['exporter']['file'] = "{}-{}".format(fname, str_o)
              conf['experiment']['environment']['exporter']['enabled'] = 0
            if "exporter" in conf['experiment']['agent']:
              conf['experiment']['agent']['exporter']['file'] = "{}-{}_elements".format(fname, str_o)
              conf['experiment']['agent']['exporter']['enabled'] = 0
              
              conf['experiment']['load_file'] = "gamma_dat_spring/{}-{}-run0".format(fname, str_o)
              
            conf = remove_viz(conf)
            write_cfg(list_of_new_cfgs[-1], conf)

    #print list_of_new_cfgs

    return list_of_new_cfgs

######################################################################################
def rl_run_param2(args, list_of_cfgs, options):
    list_of_new_cfgs = []

    loc = "tmp"
    if not os.path.exists(loc):
        os.makedirs(loc)

    for cfg in list_of_cfgs:
        conf = read_cfg(cfg)

        # after reading cfg can do anything with the name
        fname, fext = os.path.splitext( cfg.replace("/", "_") )

        for o in options:
            str_o = "-".join(map(lambda x : "{:05d}".format(int(round(10000*x))), o[:-1]))  # last element in 'o' is reserved for mp
            str_o += "-mp{}".format(o[-1])
            print "Generating parameters: {}".format(str_o)

            # create local filename
            list_of_new_cfgs.append( "{}/{}-{}{}".format(loc, fname, str_o, fext) )

            # modify options
            conf['experiment']['steps'] = 1000000
            conf['experiment']['test_interval'] = 30
            conf['experiment']['environment']['task']['power'] = o[0]
            conf['experiment']['environment']['task']['weight_nmpc'] = o[1]
            conf['experiment']['environment']['task']['weight_nmpc_aux'] = o[2]
            conf['experiment']['environment']['task']['weight_nmpc_qd'] = o[3]
            conf['experiment']['environment']['task']['weight_shaping'] = o[4]

            conf['experiment']['environment']['sim_filtered'] = o[5]

            conf['experiment']['environment']['task']['gamma'] = o[6]

            if o[7] == 0:
                conf['experiment']['environment']['model']['dynamics']['file'] = "leo_vc/leo_fb_sl.lua"
            elif o[7] == 1:
                conf['experiment']['environment']['model']['dynamics']['file'] = "leo_vc/leo_fb_sl_real.lua"
            else:
                conf['experiment']['environment']['model']['dynamics']['file'] = "leo_vc/leo_fb_sl_coulomb.lua"

            conf['experiment']['output'] = "{}-{}".format(fname, str_o)
            if "exporter" in conf['experiment']['environment']:
              conf['experiment']['environment']['exporter']['file'] = "{}-{}".format(fname, str_o)
              conf['experiment']['environment']['exporter']['enabled'] = 0
            if "exporter" in conf['experiment']['agent']:
              conf['experiment']['agent']['exporter']['file'] = "{}-{}_elements".format(fname, str_o)
              conf['experiment']['agent']['exporter']['enabled'] = 0
              
            conf['experiment']['load_file'] = "gamma_dat/{}-{}-run0".format(fname, str_o)

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

