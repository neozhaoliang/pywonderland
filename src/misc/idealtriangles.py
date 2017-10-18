# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Draw the (inf, inf, inf) Hyperbolic Tiling in Poincaré's disk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import numpy as np
import cairocffi as cairo
from collections import deque
from colorsys import hls_to_rgb


# The automaton that generates all words in the group
#  G = <A, B, C | A^2 = B^2 = C^2=1>.
# The starting state is omitted here.
automaton = {1: {"B": 2, "C": 3},
             2: {"A": 1, "C": 3},
             3: {"A": 1, "B": 2}}


def hue(x):
    """
    Return a rgb color given x between [0, 1].
    """
    return hls_to_rgb(x, 0.7, 0.9)


def degree_to_radian(*args):
    """Angle in degree --> angle in radian."""
    return [x * np.pi / 180 for x in args]
    

def circle_to_matrix(z, r):
    """
    Inversion about a circle can be viewed as the composition of the
    complex conjugation and a Mobius transformation, hence can be represented
    by a 2x2 complex matrix. This matrix is normalized to have determinat 1
    to avoid floating errors.
    """
    return np.array([[z, r**2 - abs(z)**2],
                     [1, -z.conjugate()]], dtype=np.complex) / r


def matrix_to_circle(matrix):
    """Return the circle corresponding to this matrix."""
    center = matrix[0, 0] / matrix[1, 0]
    radius = abs(1 / matrix[1, 0].real)
    return center, radius


def reflect(circle, mirror):
    """
    The inversion of a circle about another circle (called the mirror) is also
    a circle. This function returns the matrix that represents the resulting circle.
    """
    return np.dot(mirror, np.dot(circle.conjugate(), mirror))


def orthogonal_circle(alpha, beta):
    """
    alpha, beta: angles of two distinct points on the unit circle.

    return the matrix of the circle that passes through these 
    two points and is orthogonal to the unit circle.
    """
    z = complex(np.cos(alpha), np.sin(alpha))
    w = complex(np.cos(beta), np.sin(beta))
    center = 2 * (z - w) / (z * w.conjugate() - w * z.conjugate())
    radius = np.sqrt(center * center.conjugate() - 1)
    return circle_to_matrix(center, radius)


def traverse(verts, depth):
    """
    Given three points on the unit circle (by their angles alpha, beta and gamma),
    generate all words in the group and all the circles corresponding to them by 
    traversing over the automaton.
    """
    alpha, beta, gamma = verts
    mA = orthogonal_circle(alpha, beta)
    mB = orthogonal_circle(beta, gamma)
    mC = orthogonal_circle(gamma, alpha)
    
    def transform(circle, symbol):
        mirror = {"A": mA, "B": mB, "C": mC}[symbol]
        return reflect(circle, mirror)
    
    queue = deque([["A", 1, mA], ["B", 2, mB], ["C", 3, mC]])
    while queue:
        word, state, circle = queue.popleft()
        yield word, state, circle

        if len(word) < depth:
            for symbol, to in automaton[state].items():
                queue.append((word + symbol, to, transform(circle, symbol)))


def main(verts, depth, size):
    size = 600
    bg_color = (1, 1, 1)
    arc_color = (0, 0 ,0)
    funda_domain_color = (0.5, 0.5, 0.5)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    ctx = cairo.Context(surface)
    ctx.translate(size / 2.0, size / 2.0)
    ctx.scale(size / 2.0, -size / 2.0)
    ctx.set_source_rgb(*bg_color)
    ctx.paint()

    ctx.set_line_width(0.01)
    ctx.set_source_rgb(*arc_color)
    ctx.arc(0, 0, 1, 0, 2*np.pi)
    ctx.stroke_preserve()
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.fill_preserve()
    ctx.clip()
    
    for word, state, circle in traverse(verts, depth):
        d = len(word) - 1.0
        z, r =  matrix_to_circle(circle)
        ctx.arc(z.real, z.imag, r, 0, 2*np.pi)
        ctx.set_source_rgb(*hue(d / depth))
        ctx.fill_preserve()
        ctx.set_source_rgb(*arc_color)
        ctx.set_line_width((d + 2) * 0.005 / (d + 1))
        ctx.stroke()

    surface.write_to_png("infx3_tiling.png")


if __name__ == "__main__":
    main(# use three random points: verts=np.random.random(3) * 2 * np.pi,
         verts=degree_to_angle(90, 210, 330),
         depth=8,
         size=600)
