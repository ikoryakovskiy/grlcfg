# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 21:04:37 2017

@author: ivan
"""
import numpy as np
import ctypes
from ctypes import cdll
import itertools

lrepc = cdll.LoadLibrary('./librepc.so')

class CMAES(object):
    def __init__(self):
        dsize = (2, 2, 3)
        dnum = np.prod(dsize)

        xlim = [-np.pi, 2*np.pi]
        ylim = [-12*np.pi, 12*np.pi]
        self.xoffset = xlim[0]
        self.yoffset = ylim[0]
        self.xsquash = 1.0 / (xlim[1] - xlim[0])
        self.ysquash = 1.0 / (ylim[1] - ylim[0])

        # centers are given for [0, 1] scale        
        cx = np.linspace(1.0/(2.0*dsize[0]), 1.0 - 1.0/(2.0*dsize[0]), dsize[0])
        cy = np.linspace(1.0/(2.0*dsize[1]), 1.0 - 1.0/(2.0*dsize[1]), dsize[1])
        cz = np.array([0, 1, 2])
        locx = []
        locy = []
        locz = []
        for r in itertools.product(cz, cy, cx): 
            locx.append(r[2])
            locy.append(r[1])
            locz.append(r[0])
        locx = np.asarray(locx, dtype='float64')
        locy = np.asarray(locy, dtype='float64')
        locz = np.asarray(locz, dtype='float64')
        
        sigma = np.maximum(1.0/np.power(dsize[0], 1.5), 1.0/np.power(dsize[1], 1.5))
        print(sigma)

        #print (locz)
        clocx = locx.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        clocy = locy.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        clocz = locz.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        #print (np.ctypeslib.as_array((ctypes.c_double * dnum).from_address(ctypes.addressof(clocz.contents))))
        self.obj = lrepc.rbf_new(dnum, clocx, clocy, clocz, ctypes.c_double(sigma))

    def evaluate(self):
        lrepc.rbf_evaluate(self.obj)
        