# -*- coding: utf-8 -*-
"""
This file contains various kinds of 3d and 4d polytopes.
"""
from itertools import combinations
import numpy as np
from todd_coxeter import CosetTable
import helpers


def check_duplicate_face(f, l):
    """Remove duplicated faces in a list l."""
    for _ in range(len(f)):
        if f in l or f[::-1] in l:
            return True
        f = f[-1:] + f[:-1]
    return False


def get_color(i):
    return np.random.random(3)


class BasePolytope(object):

    def __init__(self, upper_triangle, init_dist):
        # the Coxeter matrix
        self.coxeter_matrix = helpers.get_coxeter_matrix(upper_triangle)
        
        # the reflection mirrors
        self._mirrors = helpers.get_mirrors(self.coxeter_matrix)
        
        # reflection transformations about the mirrors
        self._reflections = tuple(helpers.reflection_matrix(v) for v in self._mirrors)
        
        # coordinates of the initial vertex
        self.init_v = helpers.get_init_point(self._mirrors, init_dist)
        
        # a bool list holds if a mirror is active or not.
        self.active = tuple(bool(x) for x in init_dist)
        
        dim = len(self.coxeter_matrix)
        
        # generators of the Coxeter group
        self.symmetry_gens = tuple(range(dim))
        
        # relations between the generators
        self.symmetry_rels = tuple((i, j) * self.coxeter_matrix[i][j]
                                   for i, j in combinations(self.symmetry_gens, 2))
        
        # to be calculated later
        self._vtable = None
        
        self.num_vertices = None
        self.vertex_coords = []
        
        self.num_edges = None
        self.edge_indices = []
        self.edge_coords = []
        
        self.num_faces = None
        self.face_indices = []
        self.face_coords = []

    def build_geometry(self, edge=True, face=True):
        self.get_vertices()
        if edge:
            self.get_edges()
        if face:
            self.get_faces()
    
    def get_vertices(self):
        # generators for the stabilizing subgroup of the initial vertex.
        vgens = [(i,) for i, active in enumerate(self.active) if not active]
        self._vtable = CosetTable(self.symmetry_gens, self.symmetry_rels, vgens)
        self._vtable.run()
        words = self._vtable.get_words()
        self.num_vertices = len(words)
        self.vertex_coords = tuple(self._transform(self.init_v, w) for w in words)
        
    def get_edges(self):
        for i, active in enumerate(self.active):
            if active:
                egens = [(i,)]
                etable = CosetTable(self.symmetry_gens, self.symmetry_rels, egens)
                etable.run()
                words = etable.get_words()
                elist = []
                for word in words:
                    # two ends of this edge
                    v1 = self._move(0, word)
                    v2 = self._move(0, (i,) + word)
                    # remove duplicates
                    if (v1, v2) not in elist and (v2, v1) not in elist:
                        elist.append((v1, v2))
                self.edge_indices.append(elist)
                self.edge_coords.append([(self.vertex_coords[x], self.vertex_coords[y])
                                         for x, y in elist])
        self.num_edges = sum([len(elist) for elist in self.edge_indices])

    def get_faces(self):
        for i, j in combinations(self.symmetry_gens, 2):
            f0 = []  # the base face that contains the initial vertex
            if self.active[i] and self.active[j]:
                fgens = [(i, j)]
                for k in range(self.coxeter_matrix[i][j]):
                    f0.append(self._move(0, (i, j)*k))
                    f0.append(self._move(0, (j,) + (i, j)*k))    
            elif self.active[i] and self.coxeter_matrix[i][j] > 2:
                fgens = [(i, j), (i,)]
                for k in range(self.coxeter_matrix[i][j]):
                    f0.append(self._move(0, (i, j)*k))
            elif self.active[j] and self.coxeter_matrix[i][j] > 2:
                fgens = [(i, j), (j,)]
                for k in range(self.coxeter_matrix[i][j]):
                    f0.append(self._move(0, (i, j)*k))
            else:
                continue
            
            ftable = CosetTable(self.symmetry_gens, self.symmetry_rels, fgens)
            ftable.run()
            words = ftable.get_words()
            flist = []
            for w in words:
                f = tuple(self._move(v, w) for v in f0)
                if not check_duplicate_face(f, flist):
                    flist.append(f)
            self.face_indices.append(flist)
            self.face_coords.append([tuple(self.vertex_coords[x] for x in face) for face in flist])
            
        self.num_faces = sum([len(flist) for flist in self.face_indices])
                                   
    def _transform(self, vector, word):
        """Transform a vector by a word in the symmetry group."""
        for w in word:
            vector = np.dot(vector, self._reflections[w])
        return vector 
  
    def _move(self, vertex, word):
        """
        Transform a vertex by a word in the symmetry group. 
        Return the index of the resulting vertex.
        """
        for w in word:
            vertex = self._vtable[vertex][w]
        return vertex
    
    def export_pov(self, filename):
        raise NotImplementedError
        
        
class Polyhedra(BasePolytope):

    def __init__(self, upper_triangle, init_dist):
        if not len(upper_triangle) == len(init_dist) == 3:
            raise ValueError("Three integers and three floats are required")

        super().__init__(upper_triangle, init_dist)

    def export_pov(self, filename="./povray/polyhedra-data.inc"):
        with open(filename, "w") as f:
            for v in self.vertex_coords:
                f.write("Vertex({})\n".format(helpers.pov_vector(v)))

            for i, edge_list in enumerate(self.edge_coords):
                for edge in edge_list:
                    f.write("Edge({}, {})\n".format(i, helpers.pov_vector_list(edge)))

            for i, face_list in enumerate(self.face_coords):
                for face in face_list:
                    f.write(helpers.export_pov_array(face))
                    f.write("Face({}, {}, vertices_list)\n".format(i, len(face)))


class Polychora(BasePolytope):

    def __init__(self, upper_triangle, init_dist):
        if not len(upper_triangle) == 6 and len(init_dist) == 4:
            raise ValueError("Six integers and four floats are required")

        super().__init__(upper_triangle, init_dist)
        
    def export_pov(self, filename="./povray/polychora-data.inc"):
        extent = np.max([np.linalg.norm(helpers.proj3d(v)) for v in self.vertex_coords])
        with open(filename, "w") as f:
            f.write("#declare extent = {}\n;".format(extent))
            
            for v in self.vertex_coords:
                f.write("Vertex({})\n".format(helpers.pov_vector(v)))

            for i, edge_list in enumerate(self.edge_coords):
                for edge in edge_list:
                    f.write("Edge({}, {})\n".format(i, helpers.pov_vector_list(edge)))
                    
            for i, face_list in enumerate(self.face_coords):
                for face in face_list:
                    f.write(helpers.export_pov_array(face))
                    isplane, center, radius, facesize = helpers.get_sphere_info(face)
                    facecolor = get_color(i)
                    f.write(helpers.export_polygon_face(i, face, isplane, center,
                                                        radius, facesize, facecolor))
