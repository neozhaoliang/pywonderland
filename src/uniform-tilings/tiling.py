"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Generate uniform tilings via word processing in Coxeter groups
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script draws various 2D uniform tilings in euclidean, spherical
and hyperbolic (Poincaré disk model) spaces. The result is
exported to svg format. I also implemented a `render()` method
for each type of tiling to illustrate the usage.

Note: For star tilings different polygons may have overlapping
part in common, in my default implementaiton of the `render`
function the last rendered polygon will hide the region it
shares with other polygons, so the result may not look correct
in this case. This can be remedied by implementing another rendering
function for these star tilings.

:copyright (c) 2019 by Zhao Liang
"""
import os
from itertools import combinations
from functools import partial
import numpy as np
import cairocffi as cairo

# third-party module for drawing hyperbolic geodesic lines
import drawSvg
from hyperbolic import euclid
from hyperbolic.poincare.shapes import Polygon, Point, Line

# process bar
import tqdm
# color conversions
from colour import Color

from coxeter import CoxeterGroup
from dihedral import DihedralFace
import helpers


def get_euclidean_center_radius(P, hrad):
    """Compute the Euclidean center and radius of the circle
       centered at a point P with hyperbolic radius hrad.
    """
    r1 = np.tanh((P.hr + hrad) / 2)
    r2 = np.tanh((P.hr - hrad) / 2)
    R = (r1 + r2) / 2
    r = (r1 - r2) / 2
    return R * np.cos(P.theta), R * np.sin(P.theta), r


def dimmed(c):
    return Color(hue=c.hue, saturation=c.saturation, luminance=c.luminance*0.6)


def divide_line(hwidth, k):
    """Compute line strips for drawing edges of different types.
    """
    ewidth = np.tanh(hwidth / 2)
    if k == 1:
        x = 2 * np.arctanh(ewidth / 6)
        return x
    if k == 2:
        x1 = 2 * np.arctanh(ewidth / 10)
        x2 = 2 * np.arctanh(ewidth / 10 * 3)
        return x1, x2


class Tiling2D(object):

    def __init__(self, coxeter_diagram, init_dist):
        if len(coxeter_diagram) != 3 or len(init_dist) != 3:
            raise ValueError("Invalid input dimension")

        self.diagram = coxeter_diagram

        # Coxeter matrix and its rank
        self.cox_mat = helpers.get_coxeter_matrix(coxeter_diagram)
        self.rank = len(self.cox_mat)

        # generators of the symmetry group
        self.gens = tuple(range(self.rank))

        # symmetry group of this tiling
        self.G = CoxeterGroup(self.cox_mat)

        # a mirror is active iff the initial point is not on it
        self.active = tuple(bool(x) for x in init_dist)

        # reflection mirrors
        self.mirrors = self.get_mirrors(coxeter_diagram)

        # reflections (possibly affine) about the mirrors
        self.reflections = self.get_reflections()

        # coordinates of the initial point
        self.init_v = self.get_init_point(init_dist)

        # vertices of the fundamental triangle
        self.triangle_verts = self.get_fundamental_triangle_verts()

        # ----------------------
        # to be calculated later
        # ----------------------

        # holds the words in the symmetry group up to a given depth
        self.words = None

        # holds the coset representatives of the standard parabolic
        # subgroup of vertex-stabilizing subgroup
        self.vwords = None

        self.vertices_coords = []
        self.num_vertices = None
        self.num_edges = None
        self.num_faces = None
        self.edge_indices = {}
        self.face_indices = {}

    def vertex_at_mirrors(self, i, j):
        return 2 * (i + j) % 3

    def get_init_point(self, init_dist):
        raise NotImplementedError

    def get_mirrors(self, coxeter_diagram):
        raise NotImplementedError

    def get_fundamental_triangle_verts(self):
        raise NotImplementedError

    def build_geometry(self, depth=None, maxcount=20000):
        """Postpone the actual computations to this method.
        """
        self.G.init()
        self.word_generator = partial(self.G.traverse, depth=depth, maxcount=maxcount)
        self.get_vertices()
        self.get_edges()
        self.get_faces()
        return self

    def get_vertices(self):
        # generators of the vertex-stabilizing subgroup
        H = tuple(i for i, x in enumerate(self.active) if not x)
        # coset representatives of the vertex-stabilizing subgroup
        reps = set(self.word_generator(parabolic=H))
        # sort the words in shortlex order
        self.vwords = self.G.sort_words(reps)
        # build the coset table for these cosets
        self.vtable = self.G.get_coset_table(self.vwords, H)
        self.num_vertices = len(self.vwords)
        # apply each coset representative to the initial vertex
        self.vertices_coords = [self.transform(w, self.init_v) for w in self.vwords]

    def get_edges(self):
        """Compute the indices of the edges.
        """
        for i in self.gens:
            if self.active[i]:
                elist = set()
                H = (i,)  # edge-stabilizing subgroup
                reps = set(self.word_generator(parabolic=H))
                reps = self.G.sort_words(reps)
                for word in reps:
                    v1 = self.G.move(self.vtable, 0, word)
                    v2 = self.G.move(self.vtable, 0, word + (i,))
                    if v1 is not None and v2 is not None:
                        if v1 > v2:
                            v1, v2 = v2, v1
                        if (v1, v2) not in elist:
                            elist.add((v1, v2))

                self.edge_indices[i] = elist

        self.num_edges = sum(len(L) for L in self.edge_indices.values())

    def get_faces(self):
        """Compute the indices of the faces (and other information we will need).
        """
        for i, j in combinations(self.gens, 2):
            c0 = self.triangle_verts[self.vertex_at_mirrors(i, j)]
            f0 = []
            m = self.cox_mat[i][j]
            H = (i, j)
            type = 0
            if self.active[i] and self.active[j]:
                type = 1
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

            reps = set(self.word_generator(parabolic=H))
            reps = self.G.sort_words(reps)
            flist = set()
            for word in reps:
                f = tuple(self.G.move(self.vtable, v, word) for v in f0)
                if None not in f and set(f) not in flist:
                    center = self.transform(word, c0)
                    coords = [self.vertices_coords[k] for k in f]
                    face = DihedralFace(word, f, center, coords, type)
                    flist.add(face)

            self.face_indices[(i, j)] = flist

        self.num_faces = sum(len(L) for L in self.face_indices.values())

    def get_reflections(self):
        def reflect(v, normal):
            return v - 2 * np.dot(v, normal) * normal

        return [partial(reflect, normal=n) for n in self.mirrors]

    def transform(self, word, v):
        for w in reversed(word):
            v = self.reflections[w](v)
        return v

    def get_info(self):
        """Return some statistics of the tiling.
        """
        pattern = "{}-{}-{}".format(*self.diagram).replace("/", "|")
        info = ""
        info += "name: triangle group {}\n".format(pattern)
        info += "cox_mat: {}\n".format(self.cox_mat)
        info += "vertices: {}\n".format(self.num_vertices)
        info += "edges: {}\n".format(self.num_edges)
        info += "faces: {}\n".format(self.num_faces)
        info += "states in the automaton: {}\n".format(self.G.dfa.num_states)
        info += "reflection table:\n{}\n".format(self.G.reftable)
        info += "the automaton is saved as {}_dfa.png".format(pattern)
        self.G.dfa.draw(pattern + "_dfa.png")
        return info

    def render(self, *arg, **kwargs):
        raise NotImplementedError


class Poincare2D(Tiling2D):

    """Uniform tilings in Poincaré hyperbolic disk model.
    """

    def project(self, v):
        return helpers.project_poincare(v)

    def get_fundamental_triangle_verts(self):
        M = -np.eye(3)
        return [helpers.get_point_from_distance(self.mirrors, d) for d in M]

    def get_mirrors(self, coxeter_diagram):
        return helpers.get_hyperbolic_mirrors(coxeter_diagram)

    def get_init_point(self, init_dist):
        return helpers.get_point_from_distance(self.mirrors, init_dist)

    def render(self,
               output,
               image_size,
               show_vertices_labels=False,
               draw_alternative_domains=True,
               draw_polygon_edges=True,
               draw_inner_lines=False,
               draw_labelled_edges=False,
               vertex_size=0.1,
               line_width=0.07,
               checker=False,
               checker_colors=("#1E7344", "#EAF78D"),
               face_colors=("lightcoral", "mistyrose", "steelblue")):
        """
        An example drawing function shows how to draw hyperbolic patterns
        with this program.
        """
        print("=" * 40)
        print(self.get_info())
        d = drawSvg.Drawing(2.05, 2.05, origin="center")
        d.draw(euclid.shapes.Circle(0, 0, 1), fill="silver")

        bar = tqdm.tqdm(desc="processing polygons", total=self.num_faces)
        for (i, j), flist in self.face_indices.items():
            if checker:
                style1 = {"fill": checker_colors[0]}
                style2 = {"fill": checker_colors[1]}
            else:
                vertex_index = self.vertex_at_mirrors(i, j)
                color = face_colors[vertex_index]
                style1 = {"fill": color}
                style2 = {"fill": color, "opacity": 0.3}

            for k, face in enumerate(flist):
                points = [self.project(p) for p in face.coords]
                polygon = Polygon.fromVertices(points)
                domain1, domain2 = face.get_alternative_domains()
                domain1_2d = [[self.project(p) for p in D] for D in domain1]
                domain2_2d = [[self.project(p) for p in D] for D in domain2]

                for D in domain1_2d:
                    poly = Polygon.fromVertices(D)
                    d.draw(poly, **style1)
                    if checker:
                        d.draw(poly, hwidth=0.005, **style1)
                    if draw_inner_lines:
                        d.draw(poly, fill="papayawhip", hwidth=0.015)

                for D in domain2_2d:
                    poly = Polygon.fromVertices(D)
                    d.draw(poly, **style2)
                    if checker:
                        d.draw(poly, hwidth=0.005, **style2)
                    if draw_inner_lines:
                        d.draw(poly, fill="papayawhip", hwidth=0.015)

                if draw_polygon_edges:
                    d.draw(polygon, hwidth=line_width, fill="darkolivegreen")

                bar.update(1)

        bar.close()
        if draw_labelled_edges:
            for k, elist in self.edge_indices.items():
                if k != 0:
                    for i, j in elist:
                        p = self.project(self.vertices_coords[i])
                        q = self.project(self.vertices_coords[j])
                        hl = Line.fromPoints(p[0], p[1], q[0], q[1], segment=True)
                        if k == 1:
                            x = divide_line(line_width, 1)
                            d.draw(hl, hwidth=(-x, x), fill="papayawhip")
                        if k == 2:
                            x1, x2 = divide_line(line_width, 2)
                            d.draw(hl, hwidth=(x1, x2), fill="papayawhip")
                            d.draw(hl, hwidth=(-x2, -x1), fill="papayawhip")

        if show_vertices_labels:
            for i, p in enumerate(self.vertices_coords):
                loc = self.project(p)
                P = Point(*loc)
                d.draw(P, hradius=vertex_size, fill="darkolivegreen")
                x, y, r = get_euclidean_center_radius(P, hrad=vertex_size*1.3)
                d.draw(drawSvg.Text(str(i), r, x, y, center=0.7, fill="white"))

        print("saving to svg...")
        d.setRenderSize(w=image_size)
        d.saveSvg(output)
        size = os.path.getsize(output) >> 10
        print("{}KB svg file has been written to disk".format(size))
        print("=" * 40)


class Euclidean2D(Tiling2D):

    @property
    def level(self):
        """Return the z-component of the initial vertex.
        """
        return self.init_v[2]

    def project(self, v):
        return helpers.project_affine(v, self.level)

    def get_init_point(self, init_dist):
        return helpers.get_point_from_distance(self.mirrors, init_dist, False)

    def get_fundamental_triangle_verts(self):
        m0, m1, m2 = self.mirrors
        A = np.cross(m1, m2)
        B = np.cross(m0, m2)
        C = np.cross(m0, m1)
        return [p / p[-1] * self.level for p in [A, B, C]]

    def get_mirrors(self, coxeter_diagram):
        return helpers.get_spherical_or_affine_mirrors(coxeter_diagram)

    def render(self,
               output,
               image_width,
               image_height,
               extent=30,
               line_width=0.2,
               show_vertices_labels=False,
               face_colors=("thistle", "steelblue", "lightcoral")):
        print("=" * 40)
        print(self.get_info())

        surface = cairo.SVGSurface(output, image_width, image_height)
        ctx = cairo.Context(surface)
        ctx.scale(image_height / extent, -image_height / extent)
        ctx.translate(extent / 2, -extent / 2)
        ctx.scale(1, -1)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        ctx.set_line_width(line_width)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)

        bar = tqdm.tqdm(desc="processing polygons", total=self.num_faces)
        for (i, j), flist in self.face_indices.items():
            color1 = Color(face_colors[self.vertex_at_mirrors(i, j)])
            color2 = dimmed(color1)
            for face in flist:
                domain1, domain2 = face.get_alternative_domains()
                pts = [self.project(p) for p in face.coords]
                domain1 = [[self.project(p) for p in D] for D in domain1]
                domain2 = [[self.project(p) for p in D] for D in domain2]
                for D in domain1:
                    ctx.move_to(*D[0])
                    for p in D[1:]:
                        ctx.line_to(*p)
                    ctx.close_path()
                    ctx.set_source_rgb(*color1.rgb)
                    ctx.fill_preserve()
                    ctx.set_line_width(0.01)
                    ctx.stroke()

                for D in domain2:
                    ctx.move_to(*D[0])
                    for p in D[1:]:
                        ctx.line_to(*p)
                    ctx.close_path()
                    ctx.set_source_rgb(*color2.rgb)
                    ctx.fill_preserve()
                    ctx.set_line_width(0.01)
                    ctx.stroke()

                ctx.set_line_width(line_width)
                ctx.move_to(*pts[0])
                for p in pts[1:]:
                    ctx.line_to(*p)
                ctx.close_path()
                ctx.set_source_rgb(0.2, 0.2, 0.2)
                ctx.stroke()

                bar.update(1)

        bar.close()

        if show_vertices_labels:
            ctx.set_source_rgb(*Color("papayawhip").rgb)
            ctx.select_font_face("Serif", cairo.FONT_SLANT_NORMAL,
                                 cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(0.7)
            for i, p in enumerate(self.vertices_coords[:1000]):
                x, y = self.project(p)
                _, _, w, h, _, _ = ctx.text_extents(str(i))
                ctx.move_to(x - w / 2, y + h / 2)
                ctx.show_text(str(i))

        print("saving to svg...")
        surface.finish()
        size = os.path.getsize(output) >> 10
        print("{}KB svg file has been written to disk".format(size))
        print("=" * 40)


class Spherical2D(Tiling2D):

    def project(self, v):
        """keep v untouched here since we want to draw a 3d plot of the
           tiling, for 4d polychora it should be stereographic projection.
        """
        return v

    def get_init_point(self, init_dist):
        return helpers.get_point_from_distance(self.mirrors, init_dist)

    def get_fundamental_triangle_verts(self):
        M = np.eye(3)
        return [helpers.get_point_from_distance(self.mirrors, d) for d in M]

    def get_mirrors(self, coxeter_diagram):
        return helpers.get_spherical_or_affine_mirrors(coxeter_diagram)

    def render(self, output, image_size):
        """Need to find out how to draw 3d plots in SVG format.
        """
        import subprocess

        pov_string = """
#declare num_vertices = {};
#declare vertices = array[{}]{{{}}};

{}
        """
        EDGE_MACRO = "Edge({}, {}, {})\n"
        FACE_MACRO = "Face({}, {}, {})\n"
        with open("./povray/polyhedra-data.inc", "w") as f:
            f.write(pov_string.format(
                self.num_vertices,
                self.num_vertices,
                helpers.pov_vector_list(self.vertices_coords),
                "".join(EDGE_MACRO.format(k, i1, i2) for k, elist in self.edge_indices.items()
                        for i1, i2 in elist)))
            for (i, j), flist in self.face_indices.items():
                k = self.vertex_at_mirrors(i, j)
                for face in flist:
                    domain1, domain2 = face.get_alternative_domains()
                    for D in domain1:
                        f.write(FACE_MACRO.format(
                            k,
                            0,
                            "array[{}]{{{}}}".format(len(D), helpers.pov_vector_list(D))
                        ))
                    for D in domain2:
                        f.write(FACE_MACRO.format(
                            k,
                            1,
                            "array[{}]{{{}}}".format(len(D), helpers.pov_vector_list(D))
                        ))
        subprocess.check_call(
            "cd povray && " +
            "povray polyhedra.pov " +
            "+W{} +H{} +A0.001 +R4 ".format(image_size, image_size) +
            "+O../{}".format(output),
            shell=True
        )
