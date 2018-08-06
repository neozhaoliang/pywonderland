# -*- coding: utf-8 -*-
"""
This file contains some helper functions for calculating the geometry
and converting vectors to POV-Ray format.
"""
import sys
import numpy as np


def normalize(v):
    """Normalize a vector `v`."""
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
    Given the mirrors stored as row vectors in `M` and a tuple of non-negative
    floats `d`, compute the vector `v` whose distances to the mirrors are `d`
    and return its normalize version.
    """
    return normalize(np.linalg.solve(M, d))


def proj3d(v):
    """
    Stereographic projection of a 4d vector with pole at (0, 0, 0, 1).
    """
    v = normalize(v)
    x, y, z, w = v
    return np.array([x, y, z]) / (1 + 1e-8 - w)  # avoid divide by zero


def get_sphere_info(points):
    """
    Given a list of 4d points that lie on the same face of a polytope,
    compute the 3d sphere that passes through the projected points.
    """
    rib = np.sum(points, axis=0)
    rib3d = proj3d(rib)
    pts3d = np.asarray([proj3d(p) for p in points])
    facesize = np.linalg.norm(pts3d[0] - rib3d)

    M = np.ones((4, 4), dtype=np.float)
    M[:3, :3] = pts3d[:3]
    M[ 3, :3] = rib3d
    b = [-sum(x*x) for x in M[:, :3]]
    # if this is a plane
    if abs(np.linalg.det(M)) < 1e-4:
        center = rib3d
        return True, center, None, facesize
    else:
        T = np.linalg.solve(M, b)
        D, E, F, G = T
        center = -0.5 * T[:3]
        radius = 0.5 * np.sqrt(D*D + E*E + F*F - 4*G)
        return False, center, radius, facesize


def pov_vector(v):
    """Convert a vector to POV-Ray format."""
    return "<{}>".format(", ".join([str(x) for x in v]))


def pov_vector_list(vectors):
    """Convert a list of vectors to POV-Ray format."""
    return ", ".join([pov_vector(v) for v in vectors])


def pov_array(arr):
    """Export the vertices of a face to POV-Ray array."""
    declare = "#declare vertices_list = array[{}] {{ {} }};\n"
    return declare.format(len(arr), pov_vector_list(arr))


def export_face(ind, face, isplane, center,
                radius, facesize):
    """Export the information of a polytope face to a POV-Ray macro."""
    if isplane:
        macro = "FlatFace({}, {}, vertices_list, {}, {})\n"
        return macro.format(ind, len(face), pov_vector(center), facesize)
    else:
        macro = "BubbleFace({}, {}, vertices_list, {}, {}, {})\n"
        return macro.format(ind, len(face), pov_vector(center), radius, facesize)


def check_duplicate_face(f, l):
    """Check if a face `f` is already in the list `l`."""
    for _ in range(len(f)):
        if f in l or f[::-1] in l:
            return True
        f = f[-1:] + f[:-1]
    return False


def fill_matrix(upper_triangle):
    """
    Given a tuple of three or six integers/rationals, fill them in the upper triangle
    part of a 3x3 (or 4x4) symmetric matrix."""
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


def get_mirrors(upper_triangle):
    """
    Given 3 or 6 rational numbers, return a 3x3 or 4x4 matrix whose rows are
    the normal vectors of the reflection planes.
    """
    # error handling function when the input coxeter matrix is invalid.
    def err_handler(err_type, flag):
        print("Invalid input Coxeter diagram.")
        sys.exit(1)

    np.seterrcall(err_handler)
    np.seterr(all='call')

    coxeter_matrix = np.array(fill_matrix(upper_triangle)).astype(np.float)
    C = -np.cos(np.pi / coxeter_matrix)
    M = np.zeros_like(C)

    M[0, 0] = 1
    M[1, 0] = C[0, 1]
    M[1, 1] = np.sqrt(1 - M[1, 0]*M[1, 0])
    M[2, 0] = C[0, 2]
    M[2, 1] = (C[1, 2] - M[1, 0]*M[2, 0]) / M[1, 1]
    M[2, 2] = np.sqrt(1 - M[2, 0]*M[2, 0] - M[2, 1]*M[2, 1])
    if len(coxeter_matrix) == 4:
        M[3, 0] = C[0, 3]
        M[3, 1] = (C[1, 3] - M[1, 0]*M[3, 0]) / M[1, 1]
        M[3, 2] = (C[2, 3] - M[2, 0]*M[3, 0] - M[2, 1]*M[3, 1]) / M[2, 2]
        M[3, 3] = np.sqrt(1 - M[3, 0]*M[3, 0] - M[3, 1]*M[3, 1] - M[3, 2]*M[3, 2])
    return M


def get_coxeter_matrix(upper_triangle):
    return fill_matrix(upper_triangle)
