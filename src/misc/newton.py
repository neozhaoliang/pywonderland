import numpy as np
from PIL import Image
from numba import jit


# define functions manually, do not use numpy's poly1d funciton!
@jit('complex64(complex64)', nopython=True)
def f(z):
    # z*z*z is faster than z**3
    return z*z*z - 1


@jit('complex64(complex64)', nopython=True)
def df(z):
    return 3*z*z


@jit('float64(complex64)', nopython=True)
def iterate(z):
    num = 0
    while abs(f(z)) > 1e-4:
        w = z - f(z)/df(z)
        num += np.exp(-1/abs(w-z))
        z = w
    return num


def render(imgsize):
    x = np.linspace(-1, 1, imgsize)
    y = np.linspace(1, -1, imgsize)
    z = x[None, :] + y[:, None] * 1j
    img = np.frompyfunc(iterate, 1, 1)(z).astype(np.float)
    img /= np.max(img)

    # self-defined rgb channels, a mimick of matplotlib's hot colormap
    red = np.sin(img * np.pi)
    green = img * img
    blue = np.zeros_like(img)
    image = np.dstack((red, green, blue))
    Image.fromarray(np.uint8(image*255)).save('newton.png')


if __name__ == '__main__':
    import time
    start = time.time()
    render(imgsize=400)
    end = time.time()
    print('runtime: {:03f} seconds'.format(end - start))
