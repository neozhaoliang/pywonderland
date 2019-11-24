"""
This script shows how to draw uniform polyhedra with this program.
This case has already been handled in the `polytopes` project using
the Todd-Coxeter approach. But it can also down with the automatic way.
"""
import subprocess
import helpers
from tiling import SphericalTiling


POV_EXE = "povray"
SCENE_FILE = "polyhedra.pov"
IMAGE_SIZE = 600
POV_COMMAND = "cd povray &&" + \
    "{} {}".format(POV_EXE, SCENE_FILE) + \
    " +W{} +H{}".format(IMAGE_SIZE, IMAGE_SIZE) + \
    " +Q11 +A0.001 +R3" + \
    " +O../spherical.png"

POV_TEMPLATE = """
#declare nvertices = {};
#declare vertices = array[{}] {{{}}};

{}

{}

{}
"""


VERT_MACRO = "Vert(vertices, {})"      # Vert(vertices, ind, v)
EDGE_MACRO = "Edge(vertices, {}, {}, {})"  # Edge(vertices, ind, v1, v2)
FACE_MACRO = "Face(vertices, {}, {}, {})"  # Face(vertices, ind, nsides, indices)


def render(T):
    vertex_coords = helpers.pov_vector_list(T.vertices_coords)
    vert_macros = "\n".join(VERT_MACRO.format(i) for i in range(T.num_vertices))
    edge_macros = "\n".join(EDGE_MACRO.format(i, e[0], e[1])
                            for i, elist in T.edge_indices.items()
                            for e in elist)
    face_macros = "\n".join(FACE_MACRO.format((i + j) % 3

                                              , len(face), helpers.pov_array(face))
                            for (i, j), flist in T.face_indices.items()
                            for face in flist)

    with open("./povray/polyhedra-data.inc", "w") as f:
        f.write(POV_TEMPLATE.format(
            T.num_vertices,
            T.num_vertices,
            vertex_coords,
            vert_macros,
            edge_macros,
            face_macros))

    subprocess.call(POV_COMMAND, shell=True)


if __name__ == "__main__":
    T = SphericalTiling((5, 2, 3), (1, 1, 1))
    T.build_geometry()
    render(T)
