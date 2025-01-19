"""
Reproduce the image from the article "Un ensemble-limite" by Audin, Michèle and Chéritat, Arnaud:
    https://images-archive.math.cnrs.fr/Un-ensemble-limite.html?lang=fr
"""

import numpy as np
from PIL import Image
from numba import jit


def rgb(a, b, c):
    return np.array([a, b, c]) / 255


BLACK = rgb(0, 0, 0)
RED = rgb(255, 0, 0)
VIOLET = rgb(100, 40, 180)
GREEN = rgb(0, 127, 0)
YELLOW = rgb(200, 200, 0)
BROWN = rgb(191, 127, 0)
LTGREEN = rgb(92, 224, 64)
LTVIOLET = rgb(200, 100, 255)

xmin, xmax = -1, 1
ymin, ymax = -1, 1
image_width = 1000
image_height = 1000
super_sampling_level = 4
curve_thickness = 2e-3

y, x = np.ogrid[
    ymax : ymin : image_height * super_sampling_level * 1j,
    xmin : xmax : image_width * super_sampling_level * 1j,
]
z = x + y * 1j

z2 = 0.068 - 0.272j
z3 = 0.426 - 0.672j
z4 = 0.816 + 0.362j
z5 = -1.154 + 0.854j
r1 = 0.4

d23 = abs(z3 - z2)
d34 = abs(z3 - z4)
d24 = abs(z4 - z2)
d45 = abs(z4 - z5)

r2 = (d23 + d24 - d34) / 2
r3 = (d23 + d34 - d24) / 2
r4 = (d24 + d34 - d23) / 2
r5 = d45 - r4

a = r5 + r1
b = r2 + r1
c = abs(z2 - z5)


class GeometryUtils:

    @staticmethod
    def find_third_vertex(z, w, a, b, c):
        """Given a triangle with side lengths a, b, c, and two vertices z and w,
        find the third vertex.
        """
        d = z - w
        d /= abs(d)
        k = (a * a - b * b + c * c) / (2 * c)
        h = (a * a - k * k) ** 0.5
        return w + d * (k - 1j * h)

    @staticmethod
    def circumcenter(A, B, C):
        """Get the circumcenter of three points A, B, C.
        See
            https://github.com/mapbox/delaunator/blob/main/index.js#L414
        """
        dx = B.real - A.real
        dy = B.imag - A.imag
        ex = C.real - A.real
        ey = C.imag - A.imag
        bl = dx * dx + dy * dy
        cl = ex * ex + ey * ey
        d = 0.5 / (dx * ey - dy * ex)
        x = A.real + (ey * bl - dy * cl) * d
        y = A.imag + (dx * cl - ex * bl) * d
        return complex(x, y)

    @staticmethod
    def get_touch_point(z1, r1, z2):
        d = z2 - z1
        d /= abs(d)
        return d * r1 + z1


z1 = GeometryUtils.find_third_vertex(z2, z5, a, b, c)
u24 = GeometryUtils.get_touch_point(z2, r2, z4)
u23 = GeometryUtils.get_touch_point(z2, r2, z3)
u34 = GeometryUtils.get_touch_point(z3, r3, z4)
u12 = GeometryUtils.get_touch_point(z1, r1, z2)
u15 = GeometryUtils.get_touch_point(z1, r1, z5)
u45 = GeometryUtils.get_touch_point(z4, r4, z5)

points = (u12, u15, u23, u24, u34, u45)

zr1 = GeometryUtils.circumcenter(u23, u24, u34)
rr1 = abs(u24 - zr1)

u2412 = u24 - u12
u4524 = u45 - u24
u1545 = u15 - u45
u1215 = u12 - u15

circles = ((z1, r1), (z2, r2), (z3, r3), (z4, r4), (z5, r5))


@jit
def region1(z):
    """The first fundamental domain inside the three circles at z2, z3, z4"""
    return abs(z - zr1) < rr1


@jit
def region2(z):
    """The second fundamental domain surrounded by the four circles at z1, z2, z4, z5."""
    return (
        ((z.imag - u12.imag) * u2412.real - (z.real - u12.real) * u2412.imag) > 0
        and ((z.imag - u24.imag) * u4524.real - (z.real - u24.real) * u4524.imag) > 0
        and ((z.imag - u45.imag) * u1545.real - (z.real - u45.real) * u1545.imag) > 0
        and ((z.imag - u15.imag) * u1215.real - (z.real - u15.real) * u1215.imag) > 0
    )


@jit
def smoothstep(a, b, x):
    """glsl `smoothstep` function."""
    y = min(max((x - a) / (b - a), 0), 1)
    return (3 - 2 * y) * y * y


@jit
def mix(x, y, a):
    """glsl `mix` function."""
    return x * (1 - a) + y * a


@jit
def invert(z, cen, r, scale):
    """Inversion in a circle."""
    k = (r * r) / abs(z - cen) ** 2
    scale *= k
    return cen + k * (z - cen), scale


@jit
def iterate(z):
    w = z
    count = 0
    color = RED
    scale = 1.0
    for _ in range(1000):
        for p in points:
            if scale < 1e3 and abs(z - p) / scale < curve_thickness:
                return BLACK[0], BLACK[1], BLACK[2]
        found = True
        for cen, r in circles:
            if abs(z - cen) < r:
                z, scale = invert(z, cen, r, scale)
                count += 1
                found = False

        if found:
            if region1(z):
                color = BROWN if count % 2 == 0 else YELLOW
            elif region2(z):
                color = GREEN if count % 2 == 0 else LTGREEN
            else:
                color = VIOLET if count % 2 == 0 else LTVIOLET
            break

    d = 1e5
    for cen, rad in circles:
        d1 = abs(abs(w - cen) - rad) - 0.0015
        d = min(d, d1)

    d = smoothstep(0, 0.001, d)
    color = mix(np.ones(3), color, d)
    return color[0], color[1], color[2]


R, G, B = np.asarray(np.frompyfunc(iterate, 1, 3)(z)).astype(float)
img = np.stack((R, G, B), axis=2)
Image.fromarray(np.uint8(img * 255)).resize((image_width, image_height)).save(
    "klein_limit_set.png"
)
