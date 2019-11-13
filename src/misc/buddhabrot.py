"""
~~~~~~~~~~~~~~~~~~~~~~
The Buddhebrot Fractal
~~~~~~~~~~~~~~~~~~~~~~
"""
import numpy as np
from numba import jit
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import tqdm


IMAGE_SIZE = 1200
ESCAPE_RADIUS = 1000
ITERATIONS = 1000
SUPER_SAMPLING = 12
XMIN, XMAX, YMIN, YMAX = -2, 1, -1.5, 1.5


@jit
def complex_to_pixel(c):
    """Find the pixel correspondes to a given complex number.
    """
    x = int((c.real - XMIN) / (XMAX - XMIN) * IMAGE_SIZE)
    y = int((c.imag - YMIN) / (YMAX - YMIN) * IMAGE_SIZE)
    return x, y


@jit
def escape(c):
    """Check if a complex number is in the escaping set.
       Return True if it escapes.
    """
    if (c.real + 1) * (c.real + 1) + c.imag * c.imag <= 0.0625:
        return False

    p = ((c.real - 0.25) * (c.real - 0.25) + c.imag * c.imag)**0.5
    if c.real <= p - (2 * p * p) + 0.25:
        return False

    z = 0
    for i in range(ITERATIONS):
        z = z*z + c
        if z.real * z.real + z.imag * z.imag > ESCAPE_RADIUS:
            return True
    return False


@jit
def iterate(c):
    """Get the orbit for a given complex number.
    """
    z = 0
    for i in range(1, ITERATIONS + 1):
        z = z*z + c
        if z.real * z.real + z.imag * z.imag > ESCAPE_RADIUS:
            break
        yield z


def main():
    M = np.zeros((IMAGE_SIZE, IMAGE_SIZE), np.complex)
    y, x = np.ogrid[YMAX: YMIN: IMAGE_SIZE*SUPER_SAMPLING*1j,
                    XMIN: XMAX: IMAGE_SIZE*SUPER_SAMPLING*1j]
    z = x + y*1j
    for c in tqdm.tqdm(z.flatten()):
        if escape(c):
            for z in iterate(c):
                x, y = complex_to_pixel(z)
                if 0 <= x < IMAGE_SIZE and 0 <= y < IMAGE_SIZE:
                    M[x, y] += c

    M /= (SUPER_SAMPLING * SUPER_SAMPLING)
    hue = (np.angle(M) / np.pi + 1) / 2
    x = np.minimum(1, np.absolute(M) / 18.0)
    H = hue
    S = np.maximum(np.minimum(1, 2 * (1 - np.tan(x))), 0)
    V = np.minimum(1, 2 * np.sin(x))
    V = np.power(V / np.max(V), 1/1.6)
    HSV = np.stack((H, S, V), axis=2)
    img = hsv_to_rgb(HSV)
    fig = plt.figure(figsize=(IMAGE_SIZE/100.0, IMAGE_SIZE/100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], aspect=1)
    ax.axis("off")
    ax.imshow(img, interpolation="bilinear")
    plt.show()
    fig.savefig("buddhabrot.png")


if __name__ == "__main__":
    main()
