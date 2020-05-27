import numpy as np
import cairocffi as cairo
from . import helpers


def draw_on_coxeter_plane(P,
                          nodes1,
                          nodes2,
                          svgpath=None,
                          image_size=600,
                          linewidth=0.0012,
                          markersize=0.015):
    """
    Project the vertices of a polytope `P` to its Coxeter plane
    and draw the pattern to a svg image.

    The most important parameters are `nodes1` and `nodes2`, they
    can be of lists/tuples/sets type and must partition the Coxeter
    diagram of `P` into two disjoint sets such that the nodes in
    each set are mutually orthogonal with each other.
    """
    P.build_geometry()
    M = P.mirrors
    C = np.dot(M, M.T)  # Cartan matrix
    eigenvals, eigenvecs = np.linalg.eigh(C)
    # get the eigenvector with largest (or smallest) eigenvalue
    v = eigenvecs[:, 0]
    # a basis of the Coxeter plane
    mu_a = np.sum([v[i] * M[i] for i in nodes1], axis=0)
    mu_b = np.sum([v[j] * M[j] for j in nodes2], axis=0)
    # make them orthogonal
    mu_a = helpers.normalize(mu_a)
    mu_b -= np.dot(mu_b, mu_a) * mu_a
    mu_b = helpers.normalize(mu_b)
    vertices_2d = [(np.dot(mu_a, x), np.dot(mu_b, x)) for x in P.vertices_coords]

    # draw on image
    if svgpath is None:
        svgpath = P.__class__.__name__ + ".svg"
    extent = 0.99
    surface = cairo.SVGSurface(svgpath, image_size, image_size)
    ctx = cairo.Context(surface)
    ctx.scale(image_size / (extent*2.0), -image_size / (extent*2.0))
    ctx.translate(extent, -extent)
    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()
    ctx.set_line_width(linewidth)

    # draw edges
    for elist in P.edge_indices:
        for i, j in elist:
            x1, y1 = vertices_2d[i]
            x2, y2 = vertices_2d[j]
            ctx.set_source_rgb(0, 0, 0)
            ctx.set_line_width(linewidth)
            ctx.move_to(x1, y1)
            ctx.line_to(x2, y2)
            ctx.stroke()

    # draw the vertices as circles
    ctx.set_line_width(linewidth * 2)
    for x, y in vertices_2d:
        ctx.arc(x, y, markersize, 0, 2*np.pi)
        ctx.set_source_rgb(1, 0, 0)
        ctx.fill_preserve()
        ctx.set_source_rgb(0, 0, 0)
        ctx.stroke()

    surface.finish()
