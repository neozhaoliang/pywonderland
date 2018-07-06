# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Draw aperiodic tilings using de Bruijn's algebraic approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reference:

  "Algebraic theory of Penrose's non-periodic tilings of the plane".
                                                     N.G. de Bruijn.

Usage:
    Firstly run

        python debruijn.py

    This will output a .png image of a rhombus tiling rendered by cairo
    and a POV-Ray include file "rhombus.inc" that contains the data of
    the rhombus, then go to the folder "/povray" and run the file
    "scene.pov" with POV-Ray, for example in command line:

        povray scene.pov +W800 +H600 +Q11 +A0.001 +R5

    Each time you run this script it outputs a different pattern,
    these patterns are almost surely not isomorphic with each other.

Some params you can tweak with:

    1. 'DIMENSION'.
    2. 'SHIFTS' of the grids.
    3. Colors for the different rhombus.

:copyright: by Zhao Liang, 2018.
"""
import itertools
import cairocffi as cairo
import numpy as np


PI = 3.14159265358979

WIDTH = 800
HEIGHT = 640
NUM_LINES = 12

DIMENSION = 8  # you can change this to any integer >=2 but usually <= 12

if DIMENSION % 2 == 0:
    GRIDS = [np.exp(PI * 1j * i / DIMENSION) for i in range(DIMENSION)]
else:
    GRIDS = [np.exp(PI * 2j * i / DIMENSION) for i in range(DIMENSION)]

SHIFTS = np.random.random(DIMENSION)

FACE_COLOR_1 = (1.0, 0.5, 0.0)
FACE_COLOR_2 = (0.894, 0.102, 0.11)
FACE_COLOR_3 = (0.59, 0.9, 0.42)
FACE_COLOR_4 = (0.13, 0.28, 0.41)
EDGE_COLOR   = (0.216, 0.494, 0.72)


def compute_rhombus(r, s, kr, ks):
    """
    Compute the coordinates of the four vertices of the rhombus that
    correspondes to the intersection point of the kr-th line in the r-th
    grid and the ks-th line in the s-th grid. Here r, s, kr, ks are all
    integers and 0 <= r < s <= DIMENSION and -NUM_LINES <= kr, ks <= NUM_LINES.

    The intersection point is the solution to a 2x2 linear equation:
        Re(z/grids[r]) + shifts[r] = kr
        Re(z/grids[s]) + shifts[s] = ks
    """
    # The intersection point
    intersect_point = (GRIDS[r] * (ks - SHIFTS[s])
                       - GRIDS[s] * (kr - SHIFTS[r])) * 1j / GRIDS[s-r].imag

    # the list of integers that indicate the position of the intersection point.
    # the i-th integer n_i indicates that this point lies in the n_i-th strip
    # in the i-th grid.
    index = [np.ceil((intersect_point/grid).real + shift)
             for grid, shift in zip(GRIDS, SHIFTS)]

    # Be careful of the accuracy problem here.
    # Mathematically the r-th and s-th item of index should be kr and ks,
    # but programmingly it might not be the case,
    # so we have to manually set them to be the correct values.
    return [np.dot(index, GRIDS) for index[r], index[s] in
            [(kr, ks), (kr+1, ks), (kr+1, ks+1), (kr, ks+1)]]


surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context(surface)
ctx.set_line_cap(cairo.LINE_CAP_ROUND)
ctx.set_line_join(cairo.LINE_JOIN_ROUND)
ctx.set_line_width(0.1)
scale = max(WIDTH, HEIGHT) / (2.0 * NUM_LINES)
ctx.scale(scale, scale)
ctx.translate(NUM_LINES, NUM_LINES)

with open("./povray/rhombus.inc", "w") as f:
    for r, s in itertools.combinations(range(DIMENSION), 2):
        for kr, ks in itertools.product(range(-NUM_LINES, NUM_LINES), repeat=2):
            if (s-r == 1 or s-r == DIMENSION - 1):
                color = FACE_COLOR_1
                shape = 0
            elif (s-r == 2 or s-r == DIMENSION - 2):
                color = FACE_COLOR_2
                shape = 1
            elif (s-r == 3 or s-r == DIMENSION - 3):
                color = FACE_COLOR_3
                shape = 2
            else:
                color = FACE_COLOR_4
                shape = 3

            ctx.set_source_rgb(*color)
            A, B, C, D = compute_rhombus(r, s, kr, ks)
            ctx.move_to(A.real, A.imag)
            ctx.line_to(B.real, B.imag)
            ctx.line_to(C.real, C.imag)
            ctx.line_to(D.real, D.imag)
            ctx.close_path()
            ctx.fill_preserve()

            ctx.set_source_rgb(*EDGE_COLOR)
            ctx.stroke()

            f.write("Rhombus(<%f, %f>, <%f, %f>, <%f, %f>, <%f, %f>, %d)\n"
                    % (A.real, A.imag, B.real, B.imag, C.real, C.imag, D.real, D.imag, shape))

surface.write_to_png("debruijn.png")
