import collections
import itertools
from functools import partial
import cairocffi as cairo
import numpy as np
import automata
import helpers


def color(value):
    return [((value >> (8 * k)) & 255) / 255.0 for k in (2, 1, 0)]

colors = [0x477984, 0xEEAA4D, 0xC03C44, 0xFEF5EB]


def inset_corners(points, margin):
    def get_point(p, q):
        vx = p[0] - q[0]
        vy = p[1] - q[1]
        r = np.sqrt(vx*vx + vy*vy)
        t = 1 - margin / r
        return q[0] + t * vx, q[1] + t * vy

    q = np.sum(points, axis=0) / len(points)

    return [get_point(p, q) for p in points]


class Tiling(object):

    def __init__(self, pqr, init_dist):
        self.active = [bool(x) for x in init_dist]
        self.cox_mat = helpers.make_symmetry_matrix(pqr)
        self.dfa = automata.get_automaton(self.cox_mat)
        self.mirrors = self.get_mirrors(self.cox_mat)
        self.init_v = helpers.get_init_point(self.mirrors, init_dist)
        self.reflections = self.get_reflections(self.mirrors, init_dist)
        self.fundamental_faces = []

    def get_mirrors(self, cox_mat):
        C = -np.cos(np.pi / np.asarray(cox_mat, dtype=np.float))
        M = np.zeros_like(C)
        M[0, 0] = 1
        M[1, 0] = C[1, 0]
        M[1, 1] = np.sqrt(1 - M[1, 0]*M[1, 0])
        M[2, 0] = C[2, 0]
        M[2, 1] = (C[2, 1] - M[2, 0]*M[1, 0]) / M[1, 1]
        M[2, 2] = np.sqrt(abs(M[2, 0]*M[2, 0] + M[2, 1]*M[2, 1] - 1))
        return M

    def get_reflections(self, mirrors, init_dist):
        def reflect(v, N, d):
            return v - 2 * (np.dot(v, N) + d) * N

        return [partial(reflect, N=N, d=d) for N, d in zip(mirrors, init_dist)]


    def get_fundamental_faces(self):
        for i, j in itertools.combinations(range(3), 2):
            f0 = []
            P = self.init_v

            if self.active[i] and self.active[j]:
                Q = self.reflections[j](P)
                for _ in range(self.cox_mat[i][j]):
                    f0.append(P)
                    f0.append(Q)
                    P = self.reflections[j](self.reflections[i](P))
                    Q = self.reflections[j](self.reflections[i](Q))

            elif self.active[i] and self.cox_mat[i][j] > 2:
                for _ in range(self.cox_mat[i][j]):
                    f0.append(P)
                    P = self.reflections[j](self.reflections[i](P))

            elif self.active[j] and self.cox_mat[i][j] > 2:
                for _ in range(self.cox_mat[i][j]):
                    f0.append(P)
                    P = self.reflections[i](self.reflections[j](P))

            else:
                continue

            self.fundamental_faces.append(f0)

    def project_to_plane(self, v):
        return np.array(v[:2]) / v[-1]

    def traverse(self, depth, domain):
        """Traverse the dfa using breath-first search up to a given depth.
        """
        queue = collections.deque()
        queue.append([self.dfa.start, (), 0, domain])

        while queue:
            state, word, steps, shape = queue.popleft()
            yield state, word, steps, shape

            if steps < depth:
                for symbol, target in state.all_transitions():
                    queue.append([target,
                                  word + (symbol,),
                                  steps + 1,
                                  [self.reflections[symbol](p) for p in shape]])

    def draw(self, image_width, image_height, extent, depth=20):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, image_width, image_height)
        ctx = cairo.Context(surface)
        ctx.scale(image_height / extent, image_height / extent)
        ctx.translate(extent / 2, extent / 2)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        ctx.set_line_width(0.3)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)

        for i, face in enumerate(self.fundamental_faces):
            for _, _, _, shape in self.traverse(depth, face):
                shape = [self.project_to_plane(v) for v in shape]
                shape = inset_corners(shape, 0.3)
                z = shape[0]
                ctx.move_to(z[0], z[1])
                for w in shape[1:]:
                    ctx.line_to(w[0], w[1])
                ctx.line_to(z[0], z[1])
                ctx.set_source_rgb(*color(colors[i]))
                ctx.fill_preserve()
                ctx.set_source_rgb(*color(0x313E4A))
                ctx.stroke()

        surface.write_to_png("Euclidean.png")


T = Tiling((2, 3, 6), (1, 1, 1))
T.get_fundamental_faces()
T.draw(1200, 960, 50, 80)
T.dfa.draw("automata.png")
