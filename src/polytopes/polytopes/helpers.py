# -*- coding: utf-8 -*-
"""
Some helper functions for building the geometry.
"""
import sys
import numpy as np


def normalize(v):
    """
    Normalize a vector `v`.
    """
    return np.array(v) / np.linalg.norm(v)


def reflection_matrix(v):
    """
    Return the reflection transformation about a plane with normal vector `v`.
    see "https://en.wikipedia.org/wiki/Householder_transformation".
    """
    n = len(v)
    v = np.array(v)[np.newaxis]
    return np.eye(n) - 2 * np.dot(v.T, v)


def get_init_point(M, d):
    """
    Given the normal vectors of the mirrors stored as row vectors in `M`
    and a tuple of non-negative floats `d`, compute the vector `v` whose
    distance vector to the mirrors is `d` and return its normalized version.
    """
    return normalize(np.linalg.solve(M, d))


def proj3d(v):
    """
    Stereographic projection of a 4d vector with pole at (0, 0, 0, 1).
    """
    v = normalize(v)
    x, y, z, w = v
    return np.array([x, y, z]) / (1 + 1e-8 - w)  # avoid divide by zero


def make_symmetry_matrix(upper_triangle):
    """
    Make a symmetric matrix from a list of integers/rationals.
    """
    length = len(upper_triangle)
    if length not in (3, 6, 10):
        raise ValueError("the length of the coxeter diagram must be 3 or 6 or 10.")

    if length == 3:
        a12, a13, a23 = upper_triangle
        return [[1, a12, a13],
                [a12, 1, a23],
                [a13, a23, 1]]
    if length == 6:
        a12, a13, a14, a23, a24, a34 = upper_triangle
        return [[1, a12, a13, a14],
                [a12, 1, a23, a24],
                [a13, a23, 1, a34],
                [a14, a24, a34, 1]]
    if length == 10:
        a12, a13, a14, a15, a23, a24, a25, a34, a35, a45 = upper_triangle
        return [[1, a12, a13, a14, a15],
                [a12, 1, a23, a24, a25],
                [a13, a23, 1, a34, a35],
                [a14, a24, a34, 1, a45],
                [a15, a25, a35, a45, 1]]


def get_coxeter_matrix(coxeter_diagram):
    """
    Get the Coxeter matrix from a given coxeter_diagram.
    The Coxeter matrix is square and entries are all integers, it describes the
    relations between the generators of the symmetry group. Here is the math:
    suppose two mirrors mᵢ, mⱼ form an angle p/q where p,q are coprime integers,
    then the two generator reflections about these two mirrors rᵢ, rⱼ satisfy (rᵢrⱼ)^p = 1.

    Example:
    >>> coxeter_diagram = (3, 2, Fraction(5, 2))
    >>> get_coxeter_matrix(coxeter_diagram)
    >>> [[1, 3, 2],
        [3, 1, 5],
        [2, 5, 1]]

    Note that in general one cannot recover the Coxeter diagram
    from the Coxeter matrix since a star polytope may have the
    same Coxeter matrix with a convex one.
    """
    upper_triangle = [x.numerator for x in coxeter_diagram]
    return make_symmetry_matrix(upper_triangle)


def get_mirrors(coxeter_diagram):
    """
    Given three or six or ten integers/rationals that represent the angles between
    the mirrors (a rational p means the angle is π/p), return a square matrix whose
    rows are the normal vectors of the mirrors.
    """
    # error handling function when the input coxeter matrix is invalid.
    def err_handler(err_type, flag):
        print("Invalid input Coxeter diagram. This diagram does not give a finite \
symmetry group of an uniform polytope. See \
https://en.wikipedia.org/wiki/Coxeter_group#Symmetry_groups_of_regular_polytopes \
for a complete list of valid Coxeter diagrams.")
        sys.exit(1)

    np.seterrcall(err_handler)
    np.seterr(all="call")

    coxeter_matrix = np.array(make_symmetry_matrix(coxeter_diagram)).astype(np.float)
    C = -np.cos(np.pi / coxeter_matrix)
    M = np.zeros_like(C)

    M[0, 0] = 1
    M[1, 0] = C[0, 1]
    M[1, 1] = np.sqrt(1 - M[1, 0]*M[1, 0])
    M[2, 0] = C[0, 2]
    M[2, 1] = (C[1, 2] - M[1, 0]*M[2, 0]) / M[1, 1]
    M[2, 2] = np.sqrt(1 - M[2, 0]*M[2, 0] - M[2, 1]*M[2, 1])

    if len(coxeter_matrix) > 3:
        M[3, 0] = C[0, 3]
        M[3, 1] = (C[1, 3] - M[1, 0]*M[3, 0]) / M[1, 1]
        M[3, 2] = (C[2, 3] - M[2, 0]*M[3, 0] - M[2, 1]*M[3, 1]) / M[2, 2]
        M[3, 3] = np.sqrt(1 - np.dot(M[3, :3], M[3, :3]))

    if len(coxeter_matrix) == 5:
        M[4, 0] = C[4, 0]
        M[4, 1] = (C[4, 1] - M[1, 0]*M[4, 0]) / M[1, 1]
        M[4, 2] = (C[4, 2] - M[2, 0]*M[4, 0] - M[2, 1]*M[4, 1]) / M[2, 2]
        M[4, 3] = (C[4, 3] - M[3, 0]*M[4, 0] - M[3, 1]*M[4, 1] - M[3, 2]*M[4, 2]) / M[3, 3]
        M[4, 4] = np.sqrt(1 - np.dot(M[4, :4], M[4, :4]))

    return M
