# -*- coding: utf-8 -*
"""
Some helper functions for building the geometry.
"""
import numpy as np


def gram_schimdt(M):
    """
    Gram-Schimdt procedure on the row vectors of a matrix `M`.
    """
    M = np.asarray(M, dtype=np.float)
    N = M.copy()
    for i in range(1, len(M)):
        for j in range(i):
            if not N[j].any():
                continue
            else:
                N[i] -= np.dot(M[i], N[j]) / np.dot(N[j], N[j]) * N[j]
    return N


def reflection_matrix(v):
    """
    The reflection transformation about a plane with normal vector `v`.
    """
    n = len(v)
    v = np.array(v)[np.newaxis]
    return np.eye(n) - 2 * np.dot(v.T, v)


def get_mirrors(p, q, r):
    """
    Return the normal vectors of the 4 mirrors.
    Coxeter diagram: * -- p -- * -- q -- * -- r -- *.
    """
    M = np.zeros((4, 4), dtype=np.float)
    M[0, 0] = 1.0
    M[1, 0] = np.cos(np.pi / p)
    M[1, 1] = np.sqrt(1 - M[1, 0] * M[1, 0])
    M[2, 1] = np.cos(np.pi / q) / M[1, 1]
    M[2, 2] = np.sqrt(1.0 - M[2, 1] * M[2, 1])
    M[3, 2] = np.cos(np.pi / r) / M[2, 2]
    M[3, 3] = np.sqrt(1 - M[3, 2] * M[3, 2])
    return M


def proj3d(v):
    """
    stereographic projection of a 4d vector at pole (0, 0, 0, -1).
    """
    v = np.array(v) / np.linalg.norm(v)
    x, y, z, w = v
    return np.array([x, y, z]) / (1 + w)


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
        return True, center, facesize, facesize
    else:
        T = np.linalg.solve(M, b)
        D, E, F, G = T
        center = -0.5 * T[:3]
        radius = 0.5 * np.sqrt(D*D + E*E + F*F - 4*G)
        return False, center, radius, facesize


def pov_vec(v):
    return "<" + ", ".join([str(x) for x in v]) + ">"


def pov_vectors(v_list):
    return ", ".join([pov_vec(v) for v in v_list])
