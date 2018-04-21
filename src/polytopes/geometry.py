import numpy as np


def gram_schimdt(M):
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
    n = len(v)
    v = np.array(v)[np.newaxis]
    return np.eye(n) - 2 * np.dot(v.T, v)


def get_mirrors(p, q, r):
    M = np.zeros((4, 4), dtype=np.float)
    M[0, 0] = 1.0
    M[1, 0] = np.cos(np.pi / p)
    M[1, 1] = np.sqrt(1 - M[1, 0] * M[1, 0])
    M[2, 1] = np.cos(np.pi / q) / M[1, 1]
    M[2, 2] = np.sqrt(1.0 - M[2, 1] * M[2, 1])
    M[3, 2] = np.cos(np.pi / r) / M[2, 2]
    M[3, 3] = np.sqrt(1 - M[3, 2] * M[3, 2])
    return M


def proj4d(v):
    v = np.asarray(v, dtype=np.float)
    v /= np.linalg.norm(v)
    return v[:-1] / (1 - v[-1])
