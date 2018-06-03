# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Domain Coloring of Complex Functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Coloring scheme adapted from

    "https://mathematica.stackexchange.com/questions/7275/how-can-i-generate-this-domain-coloring-plot"

One can easily verify the Argument Principle from the resulting image.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb


PI = np.pi
TWOPI = 2 * PI
CONTOUR = 1.0 / 0.25  # density of the white contour lines
GRID = 1.0 / 0.5  # density of the black grid lines


def domain_coloring(z):
    """
    Hue represents the argument, saturation represents the magnitude of the real and
    imag part of f(z), and bright white lines represent the magnitude of |f(z)|.
    """
    # hue increases from 0 to 1 as z walks counterclockwise from the x-axis.
    h = np.angle(z) / TWOPI
    ind = np.where(h < 0)
    h[ind] += 1.0

    s = np.abs(np.sin(np.abs(z) * PI * CONTOUR))
    b = np.sin(z.real * PI * GRID) * np.sin(z.imag * PI * GRID)
    b = np.sqrt(np.sqrt(np.abs(b)))
    b2 = 0.5 * (1 - s + b + np.sqrt(0.01 + (1 - s - b)**2))
    b2 = np.clip(b2, 0.0, 1.0)
    hsv = np.stack((h, np.sqrt(s), b2), axis=2)
    return hsv_to_rgb(hsv)


def complex_function(z):
    return (z - 1 - 1j) / (z + 1 + 1j)


def main(xmin, xmax, ymin, ymax, width, height, supersample=2):
    y, x = np.ogrid[ymax: ymin: height*supersample*1j, xmin: xmax: width*supersample*1j]
    z = x + y*1j
    z = complex_function(z)
    img = domain_coloring(z)

    fig = plt.figure(figsize=(width/100.0, height/100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], aspect=1)
    ax.axis("off")
    ax.imshow(img)
    fig.savefig("domain-coloring.png")


if __name__ == "__main__":
    main(xmin=-4, xmax=2, ymin=-4, ymax=2, width=600, height=600)
