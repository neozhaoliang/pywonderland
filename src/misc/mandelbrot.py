#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A fast Mandelbrot set wallpaper renderer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

reddit discussion:
    https://www.reddit.com/r/math/comments/2abwyt/smooth_colour_mandelbrot
"""

import numpy as np
from PIL import Image
from numba import jit


MAXITERS = 200
RADIUS = 100


@jit
def color(z, i):
    v = np.log2(i + 1 - np.log2(np.log2(abs(z)))) / 5
    if v < 1.0:
        return v**4, v**2.5, v
    else:
        v = max(0, 2-v)
        return v, v**1.5, v**3


@jit
def iterate(c):
    z = 0j
    for i in range(MAXITERS):
        if z.real*z.real + z.imag*z.imag > RADIUS:
            return color(z, i)
        z = z*z + c
    return 0, 0 ,0


def main(xmin, xmax, ymin, ymax, width, height):
    y, x = np.ogrid[ymax: ymin: height*1j, xmin: xmax: width*1j]
    z = x + y*1j
    red, green, blue = np.asarray(np.frompyfunc(iterate, 1, 3)(z)).astype(np.float)
    img = np.dstack((red, green, blue))
    Image.fromarray(np.uint8(img*255)).save('mandelbrot.png')


if __name__ == '__main__':
    main(-2.1, 0.8, -1.16, 1.16, 800, 640)
