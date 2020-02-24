"""
Helper functions for integer arithmetic.
"""
from collections import defaultdict


def lcm(m, n):
    if m * n == 0:
        return 0
    q, r = m, n
    while r != 0:
        q, r = r, q % r
    return abs((m * n) // q)


def decompose(n):
    """
    Decompose an integer into a product of primes. The result is stored in a
    dict {p: e}. This function is used for generating cyclotomic polynomials.
    """
    n = abs(n)
    primes = defaultdict(int)
    # factor 2
    while n % 2 == 0:
        primes[2] += 1
        n = n // 2
    # odd prime factors
    for i in range(3, int(n**0.5) + 1, 2):
        while n % i == 0:
            primes[i] += 1
            n = n // i
    # if n itself is prime
    if n > 2:
        primes[n] += 1
    return primes
