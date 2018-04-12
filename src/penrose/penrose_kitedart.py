# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Penrose Tiling by Kites and Darts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import cairocffi as cairo
import numpy as np


WIDTH = 800
HEIGHT = 640
NUM_SUBDIVISIONS = 6
PHI = (np.sqrt(5) - 1) / 2
KITE_COLOR = (1.0, 0.078, 0.576)
DART_COLOR = (0, 0.545, 0.545)
EDGE_COLOR = (0, 0, 0)


def reflect(A, B, C):
    """Reflect a point A across the line passing through B and C."""
    def cdot(z, w):
        return (z * w.conjugate()).real

    n = (C - B) / abs(C - B)
    t = cdot(A - B, n)
    return 2 * (B + t * n) - A


def subdivide_kite_dart(triangles):
    result = []
    for color, A, B, C in triangles:
        if color == 0:
            # subdivide sharp isosceles (half kite) triangle
            Q = A + (B - A) * PHI
            R = B + (C - B) * PHI
            result += [(1, R, Q, B), (0, Q, A, R), (0, C, A, R)]
        else:
            # subdivide fat isosceles (half dart) triangle
            P = C + (A - C) * PHI
            result += [(1, B, P, A), (0, P, C, B)]

    return result


triangles = []
for i in range(10):
    B = np.exp((2*i - 1) * np.pi * 1j / 10)
    C = np.exp((2*i + 1) * np.pi * 1j / 10)
    if i % 2 == 0:
        B, C = C, B
    triangles.append((0, B, 0j, C))  # note the order of the vertices here!

# perform subdivisions
for i in range(NUM_SUBDIVISIONS):
    triangles = subdivide_kite_dart(triangles)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)
ctx.translate(WIDTH / 2.0, HEIGHT / 2.0)
extent = max(WIDTH, HEIGHT) / 1.2
ctx.scale(extent, extent)

color, A, B, C = triangles[0]
ctx.set_line_width(abs(B - A) / 10.0)
ctx.set_line_join(cairo.LINE_JOIN_ROUND)

for color, A, B, C in triangles:
    D = reflect(A, B, C)
    ctx.move_to(A.real, A.imag)
    ctx.line_to(B.real, B.imag)
    ctx.line_to(D.real, D.imag)
    ctx.line_to(C.real, C.imag)
    ctx.close_path()
    if color == 0:
        ctx.set_source_rgb(*KITE_COLOR)
    else:
        ctx.set_source_rgb(*DART_COLOR)
    ctx.fill_preserve()
    ctx.set_source_rgb(*EDGE_COLOR)
    ctx.stroke()

surface.write_to_png("penrose_kitedart.png")
