"""
~~~~~~~~~~~~~~~~~~
The Newton Fractal
~~~~~~~~~~~~~~~~~~
"""
import matplotlib.pyplot as plt
import numpy as np
from numba import jit


# define functions manually, do not use numpy's poly1d funciton!
@jit("complex64(complex64)", nopython=True)
def f(z):
    # z*z*z is faster than z**3
    return z * z * z - 1
    # return z**5 + 0.25*z*z + 1.17


@jit("complex64(complex64)", nopython=True)
def df(z):
    return 3 * z * z
    # return 5*z**4 + 0.5*z


@jit("float64(complex64)", nopython=True)
def iterate(z):
    num = 0
    while abs(f(z)) > 1e-4:
        w = z - f(z) / df(z)
        num += np.exp(-1 / abs(w - z))
        z = w
    return num


def render(imgsize):
    y, x = np.ogrid[1 : -1 : imgsize * 2j, -1 : 1 : imgsize * 2j]
    z = x + y * 1j
    img = np.frompyfunc(iterate, 1, 1)(z).astype(float)
    fig = plt.figure(figsize=(imgsize / 100.0, imgsize / 100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], aspect=1)
    ax.axis("off")
    ax.imshow(img, cmap="hot")
    fig.savefig("newton.png")


if __name__ == "__main__":
    render(imgsize=600)
