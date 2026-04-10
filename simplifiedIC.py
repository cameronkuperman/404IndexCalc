import primesieve
import random
import numpy as np
from math import exp, sqrt, log
import math
class IndexCalc:
    def __init__(self, prime, g, ):
        self.p = prime
        self.g = g
    def computeFactorBase(self,p):
        b = int(exp(sqrt(log(p)*log(log(p)))))
        primeList = self.computeAllFactors(b)

        return (b, primeList)
     #tuple of the list and integer
    def computeAllFactors(self, b):
        return primesieve.generate_primes(b)
    def computeFactorBaseLogs(self, p ):
        rank= 0 
        matrix = np.zeros((len(pl), len(pl)))
        b, pl = self.computeFactorBase(p)
        while (rank<len(pl)):
            k = random.randint(self.p)
            if max(self.computeAllFactors(self.g**k % p)) > max(pl):
                continue
            matrix[rank]=factors of the b smooth # we get
            if np.linalg.matrix_rank(matrix)>rank:
                continue
        logsolutions = np.linalg.solve(matrix)

        return {pl[i]: logsolutions[i] for i in range(len(pl))}
        #hardest part 
        # essentially randomly sample ks mod p-1 and take to the power of k using a set / other datra structure to ensure onrepeats
        #do this len(b smoot factors) times andthen take detemrinient of this matrix to see if linearly independent like btw t
        #btw you have been building a matrix this whole time take determinent at the end to see if lin ind
        #or you can do like 5len(size) times and just think it will work out
        #row reduction seems ideal ok and 

    def createLogVector(self, num):
        self.computeAllFactors(num)

        return #dict of the actual factor base logs e.g. like factors etc... and their corresponding logs
    def solveForX(self, b):
        #get the linear combinartion of primes in there and return it
        return