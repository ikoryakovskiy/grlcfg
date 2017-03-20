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
import random
from datetime import datetime

def main():
    # parse arguments
    parser = argparse.ArgumentParser(description="Parser")
    parser.add_argument('-s', '--size', type=int, help='Size of ensemble')
    args = parser.parse_args()
    
    random.seed(datetime.now())
    J_ = 0.000191
    m_ = 0.055
    l_ = 0.042
    b_ = 0.000003
    K_ = 0.0536
    R_ = 9.5

    f = open('params.txt', 'w')
    for i in range(0, args.size):
        J_ += 0.1*J_*random.uniform(-1.0, 1.0)
        m_ += 0.1*m_*random.uniform(-1.0, 1.0)
        l_ += 0.1*l_*random.uniform(-1.0, 1.0)
        b_ += 0.1*b_*random.uniform(-1.0, 1.0)
        K_ += 0.1*K_*random.uniform(-1.0, 1.0)
        R_ += 0.1*R_*random.uniform(-1.0, 1.0)
        f.write( "{} {} {} {} {} {}\n".format(J_, m_, l_, b_, K_, R_) )
    f.close()

if __name__ == "__main__":
    main()

