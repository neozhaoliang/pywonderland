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


eps = 1e-12  # accuracy for comparison.

# The automaton that generates all words in the group
#  G = <A, B, C | A^2 = B^2 = C^2 = 1>.
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
    Inversion about a circle (or a line) can be viewed as the composition of the
    complex conjugation and a Mobius transformation, hence can be represented
    by a 2x2 complex matrix. This matrix is normalized to have determinat 1
    to avoid floating errors. In this function we deal with circles only.
    """
    return np.array([[z, r**2 - abs(z)**2],
                     [1, -z.conjugate()]], dtype=np.complex) / r


def matrix_to_circle(matrix):
    """
    Return the circle corresponding to this matrix. We deal with the two cases
    that whether the matrix represents a circle or a line.
    """
    if abs(matrix[1, 0]) < eps:  # so this is the matrix of a line.
        return matrix[0, 0] / abs(matrix[1, 1])
    else:
        center = matrix[0, 0] / matrix[1, 0]
        radius = abs(1 / matrix[1, 0])
        return center, radius


def reflect(circle, mirror):
    """
    The inversion of a circle/line about another circle/line (called the mirror) is also
    a circle/line. This function returns the matrix that represents the resulting circle.
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
    # is it a straight line?
    if abs(abs(alpha - beta) - np.pi) < eps:
        return np.array([[z, 0],
                         [0, z.conjugate()]])
    else:
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
    bg_color = (1, 1, 1)  # color outside the unit circle.
    arc_color = (0, 0 ,0)  # color of the arcs.
    funda_domain_color = (0.5, 0.5, 0.5)  # color of the fundamental domain.

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
    ctx.clip()  # only the region inside the unit circle will be shown.
    
    for word, state, circle in traverse(verts, depth):
        d = len(word) - 1.0
        try:
            z, r =  matrix_to_circle(circle)
            ctx.arc(z.real, z.imag, r, 0, 2*np.pi)
        except:
            # We must distinguish between the inner and outer side of a line.
            # We think the left hand of z is the inner part.
            # To fill the intersection of this half plane and the unit disk
            # we simply draw a 1x2 rectangle.
            z = matrix_to_circle(circle)
            ctx.move_to(z.real, z.imag)
            ctx.line_to(z.real - z.imag, z.real + z.imag)
            ctx.line_to(-z.real - z.imag, z.real - z.imag)
            ctx.line_to(-z.real, -z.imag)
            ctx.close_path()

        ctx.set_source_rgb(*hue(d / depth))
        ctx.fill_preserve()
        ctx.set_source_rgb(*arc_color)
        ctx.set_line_width((d + 2) * 0.005 / (d + 1))
        ctx.stroke()

    surface.write_to_png("infx3_tiling.png")


if __name__ == "__main__":
    main(# use three random points: verts=np.random.random(3) * 2 * np.pi,
         verts=degree_to_radian(90, 210, 330),
         depth=8,
         size=600)
