"""
Some helper functions for building the geometry.
"""
import sys
import numpy as np


def normalize(v):
    """Normalize a vector `v`.
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
    """Stereographic projection from 4d to 3d.
    """
    v = normalize(v)
    return v[:-1] / (1 + 1e-8 - v[-1])  # avoid divide by zero


def make_symmetry_matrix(upper_triangle):
    """Make a symmetric matrix from a list of integers/rationals
    as the upper half above the diagonals.

    Example:
    >>> upper_trianle = [4, 2, 3]
    >>> make_symmstry_matrix(upper_triangle)
    >>> [[1, 4, 2],
         [4, 1, 3],
         [2, 3, 1]]
    """
    n = int((2 * len(upper_triangle)) ** 0.5) + 1
    if len(upper_triangle) != (n * n - n) / 2:
        raise ValueError("Invalid input sequence")
    ind = 0
    cox_mat = np.eye(n, dtype="object")
    for row in range(n - 1):
        for col in range(row + 1, n):
            cox_mat[row][col] = cox_mat[col][row] = upper_triangle[ind]
            ind += 1
    return cox_mat


def get_coxeter_matrix(coxeter_diagram):
    """
    Get the Coxeter matrix from a given coxeter_diagram.
    The Coxeter matrix is square and entries are all integers, it describes
    the relations between the generators of the symmetry group. Here is the
    math: suppose two mirrors mᵢ, mⱼ form an angle p/q where p,q are coprime
    integers, then the two generator reflections about these two mirrors rᵢ, rⱼ
    satisfy (rᵢrⱼ)^p = 1.

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
    Given a Coxter diagram consists of integers/rationals that represent
    the angles between the mirrors (a rational p means the angle is π/p),
    return a square matrix whose rows are the normal vectors of the mirrors.
    This matrix is not unique, here we use a lower triangle one to simplify
    the computations.
    """
    # error handling function when the input coxeter matrix is invalid.
    def err_handler(err_type, flag):
        print(
            "Invalid input Coxeter diagram. This diagram does not give a finite \
symmetry group of an uniform polytope. See \
https://en.wikipedia.org/wiki/Coxeter_group#Symmetry_groups_of_regular_polytopes \
for a complete list of valid Coxeter diagrams."
        )
        sys.exit(1)

    np.seterrcall(err_handler)
    np.seterr(all="call")

    coxeter_matrix = np.array(
        make_symmetry_matrix(coxeter_diagram)
    ).astype(float)
    C = -np.cos(np.pi / coxeter_matrix)
    M = np.zeros_like(C)
    n = len(M)
    # the first normal vector is simply (1, 0, ...)
    M[0, 0] = 1
    # in the i-th row, the j-th entry can be computed via the (j, j) entry.
    for i in range(1, n):
        for j in range(i):
            M[i, j] = (C[i, j] - np.dot(M[j, :j], M[i, :j])) / M[j, j]
        # the (i, i) entry is used to normalize this vector
        M[i, i] = np.sqrt(1 - np.dot(M[i, :i], M[i, :i]))

    return M
