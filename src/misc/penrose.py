# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Draw generalized Penrose tilings using de Bruijn's pentagrid method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reference:

    Algebraic theory of Penrose's non-periodic tilings of the plane.
                                                     N.G. de Bruijn.

Usage: python penrose.py

Each time you run this script it outputs a different pattern,
these patterns are almost surely not isomorphic with each other.
"""
import itertools
import random
import numpy as np
import cairocffi as cairo


palette = ['#E41A1C', '#377EB8', '#4DAF4A', '#984EA3', '#FF7F00', '#FFFF33',
           '#A65628', '#F781BF', '#66C2A5', '#FC8D62', '#8DA0CB', '#E78AC3',
           '#A6D854', '#FFD92F', '#E5C494', '#B3B3B3']

WIDTH = 1200
HEIGHT = 720
NUM_LINES = 25
THIN_COLOR, FAT_COLOR, EDGE_COLOR = random.sample(palette, 3)
GRIDS = [np.exp(2j*np.pi*i/5) for i in range(5)]
SHIFTS = np.random.random(5)
BACKGROUND_COLOR = '#000000'
LINE_WIDTH = 0.1


def htmlcolor_to_rgb(s):
    if not (s.startswith('#') and len(s) == 7):
        raise ValueError("Bad html color format. Expected: '#RRGGBB' ")
    return [1.0 * int(n, 16) / 255 for n in (s[1:3], s[3:5], s[5:])]


def compute_rhombus(r, s, kr, ks):
    """
    Compute the vertices of a rhombus.
    0 <= r < s <= 4 are the indices of the two grids in `GRIDS`.
    kr, ks: indices of the two lines in the two grids specified by r, s.
    return: four vertices of the rhombus corresponding to
            the intersection of the two lines.
    """
    # The intersection point is the solution to a 2x2 linear equation:
    # Re(z/GRIDS[r]) + SHIFTS[r] = kr
    # Re(z/GRIDS[s]) + SHIFTS[s] = ks
    intersect_point = (GRIDS[r] * (ks - SHIFTS[s])
                     - GRIDS[s] * (kr - SHIFTS[r])) *1j / GRIDS[s-r].imag

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


def main():
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(LINE_WIDTH)
    scale = max(WIDTH, HEIGHT) / (2.0 * NUM_LINES)
    ctx.scale(scale, scale)
    ctx.translate(NUM_LINES, NUM_LINES)

    ctx.set_source_rgb(*htmlcolor_to_rgb(BACKGROUND_COLOR))
    ctx.paint()

    for r, s in itertools.combinations(range(5), 2):
        for kr, ks in itertools.product(range(-NUM_LINES, NUM_LINES + 1), repeat=2):
            # if s-r = 1 or 4 then this is a thin rhombus, otherwise it's fat.
            if (s-r == 1 or s-r == 4):
                color = htmlcolor_to_rgb(THIN_COLOR)
            else:
                color = htmlcolor_to_rgb(FAT_COLOR)

            ctx.set_source_rgb(*color)
            A, B, C, D = compute_rhombus(r, s, kr, ks)
            ctx.move_to(A.real, A.imag)
            ctx.line_to(B.real, B.imag)
            ctx.line_to(C.real, C.imag)
            ctx.line_to(D.real, D.imag)
            ctx.close_path()
            ctx.fill_preserve()

            ctx.set_source_rgb(*htmlcolor_to_rgb(EDGE_COLOR))
            ctx.stroke()

    print('shifts in the five directions:\n{}'.format(SHIFTS))
    print('thin color: {} fat color: {} edge color: {}'.format(THIN_COLOR, FAT_COLOR, EDGE_COLOR))
    surface.write_to_png('aperiodic_tiling.png')


if __name__ == '__main__':
    main()
