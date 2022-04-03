import numpy as np


infty = 1e10
epsilon = 1e-10


def greater_than(x, y):
    return x > y + epsilon


def less_than(x, y):
    return x < y - epsilon


def iszero(x):
    return abs(x) < epsilon


def equal(x, y):
    return iszero(x - y)


def nonzero(x):
    return not iszero(x)


def isinf(x):
    return abs(x) > infty


def safe_div(x, y):
    if isinf(y):
        return 0j

    if iszero(y):
        return complex(infty)

    return x / y


def norm2(z):
    return z.real * z.real + z.imag * z.imag


def dist_poincare_to_euclidean(x):
    return np.tanh(0.5 * x)


def dist_uhs_to_euclidean(x):
    return np.exp(x)


def angle_twopi(z):
    arg = np.angle(z)
    if arg < 0:
        arg += 2 * np.pi
    return arg
