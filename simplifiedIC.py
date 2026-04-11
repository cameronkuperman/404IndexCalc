import primesieve
import random

from math import exp, sqrt, log
import math
import sympy
from itertools import combinations
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
    

    def find_invertible_subsystem(self,sample_vectors, sample_ks, pl, p):
        m = len(pl)
        mod = p - 1

        for idxs in combinations(range(len(sample_vectors)), m):
            rows = [sample_vectors[i] for i in idxs]
            rhs = [sample_ks[i] for i in idxs]

            A = sympy.Matrix(rows)
            det = A.det()

            if sympy.gcd(det, mod) == 1:
                b = sympy.Matrix(rhs)
                return A, b

        return None, None

    def computeFactorBaseLogs(self, p ):
        b, pl = self.computeFactorBase(p)
        sample_vectors = []
        vec = []
        
        while True:
            for i in range(2 * len(pl)):
                k = random.randint(1,p-2)
                num = self.g**k % p 
                
                if max(self.factor(num)) > max(pl):
                    i-=1
                    continue
                _, bl = self.computeFactorBase(p)
                sample_vectors.append(self.createLogVector(num,bl ))
                vec.append(k)
            
            A,b = self.find_invertible_subsystem(sample_vectors, vec , pl, p)
            if A is None:
                vec = []
                sample_vectors = []
                continue
            else:
                inverse = A.inv_mod(p-1)

                break
        
        logsolutions = inverse* b

        return {pl[i]: logsolutions[i] for i in range(len(pl))}


    def createLogVector(self, num, baseList):
        dc =  self.factor(num)
        

        lst2 = [dc.get(k,0) for k in sorted(baseList)]

        return lst2


            

    def solveForX(self, num ,p):
        pfactordict = self.computeFactorBaseLogs(p)
        factors = sympy.factorint(num % p)
        x=0
        for key in factors:
            x+=pfactordict[key]*factors[key]


        return x % (p-1)
