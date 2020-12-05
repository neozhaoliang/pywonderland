# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Impossible rhombus tiling using Greg Egan's idea
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adapted from Greg Egan's applet at

    "http://gregegan.net/APPLETS/02/02.html"

:copyright: by Zhao Liang, 2020.
"""
import itertools
import numpy as np

try:
    import cairocffi as cairo
except ImportError:
    import cairo


IMAGE_SIZE = (1200, 800)
NUM_LINES = 12
PI = np.pi
DIMENSION = 5
GRIDS = [np.exp(PI * 2j * i / DIMENSION) for i in range(DIMENSION)]
SHIFTS = [0.1, 0.2, 0.3, 0.15, 0.25]

THIN_COLOR_0 = (102/255, 194/255, 164/255)
THIN_COLOR_1 = (252/255, 141/255, 98/255)
FAT_COLOR_0 = (141/255, 160/255, 203/255)
FAT_COLOR_1 = (231/255, 138/255, 195/255)
EDGE_COLOR = (0, 0, 0)


def cdot(z, w):
    return z.real * w.real + z.imag * w.imag

def ccross(z, w):
    return z.real * w.imag - z.imag * w.real

def get_index(z):
    return [np.ceil((z / gd).real + shift) for gd, shift in zip(GRIDS, SHIFTS)]

def isacute(r, s):
    return cdot(GRIDS[r], GRIDS[s]) > 0


class Rhombus(object):

    def __init__(self, r, s, kr, ks):
        self.inds = (r, s, kr, ks)
        self.verts = self.compute_rhombus(r, s, kr, ks)
        self.acute = isacute(r, s)
        self.fat = (s - r == 1 or s - r == 4)
        if (r + s) % 5 == 0:
            self.flip = (kr + (kr + ks) // 2) % 2
        elif (r + s) % 5 == 1:
            self.flip = (kr % 4) // 2
        else:
            self.flip = ((2 + kr) % 4) // 2
        self.tunnel = self.get_tunnel(r, s)

    @staticmethod
    def compute_rhombus(r, s, kr, ks):
        """
        Compute the coordinates of the four vertices of the rhombus that
        correspondes to the intersection point of the kr-th line in the r-th
        grid and the ks-th line in the s-th grid. Here r, s, kr, ks are all
        integers and 0 <= r < s <= DIMENSION and -NUM_LINES <= kr, ks <= NUM_LINES.

        The intersection point is the solution to a 2x2 linear equation:
            Re(z/grids[r]) + shifts[r] = kr
            Re(z/grids[s]) + shifts[s] = ks
        """
        # The intersection point
        P = ((GRIDS[r] * (ks - SHIFTS[s]) - GRIDS[s] * (kr - SHIFTS[r]))
             * 1j / GRIDS[s - r].imag)

        # the list of integers that indicate the position of the intersection point.
        # the i-th integer n_i indicates that this point lies in the n_i-th strip
        # in the i-th grid.
        index = get_index(P)

        # Be careful of the accuracy problem here.
        # Mathematically the r-th and s-th item of index should be kr and ks,
        # but programmingly it might not be the case,
        # so we have to manually set them to correct values.
        return [
            np.dot(index, GRIDS)
            for index[r], index[s] in [
                (kr, ks),
                (kr + 1, ks),
                (kr + 1, ks + 1),
                (kr, ks + 1),
            ]
        ]

    def get_tunnel(self, r, s):
        gr = GRIDS[r] / 2
        gs = GRIDS[s] / 2
        # if vertex A is acute we move to obtuse vertex B
        # else we move to obtuse vertex C
        sgn = 1 if self.acute else -1
        xy = (sgn * gs - gr) / 2
        XY = self.get_nearest_grid_dir(r, s, xy) / 7.0
        # the first vertex p1 is half the way from center to B
        # if A is acute else it's half the way from center to C
        p1 = (gr - sgn * gs) / 2
        # the second vertex points inwards the hole by a shift XY
        p2 = p1 + XY
        # the fourth vertex is at the acute corner of the hole
        # it's half the way from center to C is A is acute
        # else it's half the way from the center to D
        p4 = (sgn * gr + gs) / 2
        t = ccross(XY, p4 - p1) / ccross(p4 + p1, p4 - p1)
        p3 = p4 + t * (p1 + p4)

        q1 = p1
        q2 = p2
        q4 = -p4
        t = ccross(XY, q4 - q1) / ccross(q4 + q1, q4 - q1)
        q3 = q4 + t * (q1 + q4)
        if self.flip:
            self.tunnels = [(-p1, -p2, -p3, -p4), (-q1, -q2, -q3, -q4)]
        else:
            self.tunnels = [(p1, p2, p3, p4), (q1, q2, q3, q4)]

    def get_nearest_grid_dir(self, r, s, v):
        maxdot = 0
        inn = 0
        for k, gd in enumerate(GRIDS):
            if k != r and k != s:
                inn = cdot(GRIDS[k], v)
                if (abs(inn) > maxdot):
                    maxdot = abs(inn)
                    result = gd if inn > 0 else -gd
        return result

    def draw_tile(self, ctx, face_color, edge_color,
                  hole_color, tunnel_color):
        A, B, C, D = self.verts
        cen = sum(self.verts) / 4
        ctx.move_to(A.real, A.imag)
        ctx.line_to(B.real, B.imag)
        ctx.line_to(C.real, C.imag)
        ctx.line_to(D.real, D.imag)
        ctx.close_path()
        ctx.set_source_rgb(*face_color)
        ctx.fill_preserve()
        ctx.set_source_rgb(*edge_color)
        ctx.set_line_width(0.005)
        ctx.stroke()

        A1 = (cen + A) / 2
        B1 = (cen + B) / 2
        C1 = (cen + C) / 2
        D1 = (cen + D) / 2
        ctx.move_to(A1.real, A1.imag)
        ctx.line_to(B1.real, B1.imag)
        ctx.line_to(C1.real, C1.imag)
        ctx.line_to(D1.real, D1.imag)
        ctx.close_path()
        ctx.set_source_rgb(*hole_color)
        ctx.fill()

        ctx.set_source_rgb(*tunnel_color)
        ctx.set_line_width(0.1)
        for inset in self.tunnels:
            for k, v in enumerate(inset):
                if k == 0:
                    ctx.move_to((cen + v).real, (cen + v).imag)
                else:
                    ctx.line_to((cen + v).real, (cen + v).imag)
            ctx.line_to((cen + inset[0]).real, (cen + inset[0]).imag)
            ctx.fill()


surface = cairo.SVGSurface("debruijn.svg", IMAGE_SIZE[0], IMAGE_SIZE[1])
ctx = cairo.Context(surface)
ctx.set_line_cap(cairo.LINE_CAP_ROUND)
ctx.set_line_join(cairo.LINE_JOIN_ROUND)
scale = max(IMAGE_SIZE) / (1.2 * NUM_LINES)
ctx.scale(scale, scale)
ctx.translate(NUM_LINES, NUM_LINES)

for r, s in itertools.combinations(range(DIMENSION), 2):
    for kr, ks in itertools.product(range(-NUM_LINES, NUM_LINES), repeat=2):
        rb = Rhombus(r, s, kr, ks)
        if rb.fat:
            face_color = FAT_COLOR_0 if rb.flip else FAT_COLOR_1
        else:
            face_color = THIN_COLOR_0 if rb.flip else THIN_COLOR_1
        rb.draw_tile(ctx, face_color, EDGE_COLOR, (0, 0, 0), (1, 1, 1))

surface.finish()
