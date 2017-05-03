'''
Draw generalized Penrose tilings using de Bruijn's pentagrid method.

Reference:

"Algebraic theory of Penrose's non-periodic tilings of the plane", N.G. de Bruijn.

Usage of this script: just run

    python penrose.py

each time you run this script it renders a different pattern,
these patterns are almost surely not isomorphic with each other.
'''
from itertools import combinations, product
import numpy as np
import random
import cairo



class GeneralizedPenroseTiling(object):

    def __init__(self, num_lines, shift, palette):
        '''
        num_lines:
            this integer determines the size of the region to be drawn.

        shift:
            five real numbers defining the shift in each direction,
            this tuple completely determines the resulting pattern.
            two tuples (a1, a2, a3, a4, a5) and (b1, b2, b3. b4, b5) determine isomorphic
            patterns if and only if
            (a1 + a2 + a3 + a4 + a5) - (b1 + b2 + b3 + b4 + b5) is an integer.

        palette:
            three colors (rgb tuples) for fat rhombus, thin rhombus and edges.
        '''
        self.num_lines = num_lines
        self.shift = shift
        self.thin_rhombus_color = palette[0]
        self.fat_rhombus_color  = palette[1]
        self.edge_color  = palette[2]
        self.grids = [np.exp(2j * np.pi * i / 5) for i in range(5)]


    def rhombus(self, r, s, kr, ks):
        '''
        Compute the four vertices and color of the rhombus corresponding to
        the intersection point of two grid lines.

        Here 0 <= r < s <= 4 indicate the two grids and
        ks, kr are line numbers in each grid.

        The intersection point is the solution to a 2x2 linear equation:

        Re(z/GRIDS[r]) + SHIFT[r] = kr
        Re(z/GRIDS[s]) + SHIFT[s] = ks
        '''

        # if s-r = 1 or 4 then this is a thin rhombus, otherwise it's fat.
        if (s - r)**2 % 5 == 1:
            color = self.thin_rhombus_color
        else:
            color = self.fat_rhombus_color

        # the intersection point
        point = (self.grids[r] * (ks - self.shift[s])
                 - self.grids[s] * (kr - self.shift[r])) *1j / self.grids[s-r].imag

        # 5 integers that indicate the intersection point's position:
        # the i-th integer n_i indicates that this point lies in the n_i-th strip
        # in the i-th grid.
        index = [np.ceil((point/grid).real + shift)
                 for grid, shift in zip(self.grids, self.shift)]

        # Be careful of the accuracy problem here:
        # Mathematically the r-th and s-th item of index should be kr and ks,
        # but programmingly it might not.
        # So we have to manually set them to be the correct values.
        vertices = []
        for index[r], index[s] in [(kr, ks), (kr+1, ks), (kr+1, ks+1), (kr, ks+1)]:
            vertices.append(np.dot(index, self.grids))

            vertices_real = [(z.real, z.imag) for z in vertices]

        return vertices_real, color


    def tile(self):
        '''
        Compute all rhombus lie in a given number of grid lines
        '''
        for r, s in combinations(range(5), 2):
            for kr, ks in product(range(-self.num_lines, self.num_lines+1), repeat=2):
                yield self.rhombus(r, s, kr, ks)


    def render(self, imgsize, filename):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, imgsize, imgsize)
        ctx = cairo.Context(surface)
        ctx.scale(imgsize/(2.0*self.num_lines), imgsize/(2.0*self.num_lines))
        ctx.translate(self.num_lines, self.num_lines)
        ctx.set_line_join(2)
        ctx.set_line_width(0.1)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()

        for rhombus, color in self.tile():
            A, B, C, D = rhombus
            ctx.move_to(*A)
            ctx.line_to(*B)
            ctx.line_to(*C)
            ctx.line_to(*D)
            ctx.line_to(*A)
            ctx.set_source_rgb(*color)
            ctx.fill_preserve()
            ctx.set_source_rgb(*self.edge_color)
            ctx.stroke()

        surface.write_to_png(filename)


if __name__ == '__main__':
    from palettable.colorbrewer.qualitative import Set1_8
    palette = random.sample(Set1_8.mpl_colors, 3)
    tiling = GeneralizedPenroseTiling(10, np.random.random(5), palette)
    tiling.render(imgsize=480, filename='penrose.png')
