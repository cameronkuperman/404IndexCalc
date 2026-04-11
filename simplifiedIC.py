import primesieve
import random
import numpy as np
from math import exp, sqrt, log
import math
import sympy
class IndexCalc:
    def __init__(self, prime, g, ):
        self.p = prime
        self.g = g
    def computeFactorBase(self,p):
        b = int(exp(sqrt(log(p)*log(log(p)))))
        primeList = self.computeAllFactors(b)

        return (b, primeList)
     #tuple of the list and integer
    def factor(self, num):
        return sympy.factorint(num)
    def computeAllFactors(self, b):
        return primesieve.primes(b)
    def computeFactorBaseLogs(self, p ):
        rank= 0 
        matrix = np.zeros((len(pl), len(pl)))
        b, pl = self.computeFactorBase(p)
        while (rank<len(pl)):
            k = random.randint(self.p)
            num = self.g**k % p 
            if max(self.computeAllFactors(num)) > max(pl):
                continue
            matrix[rank]=self.createLogVector(num)
            if np.linalg.matrix_rank(matrix)>rank:
                rank+=1
                continue
            matrix[rank]= np.zeros(len(pl))
            
        logsolutions = np.linalg.solve(matrix)

        return {pl[i]: logsolutions[i] for i in range(len(pl))}


    def createLogVector(self, num, baseList):
        dc =  self.factor(num)
        

        lst2 = [dc.get(k,0) for k in sorted(baseList)]

        return lst2


            

        return #dict of the actual factor base logs e.g. like factors etc... and their corresponding logs
    def solveForX(self, num ):
        pfactordict = self.computeFactorBaseLogs(self.p)
        factors = sympy.factorint(num % self.p)
        x=0
        for key in factors:
            x+=pfactordict[key]*factors[key]


        return x
