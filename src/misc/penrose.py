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

from itertools import combinations, product
import numpy as np
import random
import cairocffi as cairo
from palettable.colorbrewer.qualitative import Set1_8


def tile(girds, shifts, nlines):
    """Generate all rhombi that lie in a given number of grid lines."""
    for r, s in combinations(range(5), 2):
        for kr, ks in product(range(-nlines, nlines+1), repeat=2):
            # if s-r = 1 or 4 then this is a thin rhombus, otherwise it's fat.
            if (s-r == 1 or s-r == 4):
                shape = 1
            else:
                shape = 0

            # The intersection point is the solution to a 2x2 linear equation:
            # Re(z/grids[r]) + shifts[r] = kr
            # Re(z/grids[s]) + shifts[s] = ks
            point = (grids[r] * (ks - shifts[s])
                     - grids[s] * (kr - shifts[r])) *1j / grids[s-r].imag

            # 5 integers that indicate the position of the intersection point.
            # the i-th integer n_i indicates that this point lies in the n_i-th strip
            # in the i-th grid.
            index = [np.ceil((point/grid).real + shift)
                     for grid, shift in zip(grids, shifts)]

            # Be careful of the accuracy problem here.
            # Mathematically the r-th and s-th item of index should be kr and ks,
            # but programmingly it might not be the case,
            # so we have to manually set them to be the correct values.
            verts = []
            for index[r], index[s] in [(kr, ks), (kr+1, ks), (kr+1, ks+1), (kr, ks+1)]:
                verts.append(np.dot(index, grids))

            yield verts, shape 
            

def render(imgsize, nlines, grids, shifts, palette, filename):
    """
    imgsize: (width, height) of the image in pixels.
    nlines: label of the lines in each grid ranges from `-nlines` to `nlines`.
    grids: five complex numbers specify the directions of the grids.
    shifts: five real numbers specify the shift of each grid.
    palette: three colors for thin, fat rhombi and their edges.
    filename: outputs filename.
    """
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, *imgsize)
    ctx = cairo.Context(surface)
    max_size = max(imgsize)
    ctx.scale(max_size/(2.0*nlines), max_size/(2.0*nlines))
    ctx.translate(nlines, nlines)
    ctx.set_line_join(2)
    ctx.set_line_width(0.1)

    thin_color, fat_color, edge_color = palette

    for rhombus, shape in tile(grids, shifts, nlines):
        A, B, C, D = rhombus
        ctx.move_to(A.real, A.imag)
        ctx.line_to(B.real, B.imag)
        ctx.line_to(C.real, C.imag)
        ctx.line_to(D.real, D.imag)
        ctx.line_to(A.real, A.imag)
        if shape == 1:
            ctx.set_source_rgb(*thin_color)
        else:
            ctx.set_source_rgb(*fat_color)

        ctx.fill_preserve()
        ctx.set_source_rgb(*edge_color)
        ctx.stroke()

    surface.write_to_png(filename)


if __name__ == '__main__':
    palette = random.sample(Set1_8.mpl_colors, 3)
    grids = [np.exp(2j*np.pi*i/5) for i in range(5)]
    # if the five real numbers in `shifts` sum to an integer then
    # it's the famous Penrose tiling.
    shifts = np.random.random(5)
    #shifts = (0.5, 0.5, 0.5, 0.5, 0.5)
    render(imgsize=(800, 400), nlines=30, grids=grids,
           shifts=shifts, palette=palette, filename='penrose.png')
