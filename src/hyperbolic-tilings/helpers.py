from fractions import Fraction
import numpy as np


def normalize(v):
    """Normalize a vector `v`.
    """
    return np.array(v) / np.linalg.norm(v)


def make_symmetry_matrix(upper_triangle):
    """Given three or six integers/rationals, fill them into a
       3x3 (or 4x4) symmetric matrix.
    """
    if len(upper_triangle) == 3:
        a12, a13, a23 = upper_triangle
        return [[1, a12, a13],
                [a12, 1, a23],
                [a13, a23, 1]]
    elif len(upper_triangle) == 6:
        a12, a13, a14, a23, a24, a34 = upper_triangle
        return [[1, a12, a13, a14],
                [a12, 1, a23, a24],
                [a13, a23, 1, a34],
                [a14, a24, a34, 1]]
    else:
        raise ValueError("Three or six inputs are expected.")


def get_init_point(M, d):
    """Given the normal vectors of the mirrors stored as row vectors in `M`
       and a tuple of non-negative floats `d`, compute the vector `v` whose
       distance vector to the mirrors is `d` and return its normalized version.
    """
    return normalize(np.linalg.solve(M, d))


def get_geometry_type(pqr):
    """Get the geometry type. Return 1 if it's spherical, 0 if it's Euclidean,
       -1 if it's hyperbolic.
    """
    s = sum([Fraction(1, x) if x != -1 else 0 for x in pqr])
    if s > 1:
        return 1
    elif s == 1:
        return 0
    else:
        return -1
