"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Plot domain coloring images of complex functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adapted from Reusser's work at

    "https://observablehq.com/@rreusser"

"""

import numpy as np
from numpy import sin, cos, pi

from PIL import Image


image_width = 1200
image_height = 960
num_octaves = 4
num_steps = 8
zoom_factor = 10
xmin, xmax = -3, 3
aspect = image_height / image_width
ymax = xmax * aspect
ymin = xmin * aspect
super_sampling = 2
grid_opacity = 0.5
shading_opacity = 0.16


def complex_function(z):
    """
    The complex function to plot. *You can write any function here*.
    :param z: a numpy 2d array of complex numbers.
    """
    return (z - 1) / (z + 1)


def mix(x, y, a):
    """glsl `mix` function.
    """
    return x * (1 - a) + y * a


def smoothstep(a, b, x):
    """glsl `smoothstep` function.
    """
    y = np.clip((x - a) / (b - a), 0, 1)
    return (3 - 2 * y) * y * y


def colormap(t):
    """Map each entry of a 2d-array `t` to a rgb triple.
    """
    x = 2 * pi * t - 1.74533
    y = (0.25 * cos(2 * pi * t) + 0.25) * (-1.5) + 1.5
    z = (0.25 * cos(2 * pi * t) + 0.25) * (-0.9) + 0.8
    sx, cx = sin(x), cos(x)
    w = z * (1 + y * (1 - z))
    X = w * (sx * 0.14861 + cx * 1.78277)
    Y = w * (sx * 0.29227 - cx * 0.90649)
    Z = w * (sx * -1.97294)
    return np.stack((X, Y, Z), axis=2)


def checker(z):
    """
    :param z: a 2d array of complex type.
    For each entry in z, it lies in an unique unit square with left-bottom corner
    at lattice site (m, n) where (m, n) are both integers. Return a bool array of
    the same shape with its corresponding entry is True if m, n have the same parity
    else it's False.
    """
    fx = ((z.real / 2) % 1) * 2 - 1
    fy = ((z.imag / 2) % 1) * 2 - 1
    return fx * fy > 0


def grid_distance_function(z):
    """Return the absolute distance of z to the nearest horizontal and
    vertical grid lines.
    """
    fx = (z.real - 0.5) % 1 - 0.5
    fy = (z.imag - 0.5) % 1 - 0.5
    return abs(fx) + abs(fy) * 1j


def gradient_magnitude(fz):
    """Compute the magnitude of the gradients of a 2d array fz.
    """
    dx = np.absolute(np.diff(fz, axis=1, append=0))
    dy = np.absolute(np.diff(fz, axis=0, prepend=0))
    return np.maximum(np.sqrt(dx * dx + dy * dy), 1e-20)


def main():
    y, x = np.ogrid[ymax: ymin: image_height * super_sampling * 1j,
                    xmin: xmax: image_width * super_sampling * 1j]
    z = x + y * 1j
    fz = complex_function(z)
    grad_mag = gradient_magnitude(fz)
    continous_scale = np.log2(grad_mag) / np.log2(num_steps)
    discrete_scale = np.floor(continous_scale)
    fract_scale = 1 - (continous_scale - discrete_scale)
    base_scale = np.power(num_steps, -discrete_scale) / zoom_factor
    grid_scale = np.power(num_steps, fract_scale)

    total_weights = np.zeros_like(z, dtype=float)
    shading = np.zeros_like(z, dtype=float)
    grid = np.zeros_like(z, dtype=complex)
    octave_scale = 1

    for i in range(num_octaves):
        w0 = 1e-4 if i == 0 else i + 1
        w1 = 1e-4 if i == num_octaves - 1 else i + 2
        w = mix(w0, w1, fract_scale)
        total_weights += w

        value = fz * base_scale * octave_scale
        slope = zoom_factor * grid_scale / (octave_scale * num_steps)
        xygrid = grid_distance_function(value) * slope
        grid += w * (smoothstep(2, 0, xygrid.real) + smoothstep(2, 0, xygrid.imag) * 1j)
        shading += w * checker(value)
        octave_scale /= num_steps

    shading /= total_weights
    grid *= grid_opacity / total_weights
    args = np.angle(fz) / pi

    gamma = 0.454
    color = np.clip(colormap(args / 2 - 0.25), 0, 1)
    color = mix(1, color, 0.8)
    color = np.power(color, gamma)
    color = mix(1, color, 0.97)
    shade = mix(1, shading, shading_opacity)
    grid = np.maximum(grid.real, grid.imag)
    color = np.clip(
        mix(color * np.stack([shade]*3, axis=2),
            np.zeros_like(color),
            np.stack([grid]*3, axis=2)
        ), 0, 1
    )
    color = np.power(color, 1 / gamma)
    Image.fromarray(np.uint8(255 * color)).resize((image_width, image_height)).save("domain_coloring.png")


if __name__ == "__main__":
    main()
