'''
A Fast Mandelbrot set wallpaper renderer
'''
import numpy as np
from PIL import Image
from numba import jit


MAXITERS = 200
RADIUS = 100


@jit('float32(complex64)', nopython=True)
def iterate(c):
    z = 0j
    for i in range(MAXITERS):
        if z.real*z.real + z.imag*z.imag > RADIUS:
            v = np.log2(i + 1 - np.log2(np.log2(abs(z)))) / 6
            return max(0, min(v, 2-v))
        z = z*z + c
    return 0


def main(xmin, xmax, ymin, ymax, width, height):
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymax, ymin, height)
    z = x[None, :] + y[:, None]*1j
    B = np.frompyfunc(iterate, 1, 1)(z).astype(np.float)
    img = np.dstack((B**4, B**3, B))
    Image.fromarray(np.uint8(img*255)).save('mandelbrot.png')


if __name__ == '__main__':
    import time
    start = time.time()
    main(-2.1, 0.8, -1.16, 1.16, 800, 640)
    end = time.time()
    print('runtime: {:3f} seconds'.format(end - start))
