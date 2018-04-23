# -*- coding: utf-8 -*-
import numpy as np
from geometry import gram_schimdt, reflection_matrix, get_mirrors
from todd_coxeter import CosetTable


polytopes = {
    "tetrahedron": (3, 3, 2),
    "cube": (4, 3, 2),
    "octahedron": (3, 4, 2),
    "dodecahedron": (5, 3, 2),
    "icosahedron": (3, 5, 2),
    "5-cell": (3, 3, 3),
    "8-cell": (4, 3, 3),
    "16-cell": (3, 3, 4),
    "24-cell": (3, 4, 3),
    "120-cell": (5, 3, 3),
    "600-cell": (3, 3, 5)
    }


class Polytope4d(object):

    def __init__(self, p, q, r, truncated=True):
        self.pqr = (p, q, r)
        self.build_group()
        self.build_geometry()
        self.truncated = truncated

    def build_group(self):
        p, q, r = self.pqr
        gens = list(range(8))
        rels = [[0, 2]*p, [2, 4]*q, [4, 6]*r,
                [0, 4]*2, [2, 6]*2, [0, 6]*2,
                [0, 0], [2, 2], [4, 4], [6, 6],
                [0, 1], [2, 3], [4, 5], [6, 7]]
        self.vtable = CosetTable(gens, rels, [[2], [4], [6]]).run()
        self.vwords = self.vtable.get_words()
        self.ewords = CosetTable(gens, rels, [[0], [4], [6]]).get_words()
        self.fwords = CosetTable(gens, rels, [[0], [2], [6]]).get_words()

    def build_geometry(self):
        """
        1. get the 4 reflection matrices.
        2. get the coordinates of all vertices.
        """
        # the 4 reflection matrices
        M = get_mirrors(*self.pqr)
        self.reflectors = [reflection_matrix(v) for v in M]
        # an initial vertex
        v0 = gram_schimdt(M[::-1])[-1]
        self.v0 = v0 / np.linalg.norm(v0)
        # all vertex coordinates
        self.vertex_coords = [self.transform(self.v0, word) for word in self.vwords]
        # an initial edge
        e0 = (0, self.map_vertex(0, (0,)))
        # get all edges
        self.edge_list = [tuple(self.map_vertex(v, word) for v in e0) for word in self.ewords]
        # an initial face
        f0 = [self.map_vertex(0, (0, 2)*i) for i in range(self.pqr[0])]
        # get all faces
        self.face_list = [tuple(self.map_vertex(v, word) for v in f0) for word in self.fwords]

    def transform(self, v, word):
        for w in word:
            v = np.dot(v, self.reflectors[w//2])
        return v

    def map_vertex(self, v, word):
        for w in word:
            v = self.vtable[v][w]
        return v

    def write_to_pov(self):
        with open("polytope_data.inc".format(*self.pqr), "w") as f:
            for v in self.vertex_coords:
                f.write("Vertex(<{}, {}, {}, {}>)\n".format(*v))

            for i, j in self.edge_list:
                s = self.vertex_coords[i]
                e = self.vertex_coords[j]
                f.write("Arc(<{}, {}, {}, {}>, <{}, {}, {}, {}>)\n".format(*np.concatenate((s, e))))


if __name__ == "__main__":
    p, q, r = polytopes["8-cell"]
    P = Polytope4d(p, q, r)
    P.write_to_pov()
