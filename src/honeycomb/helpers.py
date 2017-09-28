import numpy as np


TOLERANCE = 1e-6
INFINITY_BOUND = 1e7


# --------------------
# comparasion of two floating numbers, they also work for +/-np.inf inputs.

def equal(x, y):
    return y - TOLERANCE <= x <= y + TOLERANCE

def less(x, y):
    return x < y - TOLERANCE

def greater(x, y):
    return x > y + TOLERANCE

def greater_equal(x, y):
    return not less(x, y)

def less_equal(x, y):
    return not greater(x, y)

# --------------------

def is_finite(x):
    if hasattr(x, "__getitem__"):
        return np.max(np.absolute(x[:])) <= INFINITY_BOUND
    else:
        return abs(x) <= INFINITY_BOUND

def round_and_hash(x):
    decimals = int(np.log10(1.0 / TOLERANCE))
    if hasattr(x, "__getitem__"):
        return hash(tuple(x[:].round(decimals)))
    else:
        return hash(round(x, decimals))
