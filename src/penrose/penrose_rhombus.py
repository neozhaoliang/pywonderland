# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Standard Penrose Tiling by Fat and Thin Rhombus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

reference:

    "http://preshing.com/20110831/penrose-tiling-explained/"

"""
import cairocffi as cairo
import numpy as np


WIDTH = 800
HEIGHT = 640
NUM_SUBDIVISIONS = 6
FAT_COLOR = (0, 0.545, 0.545)
THIN_COLOR = (1.0, 0.078, 0.576) 
EDGE_COLOR = (0, 0, 0)
PHI = (np.sqrt(5) - 1) / 2


def subdivide(triangles):
    result = []
    for color, A, B, C in triangles:
        if color == 0:
            P = A + (B - A) * PHI
            result += [(0, C, P, B), (1, P, C, A)]
        else:
            Q = B + (A - B) * PHI
            R = B + (C - B) * PHI
            result += [(1, R, C, A), (1, Q, R, B), (0, R, Q, A)]
    return result


triangles = []
for i in range(10):
    B = np.exp((2*i - 1) * np.pi * 1j / 10)
    C = np.exp((2*i + 1) * np.pi * 1j / 10)
    if i % 2 == 0:
        B, C = C, B
    triangles.append((0, 0j, B, C))

for i in range(NUM_SUBDIVISIONS):
    triangles = subdivide(triangles)

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)
ctx.translate(WIDTH / 2.0, HEIGHT / 2.0)
extent = max(WIDTH, HEIGHT) / 1.5
ctx.scale(extent, extent)

color, A, B, C = triangles[0]
ctx.set_line_width(abs(B - A) / 10.0)
ctx.set_line_join(cairo.LINE_JOIN_ROUND)

for color, A, B, C in triangles:
    D = B + C - A
    ctx.move_to(A.real, A.imag)
    ctx.line_to(B.real, B.imag)
    ctx.line_to(D.real, D.imag)
    ctx.line_to(C.real, C.imag)
    ctx.close_path()
    if color == 0:
        ctx.set_source_rgb(*FAT_COLOR)
    else:
        ctx.set_source_rgb(*THIN_COLOR)
    ctx.fill_preserve()
    ctx.set_source_rgb(*EDGE_COLOR)
    ctx.stroke()

surface.write_to_png("penrose_rhombus.png")