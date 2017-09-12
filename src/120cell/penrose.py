# pylint: disable=unused-import
# pylint: disable=undefined-variable

from itertools import combinations, product
import numpy as np
from vapory import *


class Penrose(object):

    GRIDS = [np.exp(2j * np.pi * i / 5) for i in range(5)]

    def __init__(self, num_lines, shift, thin_color, fat_color, **config):
        self.num_lines = num_lines
        self.shift = shift
        self.thin_color = thin_color
        self.fat_color = fat_color
        self.objs = self.compute_pov_objs(**config)


    def compute_pov_objs(self, **config):
        objects_pool = []

        for rhombi, color in self.tile():
            p1, p2, p3, p4 = rhombi
            polygon = Polygon(5, p1, p2, p3, p4, p1,
                              Texture(Pigment('color', color), config['default']))
            objects_pool.append(polygon)

            for p, q in zip(rhombi, [p2, p3, p4, p1]):
                cylinder = Cylinder(p, q, config['edge_thickness'], config['edge_texture'])
                objects_pool.append(cylinder)

            for point in rhombi:
                x, y = point
                sphere = Sphere((x, y, 0), config['vertex_size'], config['vertex_texture'])
                objects_pool.append(sphere)

        return Object(Union(*objects_pool))


    def rhombus(self, r, s, kr, ks):
        if (s - r)**2 % 5 == 1:
            color = self.thin_color
        else:
            color = self.fat_color

        point = (Penrose.GRIDS[r] * (ks - self.shift[s])
                 - Penrose.GRIDS[s] * (kr - self.shift[r])) *1j / Penrose.GRIDS[s-r].imag
        index = [np.ceil((point/grid).real + shift)
                 for grid, shift in zip(Penrose.GRIDS, self.shift)]

        vertices = []
        for index[r], index[s] in [(kr, ks), (kr+1, ks), (kr+1, ks+1), (kr, ks+1)]:
            vertices.append(np.dot(index, Penrose.GRIDS))

        vertices_real = [(z.real, z.imag) for z in vertices]
        return vertices_real, color


    def tile(self):
        for r, s in combinations(range(5), 2):
            for kr, ks in product(range(-self.num_lines, self.num_lines+1), repeat=2):
                yield self.rhombus(r, s, kr, ks)


    def put_objs(self, *args):
        return Object(self.objs, *args)
