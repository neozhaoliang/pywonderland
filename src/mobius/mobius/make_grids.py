import numpy as np

from .mobius import Mobius
from .cline import CLine
from .import utils


def generate_grids_elliptic(p, N, interval=(0.0001, 5)):
    """Generate two mutually orthogonal circles from a
    specified point `p` inside the disk.

    The first family (`para_grid`) consists of circles that are concentric
    at `p` and have equal radius difference between adjacent pairs.

    The second family (`orth_grid`) consists of circles that pass
    through `p` and have equal angle difference between adjacent pairs.

    :param p: A point inside the unit disk.
    :param N: The number of circles in each family.
    :param interval: min/max radius for the circles in the `para_grid`
        family, in the hyperbolic metric.
    """
    rads = utils.dist_poincare_to_euclidean(np.linspace(0.001, 5, N))
    para_grid = [CLine.from_circle(0, r) for r in rads]
    dirs = np.exp(1j * np.linspace(0, 2 * np.pi, N + 1))
    orth_grid = [CLine.from_line(n, 0) for n in dirs]
    T = Mobius.translation(0, p)
    para_grid = [T(C) for C in para_grid]
    orth_grid = [T(C) for C in orth_grid]
    return para_grid, orth_grid


def generate_grids_parabolic(p, N, dist=1):
    """Generate two mutually orthogonal circles from a
    specified point `p` on the ideal boundary.

    The first family (`para_grid`) consists of horocycles that are all
    tangent with the ideal boundary at `p`.

    The second family (`orth_grid`) consists of circles that are tangent
    at `p` and are orthogonal to the ideal boundary.

    :param p: A point on the unit circle.
    :param N: The number of circles in each family.
    :param dist: The parabolic transformation that keeps the two families
        invariant will be conjugate to `z --> z + dist`.
    """
    horizons = utils.dist_uhs_to_euclidean(np.linspace(-3, 3, N))
    para_grid = [CLine.from_line(1j, offset) for offset in horizons]
    verticals = np.arange(-(N // 2) * dist, (N // 2) * dist, dist)
    orth_grid = [CLine.from_line(1, offset) for offset in verticals]
    T = Mobius.disk_to_uhs(p, 'to_inf')
    para_grid = [T.inv(C) for C in para_grid]
    orth_grid = [T.inv(C) for C in orth_grid]
    return para_grid, orth_grid


def generate_grids_hyperbolic(p1, p2, N, scale=3.0):
    """Generate two mutually orthogonal circles from two points
    `p1`, `p2` on the ideal boundary.

    The first family (`para_grid`) consists of circles that are all
    tangent with the ideal boundary at `p`.

    The second family (`orth_grid`) consists of circles that are tangent
    at `p` and are orthogonal to the ideal boundary.

    :param p1, p2: Two distinct points on the unit circle.
    :param N: The number of circles in each family.
    :param scale: The hyperbolic transformation that keeps the two
        families invariant will be conjugate to `z --> scale * z`.
    """
    if N % 2 == 0:
        N += 1
    nors = np.exp(np.linspace(0, np.pi, N + 1) * 1j)
    para_grid = [CLine.from_line(n, 0) for n in nors]
    rads = np.exp(np.linspace(-3, 3, N + 1))
    orth_grid = [CLine.from_circle(0, r) for r in rads]
    T = Mobius([-p1.conjugate() * 1j, 1j, -p2.conjugate(), 1]).inv
    para_grid = [T(C) for C in para_grid]
    orth_grid = [T(C) for C in orth_grid]
    return para_grid, orth_grid
