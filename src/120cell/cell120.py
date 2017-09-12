# pylint: disable=unused-import
# pylint: disable=undefined-variable

import numpy as np
from vapory import *
from data import VERTS, EDGES, FACES


class Cell_120(object):

    def __init__(self, **config):
        # north pole for stereographic projection
        self.pole = 2
        # project to 3d
        self.verts_3d = np.array([self.stereo_projection(v) for v in VERTS])
        # the lowest point
        Cell_120.bottom = min(v[2] for v in self.verts_3d)
        self.objs = self.compute_pov_objs(**config)


    def stereo_projection(self, v):
        x, y, z, w = v
        return np.array([x, y, z]) * 4 * self.pole / (w - 2 * self.pole)


    def compute_pov_objs(self, **config):
        # firstly the vertices
        verts_pool = []
        for v in self.verts_3d:
            ball = Sphere(v, config['vertex_size'])
            verts_pool.append(ball)

        verts = Object(Union(*verts_pool), config['vertex_texture'])

        # and the edges
        edges_pool = []
        for i, j in EDGES:
            u, v = self.verts_3d[i], self.verts_3d[j]
            edge = Cylinder(u, v, config['edge_thickness'])
            edges_pool.append(edge)

        edges = Object(Union(*edges_pool), config['edge_texture'])

        # finally the faces
        faces_pool = []
        for f in FACES:
            pentagon_verts = [self.verts_3d[index] for index in f]
            pentagon = Polygon(5, *pentagon_verts)
            faces_pool.append(pentagon)

        faces = Object(Union(*faces_pool), config['face_texture'], config['interior'])
        return Object(Union(verts, edges, faces))


    def put_objs(self, *args):
        return Object(self.objs, *args)
