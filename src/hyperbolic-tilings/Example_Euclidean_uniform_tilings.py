"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Draw 2d Euclidean uniform tilings using the automata approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are three kinds of 2d Euclidean uniform tiings, their symmetry groups
are all Coxeter groups of affine type (hence are infinite)

1. Tiling (3, 3), its group is affine A_2~.
2. Tiling (4, 4), its group is affine B_2~.
3. Tiling (6, 3), its group is affine G_2~.
"""
from itertools import combinations
import numpy as np
import cairocffi as cairo
import helpers
import automata


def get_euclidean_fundamental_triangle(p, q, r):
    """Return the vertices A, B, C of the fundamental triangle with
       <A=pi/r, <B=pi/q, <C=pi/p. A is always the origin, B is (1, 0),
       C lies in the first quadrant.
    """
    A = 0j
    B = 1 + 0j
    alpha = np.pi / r
    beta = np.pi / q
    cosa = np.cos(alpha)
    sina = np.sin(alpha)
    sinb = np.sin(beta)
    vAC = cosa + sina * 1j
    vBC = -np.cos(beta) + sinb * 1j
    rAC = 1 / (vAC - sina / sinb * vBC)
    C = rAC * vAC
    return A, B, C


p, q, r = 6, 2, 3  # the tiling
active = (1, 1, 1)  # active mirrors
depth = 80  # draw tiles with their shortlex word representations up to length 50
cox_mat = helpers.make_symmetry_matrix(p, q, r)  # Coxeter matrix
A, B, C = get_euclidean_fundamental_triangle(p, q, r)  # fundamental triangle
dfa = automata.get_automaton(cox_mat)  # the dfa of the Coxeter group
v0 = helpers.from_bary_coords([A, B, C], active)  # initial vertex
edges = [[B, C], [A, C], [A, B]]
reflections = [helpers.reflection_by_line(*e) for e in edges]  # three reflections


def get_fundamental_faces():
    faces = []
    for i, j in combinations(range(3), 2):
        f0 = []
        P = v0

        if active[i] and active[j]:
            Q = reflections[j](P)
            for _ in range(cox_mat[i][j]):
                f0.append(P)
                f0.append(Q)
                P = reflections[j](reflections[i](P))
                Q = reflections[j](reflections[i](Q))

        elif active[i] and cox_mat[i][j] > 2:
            for _ in range(cox_mat[i][j]):
                f0.append(P)
                P = reflections[j](reflections[i](P))

        elif active[j] and cox_mat[i][j] > 2:
            for _ in range(cox_mat[i][j]):
                f0.append(P)
                P = reflections[i](reflections[j](P))

        else:
            continue

        faces.append(f0)
    return faces


image_width = 800
image_height = 600
extent = 40

surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, image_width, image_height)
ctx = cairo.Context(surface)
ctx.translate(image_width / 2, image_height / 2)
ctx.scale(image_height / extent, -image_height / extent)
ctx.set_source_rgb(1, 1, 1)
ctx.paint()
ctx.set_line_width(0.1)
ctx.set_line_cap(cairo.LINE_CAP_ROUND)
ctx.set_line_join(cairo.LINE_JOIN_ROUND)

faces = get_fundamental_faces()
for face in faces:
    color = np.random.random(3)
    for _, _, _, shape in helpers.traverse(dfa, depth, reflections, face):
        z = shape[0]
        ctx.move_to(z.real, z.imag)
        for w in shape[1:]:
            ctx.line_to(w.real, w.imag)
        ctx.line_to(z.real, z.imag)
        ctx.set_source_rgb(*color)
        ctx.fill_preserve()
        ctx.set_source_rgb(0.2, 0.2, 0.2)
        ctx.stroke()

surface.write_to_png("Euclidean{}{}{}-{}{}{}.png".format(p, q, r, *active))
dfa.draw("automaton{}{}{}.png".format(p, q, r))
