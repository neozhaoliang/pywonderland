"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A kaleidoscope pattern with icosahedral symmetry
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import hsv_to_rgb


def Klein(z):
    """Klein's icosahedral invariants."""
    return (
        1728
        * (z * (z ** 10 + 11 * z ** 5 - 1)) ** 5
        / (-(z ** 20 + 1) + 228 * (z ** 15 - z ** 5) - 494 * z ** 10) ** 3
    )


def RiemannSphere(z):
    """Map the complex plane to Riemann's sphere via stereographic projection.
    """
    t = 1 + z.real * z.real + z.imag * z.imag
    return 2 * z.real / t, 2 * z.imag / t, 2 / t - 1


def Mobius(z):
    """Distort the resulting image by a Mobius transformation."""
    return (z - 20) / (3 * z + 1j)


def main(imgsize):
    y, x = np.ogrid[6 : -6 : imgsize * 2j, -6 : 6 : imgsize * 2j]
    z = x + y * 1j
    z = RiemannSphere(Klein(Mobius(Klein(z))))

    # define colors in hsv space
    H = np.sin(z[0] * np.pi) ** 2
    S = np.cos(z[1] * np.pi) ** 2
    V = abs(np.sin(z[2] * np.pi) * np.cos(z[2] * np.pi)) ** 0.2
    HSV = np.stack((H, S, V), axis=2)

    # transform to rgb space
    img = hsv_to_rgb(HSV)
    fig = plt.figure(figsize=(imgsize / 100.0, imgsize / 100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], aspect=1)
    ax.axis("off")
    ax.imshow(img)
    fig.savefig("kaleidoscope.png")


if __name__ == "__main__":
    main(imgsize=500)
