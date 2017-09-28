import numpy as np
from enum import Enum


Geometry = Enum("Geometry", ["Euclidean", "Spherical", "Hyperbolic"])


# --- conversions between Euclidean, Spherical and Hyperbolic distances ---

def h2enorm(x):
    return 1.0 if np.isnan(x) else np.tanh(0.5 * x)

def e2hnorm(x):
    if not 0 <= x < 1:
        raise ValueError("Invaid Euclidean distance encountered.")
    else:
        return 2.0 * np.arctanh(x)
 
def s2enorm(x):
    return np.tan(0.5 * x)
 
def e2snorm(x):
    return 2.0 * np.arctan(x)
