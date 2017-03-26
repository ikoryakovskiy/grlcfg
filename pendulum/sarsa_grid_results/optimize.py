from anneal import *
import numpy as np

class OptimizerSA(Annealer):
    """Test annealer"""
    dim = (125, 101, 3)
    click = [(-1,0), (1,0), (0,-1), (0,1)]
    prior = 0
    prior_delta = 0
    smoothness = 0
    smoothness_delta = 0
    updated_idx = 0
    updated_val = 0

    # pass extra data (the distance matrix) into the constructor
    def __init__(self, state, targets, tm, ts, tv2):
        self.targets, self.tm, self.ts, self.tv2 = targets, tm, ts, tv2
        self.Tmax = 2500.0     # Max (starting) temperature
        self.Tmin = 2.0     # Min (ending) temperature
        self.steps = 500     # Number of iterations
        self.updates = 1      # Number of updates (by default an update prints to stdout)
        super(OptimizerSA, self).__init__(state)  # important! 
        #(i,j,k) = self.idx2ijk(np.prod(self.dim)-1)
        #idx = self.ijk2idx(i,j,k)
        #print("{} {} {} {}".format(idx, i, j ,k))
        self.prior = self.calc_prior()
        print("Initial prior = {}".format(self.prior))
        self.smoothness = self.calc_smoothness()
        print("Initial smoothness = {}".format(self.smoothness))
        self.updated_val = state[self.updated_idx]


    def move(self, idx):
        """Swaps two cities in the route."""
        #i = np.random.randint(0, len(self.tm))
        self.updated_idx = idx
        self.updated_val = self.state[idx]
        self.state[idx] = np.random.normal(self.state[idx], self.ts[idx])
        
    def accepted(self):
        self.prior += self.prior_delta
        self.smoothness += self.smoothness_delta

    def energy(self):
        """Calculates the length of the route."""
        #prior = np.sum(np.divide(np.square(self.state - self.tm), self.tv2))
        old = self.f_prior(self.tm[self.updated_idx], self.updated_val)
        new = self.f_prior(self.tm[self.updated_idx], self.state[self.updated_idx])
        self.prior_delta = new - old        
        pr = self.prior_delta + self.prior
        #print("Prior difference {}".format(pr - self.calc_prior()))        
        
        (i,j,k) = self.idx2ijk(self.updated_idx)
        self.smoothness_delta = 0;
        for cl in self.click:
            ni = i+cl[0]
            nj = j+cl[1]
            if (ni >= 0 and ni < self.dim[0] and nj >= 0 and nj < self.dim[1]):
                idx = self.ijk2idx(ni,nj,k)
                old = self.f_smoothness(self.state[idx], self.updated_val)
                new = self.f_smoothness(self.state[idx], self.state[self.updated_idx])
                self.smoothness_delta += 2*(new-old)
        sm = self.smoothness_delta + self.smoothness
        #print("Smoothness difference {}".format(sm - self.calc_smoothness()))        
        
        e = pr + 1.0*sm
        return e
        
    def f_prior(self, a, b):
        return np.square(a-b)
        
    def calc_prior(self):
        prior = np.sum(self.f_prior(self.state, self.tm))
        return prior
        
    def f_smoothness(self, a, b):
        return np.minimum(abs(a-b), 20)

    def calc_smoothness(self):
        sm = 0
        for k in range(0, self.dim[2]): # for every action
            for i in range(0, self.dim[0]):
                for j in range(0, self.dim[1]):
                    for cl in self.click:
                        ni = i+cl[0]
                        nj = j+cl[1]
                        if (ni >= 0 and ni < self.dim[0] and nj >= 0 and nj < self.dim[1]):
                            v = self.state[self.ijk2idx(i,j,k)]
                            nv = self.state[self.ijk2idx(ni,nj,k)]
                            sm += self.f_smoothness(v, nv)
        return sm
                            
    def ijk2idx(self, i, j, k):
        return i + self.dim[0]*j + self.dim[0]*self.dim[1]*k
        
    def idx2ijk(self, li):
        k = li // (self.dim[0]*self.dim[1])
        j = (li % (self.dim[0]*self.dim[1])) // self.dim[0]
        i = (li % (self.dim[0]*self.dim[1])) % self.dim[0]
        return (i, j, k)
        
        
        
        