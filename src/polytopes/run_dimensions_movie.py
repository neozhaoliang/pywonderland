"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Reproduce the scene of 120-cell in the movie

    "Dimensions - A walk through mathematics"

at "http://www.dimensions-math.org/".
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The rendering process may take several hours to complete.

:copyright (c) 2018 by Zhao Liang.
"""
import os
import subprocess
import numpy as np
from models import Polychora
import helpers


POV_EXE = "povray"                   # POV-Ray exe binary
SCENE_FILE = "dimensions_movie.pov"  # the main scene file
OUTPUT_DIR = "./dimensions_frames/"  # output directory
FRAMES = 1200                        # number of frames
IMAGE_SIZE = 800                     # image size in pixels
IMAGE_QUALITY_LEVEL = 11             # between 0-11
SUPER_SAMPLING_LEVEL = 2             # between 1-9
ANTIALIASING_LEVEL = 0.001           # lower for better quality

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

POV_COMMAND = " cd povray && " + \
              " {} +I{}".format(POV_EXE, SCENE_FILE) + \
              " +W{} +H{}".format(IMAGE_SIZE, IMAGE_SIZE) + \
              " +Q{}".format(IMAGE_QUALITY_LEVEL) + \
              " +A{}".format(ANTIALIASING_LEVEL) + \
              " +R{}".format(SUPER_SAMPLING_LEVEL) + \
              " +KFI0" + \
              " +KFF{}".format(FRAMES - 1) + \
              " +O../{}".format(OUTPUT_DIR)

POV_TEMPLATE = """
#declare extent = {};
#declare vertices = array[{}] {{{}}};

{}

{}

{}
"""

VERT_MACRO = "Vert(vertices, {})"      # Vert(vertices, i)
EDGE_MACRO = "Edge(vertices, {}, {})"  # Edge(vertices, v1, v2)


def write_to_pov(P):
    with open("./povray/120-cell-data.inc", "w") as f:
        extent = max(np.linalg.norm(helpers.proj3d(v)) for v in P.vertex_coords)
        vert_macros = "\n".join(VERT_MACRO.format(k) for k in range(P.num_vertices))
        edge_macros = "\n".join(EDGE_MACRO.format(e[0], e[1])
                                for elist in P.edge_indices
                                    for e in elist)
        face_macros = "\n".join(helpers.export_face(i, face)
                                for i, flist in enumerate(P.face_coords)
                                    for face in flist)
        f.write(POV_TEMPLATE.format(
            extent,
            P.num_vertices,
            helpers.pov_vector_list(P.vertex_coords),
            vert_macros,
            edge_macros,
            face_macros))


def main():
    coxeter_diagram = (5, 2, 2, 3, 2, 3)
    coxeter_matrix = helpers.make_symmetry_matrix(coxeter_diagram)
    mirrors = helpers.get_mirrors(coxeter_diagram)
    P = Polychora(coxeter_matrix, mirrors, (1, 0, 0, 0))
    P.build_geometry()
    write_to_pov(P)
    subprocess.call(POV_COMMAND, shell=True)


if __name__ == "__main__":
    main()
