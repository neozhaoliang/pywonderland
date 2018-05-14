# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Draw generalized Penrose tilings using de Bruijn's pentagrid method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reference:

    "Algebraic theory of Penrose's non-periodic tilings of the plane".
                                                     N.G. de Bruijn.

Each time you run this script it outputs a different pattern,
these patterns are almost surely not isomorphic with each other.
"""
import itertools
import numpy as np
import cairocffi as cairo


WIDTH = 800
HEIGHT = 640
GRIDS = [np.exp(2j * np.pi * i / 5) for i in range(5)]
SHIFTS = np.random.random(5)
NUM_LINES = 12
FAT_COLOR = (1.0, 0.5, 0.0)
THIN_COLOR = (0.894, 0.102, 0.11)
EDGE_COLOR = (0.216, 0.494, 0.72)


def compute_rhombus(r, s, kr, ks):
    """
    Compute the vertices of a rhombus.
    0 <= r < s <= 4 are the indices of the two grids in `GRIDS`.
    kr, ks: indices of the two lines in the two grids specified by r, s.
    return: four vertices of the rhombus corresponding to
            the intersection of the two lines.
    """
    # The intersection point is the solution to a 2x2 linear equation:
    # Re(z/GRIDS[r]) + shifts[r] = kr
    # Re(z/GRIDS[s]) + shifts[s] = ks
    intersect_point = (GRIDS[r] * (ks - SHIFTS[s])
                       - GRIDS[s] * (kr - SHIFTS[r])) * 1j / GRIDS[s-r].imag

    # 5 integers that indicate the position of the intersection point.
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

with open('./povray/rhombus.inc', 'w') as f:
    for r, s in itertools.combinations(range(5), 2):
        for kr, ks in itertools.product(range(-NUM_LINES, NUM_LINES), repeat=2):
            # if s-r = 1 or 4 then this is a thin rhombus, otherwise it's fat.
            if (s-r == 1 or s-r == 4):
                color = THIN_COLOR
                shape = 0
            else:
                color = FAT_COLOR
                shape = 1

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

surface.write_to_png("penrose_debruijn.png")
