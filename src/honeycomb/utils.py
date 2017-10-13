import numpy as np


INFINITY = 1e11  # or np.inf
EPSILON = 1e-8


def invalid(x):
    if hasattr(x, "__getitem__"):
        return any(np.isnan(x[:]))
    else:
        return np.isnan(x)

def finite(x):
    if hasattr(x, "__getitem__"):
        return max(np.absolute(x[:])) < INFINITY
    else:
        return abs(x) < INFINITY

def isinf(x):
    return not finite(x)

def zero(x):
    if hasattr(x, "__getitem__"):
        return max(np.absolute(x[:])) <= EPSILON
    else:
        return abs(x) <= EPSILON
    
def equal(x, y):
    return y - EPSILON <= x <= y + EPSILON

def less(x, y):
    return x < y - EPSILON

def greater(x, y):
    return x > y + EPSILON

def greater_equal(x, y):
    return not less(x, y)

def less_equal(x, y):
    return not greater(x, y)

def even(n):
    return n % 2 == 0

def odd(n):
    return n % 2 == 1

def round_and_hash(x):
    decimals = int(np.log10(1.0 / EPSILON))
    if hasattr(x, "__getitem__"):
        return hash(tuple(np.round(x[:], decimals)))
    else:
        return hash(np.round(x, decimals))
