import enum
import numpy as np


class Geometry(enum.Enum):
    spherical = 0
    euclidean = 1
    hyperbolic = 2



def e2hnorm(x):
    return 2 * np.arctanh(x)
    
def h2enorm(x):
    return 1.0 if np.isnan(x) else np.tanh(0.5 * x)

def e2snorm(x):
    return 2 * np.arctan(x)

def s2enorm(x):
    return np.tan(0.5 * x)

def isinfinite(z):
    try:
        return any(np.isnan(z)) or np.max(z) > np.Infinity
    except TypeError:
        return np.isnan(z) or abs(z) > np.Infinity
