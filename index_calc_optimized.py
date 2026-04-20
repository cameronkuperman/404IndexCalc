import primesieve
import random
from math import exp, sqrt, log
import sympy
from itertools import combinations


class IndexCalc:
    def __init__(self, prime, g):
        self.p = prime
        self.g = g
        """ Optimization 1: Instead of computing factor base each iteration of loop 
        within computeFactorBaseLogs(), store within init to save time """
        self._factor_base_cache: dict[int, tuple[int, list[int]]] = {}
        self._log_cache: dict[int, dict[int, int]] = {}

    def computeFactorBase(self, p: int) -> tuple[int, list[int]]:
        if p not in self._factor_base_cache:
            b = int(exp(sqrt(log(p) * log(log(p)))))
            prime_list = primesieve.primes(b)
            self._factor_base_cache[p] = (b, prime_list)
        return self._factor_base_cache[p]

    def computeAllFactors(self, b: int) -> list[int]:
        return primesieve.primes(b)

    def factor(self, num: int) -> dict[int, int]:
        return sympy.factorint(num)

    def _is_b_smooth(self, num: int, bound: int) -> bool:
        factors = sympy.factorint(num, limit=bound)
        """ Optimization 3: Immediately break if large enough
        factor found (limit=bound param)"""
        if 1 in factors:
            return False
        return all(p <= bound for p in factors)

    def turnBSmooth(self, num: int, p: int, bound: int, g: int) -> tuple[int, int]:
        x = 0
        while not self._is_b_smooth(num, bound):
            num = num * g % p
            x += 1
        return num, x

    def createLogVector(self, num: int, base_list: list[int]) -> list[int]:
        dc = sympy.factorint(num)
        return [dc.get(k, 0) for k in base_list]
        """ Optimization 4: No need to sort base_list each time if we plug
        in a precomputed sorted base_list each time"""

    def find_invertible_subsystem(
        self,
        sample_vectors: list[list[int]],
        sample_ks: list[int],
        pl: list[int],
        p: int,
    ) -> tuple[sympy.Matrix | None, sympy.Matrix | None]:
        m = len(pl)
        mod = p - 1
        for idxs in combinations(range(len(sample_vectors) - 1, -1, -1), m):
            """ Optimization 5: use a FILO algorithm instead of FIFO in order to
            increase chance of lin ind rows"""
            rows = [sample_vectors[i] for i in idxs]
            rhs  = [sample_ks[i]      for i in idxs]
            A    = sympy.Matrix(rows)
            det  = A.det()
            if sympy.gcd(int(det), mod) == 1:
                return A, sympy.Matrix(rhs)
        return None, None

    def computeFactorBaseLogs(self, p: int) -> dict[int, int]:
        if p in self._log_cache:
            return self._log_cache[p]

        b, pl = self.computeFactorBase(p)
        mod   = p - 1
        m     = len(pl)

        sample_vectors: list[list[int]] = []
        sample_ks:      list[int]       = []

        while True:
            needed = max(0, 2 * m - len(sample_vectors))
            attempts = 0
            max_attempts = needed * 20

            while len(sample_vectors) < 2 * m and attempts < max_attempts:
                attempts += 1
                k   = random.randint(1, mod - 1)
                num = pow(self.g, k, p)
                """ Optimization 2: Fast binary exponentiation takes O(log(k)) time
                instead of computing g^k and then mod reducing being O(k)"""
                if not self._is_b_smooth(num, b):
                    continue
                sample_vectors.append(self.createLogVector(num, pl))
                sample_ks.append(k)

            A, bvec = self.find_invertible_subsystem(sample_vectors, sample_ks, pl, p)
            if A is None:
                continue

            inverse      = A.inv_mod(mod)
            logsolutions = (inverse * bvec).applyfunc(lambda x: int(x) % mod)
            """ Optimization 6: instead of implicitly calculating inverse*b,
            reduce each entry p-1 and then convert to int, 
            avoiding extra overhead"""
            break

        result = {pl[i]: int(logsolutions[i]) for i in range(m)}
        self._log_cache[p] = result
        return result
        """ Optimization 7: after each failed attempt, keep old rows and add
        new ones to polynomial increase combinations of a new hit
        ((# of rows available) choose (m))"""

    def solveForX(self, num: int, p: int) -> int:
        pfactordict = self.computeFactorBaseLogs(p)
        factors = sympy.factorint(num % p)
        x = 0
        for key, exp_ in factors.items():
            x += pfactordict[key] * exp_
        return x % (p - 1)

    def indexCalcAlgoFull(self, p: int, g: int, num: int) -> int:
        b, factor_base = self.computeFactorBase(p)
        num_smooth, x = self.turnBSmooth(num, p, b, g)
        k = self.solveForX(num_smooth, p)
        return (k - x) % (p - 1)
