# -*- coding: utf-8 -*-
"""
This script computes the symmetry group and coordinates
of a given 3D/4D regular polytope and writes the data to
a .pov file for rendering.
"""
import numpy as np
from todd_coxeter import CosetTable
from geometry import gram_schimdt, reflection_matrix, get_mirrors


class Polytope(object):
    """
    A 3D polytope has Coxeter diagram * -- p -- * -- q -- *,
    A 4D polytope has Coxeter diagram * -- p -- * -- q -- * -- r -- *,
    The first case can be unified into the second one by viewing it
    as * -- p -- * -- q -- * -- 2 -- *.
    """
    shapes = {
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
        "600-cell": (3, 3, 5)}

    def __init__(self, name):
        p, q, r = Polytope.shapes[name]
        self.p = p
        self.q = q
        self.r = r

    def build(self):
        gens = list(range(8))
        rels = [[0, 2]*self.p, [2, 4]*self.q, [4, 6]*self.r,
                [0, 4]*2, [2, 6]*2, [0, 6]*2,
                [0, 0], [2, 2], [4, 4], [6, 6],
                [0, 1], [2, 3], [4, 5], [6, 7]]

        # 1. compute the three coset tables
        self.Vtable = CosetTable(gens, rels, [[2], [4], [6]])
        self.Vtable.run()
        self.Etable = CosetTable(gens, rels, [[0], [4], [6]])
        self.Etable.run()
        self.Ftable = CosetTable(gens, rels, [[0], [2], [6]])
        self.Ftable.run()

        # 2. get the words of these cosets
        self.Vwords = self.get_words(self.Vtable)
        self.Ewords = self.get_words(self.Etable)
        self.Fwords = self.get_words(self.Ftable)

        # 3. get the matrices of the reflections
        M = get_mirrors(self.p, self.q, self.r)
        self.reflectors = [reflection_matrix(v) for v in M]

        # 4. use Gram-Schimdt to find an initial vertex
        init_v = gram_schimdt(M[::-1])[-1]
        init_v /= np.linalg.norm(init_v)

        # 5. compute the vertex_indices and vertex_coords lists
        v0 = 0
        self.vertex_indices = tuple(range(len(self.Vtable)))
        self.vertex_coords = [self.transform(init_v, word) for word in self.Vwords]

        # 6. compute the edge_indices and edge_coords lists
        v1 = self.move(v0, (0,))  # the other end of an edge from v0
        e0 = (v0, v1)  # an initial edge
        self.edge_indices = [[self.move(v, word) for v in e0] for word in self.Ewords]
        self.edge_coords = []
        for i, j in self.edge_indices:
            start = self.vertex_coords[i]
            end = self.vertex_coords[j]
            self.edge_coords.append((start, end))

        # 7. compute the face_indices and face_coords lists
        f0 = tuple(self.move(v0, [0, 2]*i) for i in range(self.p))
        self.face_indices = [[self.move(v, word) for v in f0] for word in self.Fwords]
        self.face_coords = []
        for face in self.face_indices:
            self.face_coords.append(tuple(self.vertex_coords[i] for i in face))

    def transform(self, v, word):
        """Compute the coordinates of `v` transformed by `word`."""
        for w in word:
            v = np.dot(v, self.reflectors[w//2])
        return v

    def move(self, coset, word):
        """Compute the result of `coset` multiplied by `word`."""
        for w in word:
            coset = self.Vtable[coset][w]
        return coset

    @staticmethod
    def get_words(T):
        """
        Return the list of words that represent the cosets in a
        coset table `T`.
        """
        result = [None] * len(T)
        result[0] = tuple()
        q = [0]
        while len(q) > 0:
            coset = q.pop()
            for x in T.A[::2]:
                new_coset = T[coset][x]
                if result[new_coset] is None:
                    result[new_coset] = result[coset] + (x,)
                    q.append(new_coset)
        return result

    def export_graph(self):
        """Export the graph of this polytope."""
        with open("polytope-graph.txt", "w") as f:
            f.write("Vertices: {}\n".format(len(self.Vtable)))
            f.write("Edges: {}\n".format(len(self.Etable)))
            f.write("Faces: {}\n".format(len(self.Ftable)))
            for i, j in self.edge_indices:
                f.write("({}, {})\n".format(i, j))
            for face in self.face_indices:
                f.write("(" + ", ".join([str(i) for i in face]) + ")\n")

    def write_to_pov(self):
        with open("./povray/polytope-data.inc", "w") as f:
            for v in self.vertex_coords:
                f.write("Vertex(<{}, {}, {}, {}>)\n".format(*v))

            for u, v in self.edge_coords:
                f.write("Arc(<{}, {}, {}, {}>, <{}, {}, {}, {}>)\n".format(*np.concatenate((u, v))))


if __name__ == "__main__":
    P = Polytope("120-cell")
    P.build()
    P.write_to_pov()
