"""
Short helper functions for handling integer arithmetic.
"""
from collections import defaultdict


__all__ = ["gcd", "lcm", "prime_factors"]


def gcd(m, n):
    """greatest commond divisor."""
    m = abs(m)
    n = abs(n)
    while n:
        m, n = n, m % n
    return m


def lcm(m, n):
    """least common multiple."""
    d = gcd(m, n)
    return abs(m * n) // d


def prime_factors(n):
    """
    return the prime factors of an integer stored in a dict {prime: exponent}.
    """
    n = abs(n)
    primes = defaultdict(int)
    # prime factor 2
    while n % 2 == 0:
        primes[2] += 1
        n = n // 2
    # odd prime factors
    for i in range(3, int(n**0.5) + 1, 2):
        while n % i == 0:
            primes[i] += 1
            n = n // i
    # if n is prime
    if n > 2:
        primes[n] += 1

    return primes
