# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 21:04:37 2017

@author: ivan
"""
import numpy as np

from ctypes import cdll
lib = cdll.LoadLibrary('./librepc.so')

class CMAES(object):
    def __init__(self):
        dim = (10, 10, 3)

        xlim = [-np.pi, 2*np.pi]
        ylim = [-12*np.pi, 12*np.pi]
        self.xoffset = xlim[0]
        self.yoffset = ylim[0]
        self.xsquash = 1.0 / (xlim[1] - xlim[0])
        self.ysquash = 1.0 / (ylim[1] - ylim[0])

        # centers are given for [0, 1] scale        
        cx = np.linspace(1.0/(2.0*dim[0]), 1.0 - 1.0/(2.0*dim[0]), dim[0])
        cy = np.linspace(1.0/(2.0*dim[1]), 1.0 - 1.0/(2.0*dim[1]), dim[1])
        cz = [0, 1, 2]
        sigma = np.maximum(1.0/np.power(dim[0], 1.5), 1.0/np.power(dim[1], 1.5))
        print(sigma)
        
        self.obj = lib.repc_new(dim, cx, cy, cz)

    def evaluate(self):
        lib.repc_evaluate(self.obj)
        