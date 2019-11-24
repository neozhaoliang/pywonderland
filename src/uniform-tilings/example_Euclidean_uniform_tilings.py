"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Draw 2d Euclidean uniform tilings using the automata approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are three kinds of uniform tilings in the 2d Euclidean plane,
their symmetry groups are all Coxeter groups of affine type:

1. Tiling (3, 3), its group is affine A_2~.
2. Tiling (4, 4), its group is affine B_2~.
3. Tiling (6, 3), its group is affine G_2~.

In this program we used the standard geometric representation for
an affine Coxeter group and its automaton to generated the Tit's
cone in R^3 (which is the upper halfspace {(x, y, z) ∈ R^3 | z ≥ 0}).
Our 2d tiling is obtained by drawing the cross-section of the cone with plane z=1.

reference:

    "Cells in Coxeter groups", Paul E. Gunnells.

"""
import subprocess
import numpy as np
import cairocffi as cairo
import helpers
from tiling import EuclideanTiling


POV_EXE = "povray"
SCENE_FILE = "euclid3d.pov"
IMAGE_SIZE = 600
POV_COMMAND = "cd povray &&" + \
    "{} {}".format(POV_EXE, SCENE_FILE) + \
    " +W{} +H{}".format(IMAGE_SIZE, IMAGE_SIZE) + \
    " +Q11 +A0.001 +R3" + \
    " +O../euclid3d.png"

POV_TEMPLATE = """
#declare nvertices = {};
#declare vertices = array[{}] {{{}}};

{}

{}
"""


def inset_corners(points, margin):
    """Draw a smaller polygon inside the given one.
    """
    def get_point(p, q):
        vx = p[0] - q[0]
        vy = p[1] - q[1]
        r = np.sqrt(vx * vx + vy * vy)
        t = 1 - margin / r
        return q[0] + t * vx, q[1] + t * vy

    q = np.sum(points, axis=0) / len(points)
    return [get_point(p, q) for p in points]


def draw(T, output, image_width, image_height,
         extent, depth, line_width=0.2, margin=0.3,
         edge_color=0x313E4A, face_colors=[0x477984, 0xEEAA4D, 0xC03C44]):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, image_width, image_height)
    ctx = cairo.Context(surface)
    ctx.scale(image_height / extent, image_height / extent)
    ctx.translate(extent / 2, extent / 2)
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    ctx.set_line_width(line_width)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)

    for (i, j), flist in T.face_indices.items():
        for face in flist:
            coords = [T.vertices_coords[k] for k in face]
            shape = [T.project(v) for v in coords]
            shape = inset_corners(shape, margin)
            p = shape[0]
            ctx.move_to(p[0], p[1])
            for q in shape[1:]:
                ctx.line_to(q[0], q[1])
            ctx.line_to(p[0], p[1])
            if face_colors is not None:
                ctx.set_source_rgb(*helpers.hex_to_rgb(face_colors[(i+j)%3]))
                ctx.fill_preserve()
            ctx.set_source_rgb(*helpers.hex_to_rgb(edge_color))
            ctx.stroke()

    surface.write_to_png(output)


def render3d(T, output="./povray/affine-data.inc", scene_file="euclid3d.pov"):
    VERT_MACRO = "Vert({})"
    EDGE_MACRO = "Edge(vertices, {}, {}, {})"
    vert_macros = "\n".join(VERT_MACRO.format(i) for i in range(T.num_vertices))
    edge_macros = "\n".join(EDGE_MACRO.format(i, e[0], e[1])
                            for i, elist in T.edge_indices.items()
                            for e in elist)
    with open(output, "w") as f:
        f.write(POV_TEMPLATE.format(
            T.num_vertices,
            T.num_vertices,
            helpers.pov_vector_list([T.project(v) for v in T.vertices_coords]),
            vert_macros,
            edge_macros,
        ))
    subprocess.call(POV_COMMAND, shell=True)


def main():
    width, height = 1200, 960

    T = EuclideanTiling((3, 3, 3), (1, 0, 0))
    T.build_geometry(depth=50, maxcount=10000)
    draw(T, "333-100.png", width, height, extent=10, depth=30)

    T = EuclideanTiling((3, 3, 3), (1, 1, 0))
    T.build_geometry(depth=50, maxcount=10000)
    draw(T, "333-110.png", width, height, extent=20, depth=30)

    T = EuclideanTiling((2, 4, 4), (1, 1, 1))
    T.build_geometry(depth=50, maxcount=10000)
    draw(T, "244-111.png", width, height, extent=30, depth=30)

    T = EuclideanTiling((2, 4, 4), (0, 1, 1))
    T.build_geometry(depth=50, maxcount=10000)
    draw(T, "244-011.png", width, height, extent=25, depth=30)

    T = EuclideanTiling((2, 3, 6), (1, 0, 1))
    T.build_geometry(depth=50, maxcount=10000)
    draw(T, "236-101.png", width, height, extent=30, depth=30)

    T = EuclideanTiling((2, 3, 6), (1.2, 1.0, 0.8))
    T.build_geometry(depth=50, maxcount=10000)
    draw(T, "236-111.png", width, height, extent=30, depth=50)

    # cube tiling
    T = EuclideanTiling((4, 2, 2, 3, 2, 4), (1, 0, 0, 0))
    T.build_geometry(80, maxcount=30000)
    render3d(T)


if __name__ == "__main__":
    main()
