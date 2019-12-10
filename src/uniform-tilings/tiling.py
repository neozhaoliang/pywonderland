from itertools import combinations
from functools import partial
import numpy as np
import helpers
from coxeter import CoxeterGroup


def rot(arr):
    return arr[1:] + [arr[0]]


class Face(object):

    """This class holds the information of a face and is
       used to color the faces alternatively.
    """

    def __init__(self, word, center, points, domain1, domain2):
        """
        word: the word in the symmetry group that transforms the fundamental face to
              this face.
        center: center of this face.
        points: coordinates of the vertices of this face.
        domain1 && domain2: alternate domains form the face.
        """
        self.word = word
        self.center = center
        self.points = points
        self.domain1 = domain1
        self.domain2 = domain2


class UniformTiling(object):

    def __init__(self, coxeter_diagram, init_dist):
        self.cox_mat = helpers.get_coxeter_matrix(coxeter_diagram)
        self.G = CoxeterGroup(self.cox_mat)
        self.active = tuple(bool(x) for x in init_dist)
        self.words = None

        self.mirrors = self.get_mirrors(coxeter_diagram)
        self.init_v = helpers.get_point_from_distance(self.mirrors, init_dist)
        self.reflections = self.get_reflections(init_dist)

        # to be calculated later
        self.vertices_coords = []
        self.num_vertices = None
        self.num_edges = None
        self.num_faces = None
        self.edge_indices = {}
        self.face_indices = {}

    def build_geometry(self, depth=None, maxcount=20000):
        self.G.init()
        self.words = tuple(self.G.traverse(depth, maxcount))
        self.get_vertices()
        self.get_edges()
        self.get_faces()

    def get_vertices(self):
        parabolic = tuple(i for i, x in enumerate(self.active) if not x)
        coset_reps = set([self.G.get_coset_representative(w, parabolic) for w in self.words])
        self.vwords = self.G.sort_words(coset_reps)
        self.vtable = self.G.get_coset_table(self.vwords, parabolic)
        self.num_vertices = len(self.vwords)
        self.vertices_coords = [self.transform(word, self.init_v) for word in self.vwords]

    def get_edges(self):
        for i in range(len(self.active)):
            if self.active[i]:
                elist = []
                coset_reps = set([self.G.get_coset_representative(w, (i,)) for w in self.words])
                for word in self.G.sort_words(coset_reps):
                    v1 = self.G.move(self.vtable, 0, word)
                    v2 = self.G.move(self.vtable, 0, word + (i,))
                    if v1 is not None and v2 is not None:
                        if (v1, v2) not in elist and (v2, v1) not in elist:
                            elist.append((v1, v2))

                self.edge_indices[i] = elist

        self.num_edges = sum(len(L) for L in self.edge_indices.values())

    def get_faces(self):
        for i, j in combinations(range(len(self.active)), 2):
            f0 = []
            m = self.cox_mat[i][j]
            parabolic = (i, j)
            if self.active[i] and self.active[j]:
                for k in range(m):
                    f0.append(self.G.move(self.vtable, 0, (i, j) * k))
                    f0.append(self.G.move(self.vtable, 0, (i, j) * k + (i,)))
            elif self.active[i] and m > 2:
                for k in range(m):
                    f0.append(self.G.move(self.vtable, 0, (j, i) * k))
            elif self.active[j] and m > 2:
                for k in range(m):
                    f0.append(self.G.move(self.vtable, 0, (i, j) * k))
            else:
                continue

            coset_reps = set([self.G.get_coset_representative(w, parabolic) for w in self.words])
            flist = []
            for word in self.G.sort_words(coset_reps):
                f = tuple(self.G.move(self.vtable, v, word) for v in f0)
                if None not in f and not helpers.check_duplicate_face(f, flist):
                    flist.append(f)

            self.face_indices[(i, j)] = flist

        self.num_faces = sum(len(L) for L in self.face_indices.values())

    def transform(self, word, v):
        for w in reversed(word):
            v = self.reflections[w](v)
        return v

    def get_reflections(self, init_dist):
        raise NotImplementedError

    def get_fundamental_triangle_vertices(self):
        raise NotImplementedError

    def project(self, v):
        raise NotImplementedError

    def get_mirrors(self, coxeter_diagram):
        raise NotImplementedError


class EuclideanTiling(UniformTiling):

    def project(self, v):
        return helpers.project_euclidean(v)

    def get_mirrors(self, coxeter_diagram):
        return helpers.get_spherical_or_affine_mirrors(coxeter_diagram)

    def get_reflections(self, init_dist):
        def reflect(v, normal, dist):
            """(affine) reflection.
            """
            return v - 2 * (np.dot(v, normal) + dist) * normal

        return [partial(reflect, normal=n, dist=d) for n, d in zip(self.mirrors, init_dist)]


class Poincare2D(UniformTiling):

    def __init__(self, coxeter_diagram, init_dist):
        super().__init__(coxeter_diagram, init_dist)
        # vertices of the fundamental triangle
        self.fundamental_triangle = self.get_fundamental_triangle_vertices()
        # middle points of the edges of the fundamental triangle
        self.edge_points = self.get_edge_points()

    def project(self, v):
        return helpers.project_hyperbolic(v)

    def get_mirrors(self, coxeter_diagram):
        return helpers.get_hyperbolic_mirrors(coxeter_diagram)

    def get_reflections(self, init_dist):
        def reflect(v, normal):
            """(affine) reflection.
            """
            return v - 2 * np.dot(v, normal) * normal

        return [partial(reflect, normal=n) for n in self.mirrors]

    def get_fundamental_triangle_vertices(self):
        return [helpers.get_point_from_distance(self.mirrors, d) for d in -np.eye(3)]

    def get_edge_points(self):
        d0 = (0, -1, -1)
        d1 = (-1, 0, -1)
        d2 = (-1, -1, 0)
        return [helpers.get_point_from_distance(self.mirrors, d) for d in (d0, d1, d2)]

    def get_faces(self):
        for i, j in combinations(range(len(self.active)), 2):
            f0 = []
            m = self.cox_mat[i][j]
            parabolic = (i, j)
            P1 = P2 = None
            c0 = self.fundamental_triangle[2 * (i + j) % 3]
            if self.active[i] and self.active[j]:
                P1 = self.edge_points[i]
                P2 = self.edge_points[j]
                for k in range(m):
                    f0.append(self.G.move(self.vtable, 0, (i, j) * k))
                    f0.append(self.G.move(self.vtable, 0, (i, j) * k + (i,)))
            elif self.active[i] and m > 2:
                P1 = self.edge_points[i]
                for k in range(m):
                    f0.append(self.G.move(self.vtable, 0, (j, i) * k))
            elif self.active[j] and m > 2:
                P2 = self.edge_points[j]
                for k in range(m):
                    f0.append(self.G.move(self.vtable, 0, (i, j) * k))
            else:
                continue

            coset_reps = set([self.G.get_coset_representative(w, parabolic) for w in self.words])
            flist = []
            for word in self.G.sort_words(coset_reps):
                f = tuple(self.G.move(self.vtable, v, word) for v in f0)
                if None not in f and not helpers.check_duplicate_face(f, flist):
                    center = self.transform(word, c0)
                    coords = [self.vertices_coords[k] for k in f]
                    coords2 = rot(coords)
                    if P1 is None or P2 is None:
                        mids = [helpers.normalize((P + Q) / 2) for P, Q in zip(coords, coords2)]
                        domain1 = [(V, P) for V, P in zip(coords, mids)]
                        domain2 = [(P, V) for P, V in zip(mids, coords2)]
                    else:
                        mids1 = [helpers.normalize((P + Q) / 2) for P, Q in zip(coords[::2], coords[1::2])]
                        mids2 = [helpers.normalize((P + Q) / 2) for P, Q in zip(coords[1::2], rot(coords[::2]))]
                        domain1 = [(Q1, V, Q2) for Q1, V, Q2 in zip(mids1, coords[1::2], mids2)]
                        domain2 = [(Q1, V, Q2) for Q1, V, Q2 in zip(mids2, rot(coords[::2]), rot(mids1))]

                    if len(word) % 2 == 1:
                        domain1, domain2 = domain2, domain1

                    face = Face(word, center, coords, domain1, domain2)
                    flist.append(face)

            self.face_indices[(i, j)] = flist

        self.num_faces = sum(len(L) for L in self.face_indices.values())


class SphericalTiling(UniformTiling):

    def project(self, v):
        return helpers.project_spherical(v)

    def get_mirrors(self, coxeter_diagram):
        return helpers.get_spherical_or_affine_mirrors(coxeter_diagram)

    def get_reflections(self, init_dist):
        def reflect(v, normal):
            """(affine) reflection.
            """
            return v - 2 * np.dot(v, normal) * normal

        return [partial(reflect, normal=n) for n in self.mirrors]
