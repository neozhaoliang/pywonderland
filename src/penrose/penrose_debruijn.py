# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Draw generalized Penrose tilings using de Bruijn's pentagrid method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reference:

    Algebraic theory of Penrose's non-periodic tilings of the plane.
                                                     N.G. de Bruijn.

Usage: python penrose.py -size 800x800
                         -lines 15
                         -colors c1 c2 c3
                         -shifts s1 s2 s3 s4 s5
                         -output your-filename.png

Each time you run this script it outputs a different pattern,
these patterns are almost surely not isomorphic with each other.
"""
import itertools
import argparse
import numpy as np
import cairocffi as cairo


GRIDS = [np.exp(2j * np.pi * i / 5) for i in range(5)]
LINE_WIDTH = 0.1


def htmlcolor_to_rgb(s):
    if len(s) != 6:
        raise ValueError("Bad html color format. Expected: 'RRGGBB' ")
    return [int(n, 16) / 255.0 for n in (s[0:2], s[2:4], s[4:])]


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
    intersect_point = (GRIDS[r] * (ks - shifts[s])
                     - GRIDS[s] * (kr - shifts[r])) *1j / GRIDS[s-r].imag

    # 5 integers that indicate the position of the intersection point.
    # the i-th integer n_i indicates that this point lies in the n_i-th strip
    # in the i-th grid.
    index = [np.ceil((intersect_point/grid).real + shift)
             for grid, shift in zip(GRIDS, shifts)]

    # Be careful of the accuracy problem here.
    # Mathematically the r-th and s-th item of index should be kr and ks,
    # but programmingly it might not be the case,
    # so we have to manually set them to be the correct values.
    return [np.dot(index, GRIDS) for index[r], index[s] in
            [(kr, ks), (kr+1, ks), (kr+1, ks+1), (kr, ks+1)]]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-size', metavar='s', type=str, default='800x600',
                        help='size of the image')
    parser.add_argument('-lines', metavar='l', type=int, default=8,
                        help='half the number of lines in each grid')
    parser.add_argument('-colors', metavar='c', nargs=3, type=str,
                        default=['E41A1C', 'FF7F00', '377EB8'],
                        help='html colors for thin, fat rhombus and edges')
    parser.add_argument('-shifts', nargs=5, default=np.random.random(5), type=float,
                        help='five floating numbers specify the shifts of the grids')
    parser.add_argument('-output', metavar='o', type=str, default='penrose_rhombus.png',
                        help='output filenname')

    args = parser.parse_args()
    nlines = args.lines
    shifts = args.shifts
    width, height = [int(x) for x in args.size.split('x')]
    thin_color, fat_color, edge_color = args.colors

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.set_line_width(LINE_WIDTH)
    scale = max(width, height) / (2.0 * nlines)
    ctx.scale(scale, scale)
    ctx.translate(nlines, nlines)

    with open('rhombus.inc', 'w') as f:
        for r, s in itertools.combinations(range(5), 2):
            for kr, ks in itertools.product(range(-nlines, nlines), repeat=2):
                # if s-r = 1 or 4 then this is a thin rhombus, otherwise it's fat.
                if (s-r == 1 or s-r == 4):
                    color = htmlcolor_to_rgb(thin_color)
                    shape = 0
                else:
                    color = htmlcolor_to_rgb(fat_color)
                    shape = 1

                ctx.set_source_rgb(*color)
                A, B, C, D = compute_rhombus(r, s, kr, ks)
                ctx.move_to(A.real, A.imag)
                ctx.line_to(B.real, B.imag)
                ctx.line_to(C.real, C.imag)
                ctx.line_to(D.real, D.imag)
                ctx.close_path()
                ctx.fill_preserve()

                ctx.set_source_rgb(*htmlcolor_to_rgb(edge_color))
                ctx.stroke()

                f.write("Rhombus(<%f, %f>, <%f, %f>, <%f, %f>, <%f, %f>, %d)\n" \
                        % (A.real, A.imag, B.real, B.imag, C.real, C.imag, D.real, D.imag, shape))
    surface.write_to_png(args.output)
