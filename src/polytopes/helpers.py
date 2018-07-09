# -*- coding: utf-8 -*-
"""
Some helper functions for calculating the geometry
and writing to POV-Ray files.
"""
import numpy as np


def normalize(v):
    """Normalize a vector v."""
    return np.asarray(v) / np.linalg.norm(v)


def reflection_matrix(v):
    """Return the reflection transformation about a plane with normal vector v."""
    n = len(v)
    v = np.array(v)[np.newaxis]
    return np.eye(n) - 2 * np.dot(v.T, v)


def get_init_point(M, d):
    """
    Given the mirrors M, return a vector whose distances to the mirrors
    are represented by the vector d. The result is normlized, so it's determines
    by the ratio between those distances.
    """
    return normalize(np.linalg.solve(M, d))


def get_coxeter_matrix(upper_triangle):
    """
    Construct the Coxeter matrix from a list of 3 or 6 integers.
    If 3 integers are given then the result is a 3x3 matrix, else it's a 4x4 matrix.
    These integers are interpreted as the upper triangle part of the matrix.
    """
    if len(upper_triangle) == 3:
        p, q, r = upper_triangle
        return [[1, p, q], [p, 1, r], [q, r, 1]]
    elif len(upper_triangle) == 6:
        coxeter_matrix = np.eye(4).astype(np.int)
        for i in range(4):
            for j in range(i+1, 4):
                k = j - 1 if i == 0 else i + j
                coxeter_matrix[i, j] = coxeter_matrix[j, i] = upper_triangle[k]
        return coxeter_matrix
    else:
        raise ValueError("Invalid number of inputs for the Coxeter matrix")


def get_mirrors(coxeter_matrix):
    """
    Given a 3x3 or 4x4 Coxeter matrix, get the normal
    vectors of the reflection planes.
    """
    coxeter_matrix = np.asarray(coxeter_matrix, dtype=np.float)
    C = -np.cos(np.pi / coxeter_matrix)
    M = np.zeros_like(C)
    try:
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
    except:
        raise ValueError("Cannot get mirrors for this input Coxeter matrix")


def proj3d(v):
    """
    stereographic projection of a 4d vector with pole at (0, 0, 0, 1).
    """
    v = normalize(v)
    x, y, z, w = v
    return np.array([x, y, z]) / (1 - w)
    

def get_sphere_info(points):
    """Return the sphere pass through 4 4d-points."""
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


def export_pov_array(arr):
    """Export the vertices of a face to povray array."""
    declare = "#declare vertices_list = array[{}] {{ {} }};\n"
    return declare.format(len(arr), pov_vector_list(arr))


def export_polygon_face(ind, face, isplane, center,
                        radius, facesize, facecolor):
    """Export the information of a face to a povray macro."""
    if isplane:
        macro = "FlatFace({}, {}, vertices_list, {}, {})\n"
        return macro.format(ind, len(face), facesize, pov_vector(facecolor))
    else:
        macro = "BubbleFace({}, {}, vertices_list, {}, {}, {}, {})\n"
        return macro.format(ind, len(face), pov_vector(center), radius,
                            facesize, pov_vector(facecolor))
