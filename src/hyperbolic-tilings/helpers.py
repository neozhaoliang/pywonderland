from collections import deque
import numpy as np


def cdot(z, w):
    return (z * w.conjugate()).real


def ccross(z, w):
    return (z * w.conjugate()).imag


def make_symmetry_matrix(p, q, r):
    return [[1, p, q], [p, 1, r], [q, r, 1]]


def project_point(v, z1, z2):
    """Project a point v to the line passes through z1 and z2
    """
    n = z2 - z1
    n /= abs(n)
    t = cdot(v - z1, n)
    return z1 + t * n


def reflection_by_line(z1, z2):
    """Return the reflection transformation about the line passes through points z1 and z2.
    """
    return lambda v: 2 * project_point(v, z1, z2) - v


def traverse(dfa, depth, reflections, fundamental_shape):
    """Traverse the given dfa using bread-first search.
    """
    queue = deque()
    queue.append([dfa.start, (), 0, fundamental_shape] )
    while queue:
        state, word, i, shape = queue.popleft()
        yield state, word, i, shape
        if i < depth:
            for symbol, target in state.all_transitions():
                queue.append([target,
                              word + (symbol,),
                              i + 1,
                              [reflections[symbol](p) for p in shape]])


def from_bary_coords(vertices, weights):
    """Weighted sum of the points in `vertices`.
    """
    return np.dot(vertices, weights) / sum(weights)
