# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Render curved 4d polychoron examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script draws uniform polychoron whose vertices lie
on the unit sphere S^3 by using stereographic projection
to map them into 3d space.

:copyright (c) 2018 by Zhao Liang.
"""
import subprocess
from fractions import Fraction
import numpy as np
from models import Polychora
import helpers


POV_EXE = "povray"                   # POV-Ray exe binary
SCENE_FILE = "polychora_curved.pov"  # the main scene file
IMAGE_SIZE = 600                     # image size in pixels
IMAGE_QUALITY_LEVEL = 11             # between 0-11
SUPER_SAMPLING_LEVEL = 3             # between 1-9
ANTIALIASING_LEVEL = 0.001           # lower for better quality

POV_COMMAND = " cd povray && " + \
              " {} +I{}".format(POV_EXE, SCENE_FILE) + \
              " +W{} +H{}".format(IMAGE_SIZE, IMAGE_SIZE) + \
              " +Q{}".format(IMAGE_QUALITY_LEVEL) + \
              " +A{}".format(ANTIALIASING_LEVEL) + \
              " +R{}".format(SUPER_SAMPLING_LEVEL) + \
              " +O../{}"


POV_TEMPLATE = """
#declare vertex_size = {};
#declare edge_size = {};
#declare camera_location = {};
#declare object_rotation = {};
#declare extent = {};
#declare vertices = array[{}] {{{}}};
#declare size_func = {};
#declare face_max= {};
#declare face_min = {};
#declare face_index = {};

// this macro is used for adjusting the size of edges
// according to their positions in the space.
#macro get_size(q)
    #local len = vlength(q);
    #if (size_func = 0)
        #local len = (1.0 + len * len) / 4;
    #else #if (size_func = 1)
        #local len = 2.0 * log(2.0 + len * len);
    #else
        #local len = 2.0 * log(1.13 + len * len);
    #end
    #end
    len
#end

#macro choose_face(i, face_size)
    #local chosen = false;
    #for (ind, 0, dimension_size(face_index, 1) - 1)
        #if (i = face_index[ind])
            #if (face_size > face_min & face_size < face_max)
                #local chosen = true;
            #end
        #end
    #end
    chosen
#end

{}

{}

{}
"""


VERT_MACRO = "Vert(vertices, {})"
EDGE_MACRO = "Edge(vertices, {}, {}, {})"


def write_to_pov(P,
                 camera=(0, 0, 180),
                 rotation=(0, 0, 0),
                 vertex_size=0.04,
                 edge_size=0.02,
                 size_func=0,
                 face_index=(0,),
                 face_max=3,
                 face_min=0.5):
    """Write the data of a polytope `P` to the include file.

    :param camera: camera location.

    :param rotation: rotation angles (in degree) of the polytope.

    :param vertex_size: controls size of the vertices.

    :param edge_size: controls size of the edges.

    :param size_func: choose which way to adjust the size of the edges.
        currently there are three choices, so it can only be 0-2.

    :param face_index: controls which type of faces are rendered,
        must be a list of integers.

    :param face_max: faces larger than this value will not be rendered.

    :param face_min: faces smaller than this value will not be rendered.
    """
    with open("./povray/polychora-data.inc", "w") as f:
        extent = max(np.linalg.norm(helpers.proj3d(v)) for v in P.vertex_coords)
        vert_macros = "\n".join(VERT_MACRO.format(k) for k in range(P.num_vertices))
        edge_macros = "\n".join(EDGE_MACRO.format(i, e[0], e[1])
                                for i, elist in enumerate(P.edge_indices)
                                for e in elist)
        face_macros = "\n".join(helpers.export_face(i, face)
                                for i, flist in enumerate(P.face_coords)
                                for face in flist)
        f.write(POV_TEMPLATE.format(
            vertex_size,
            edge_size,
            helpers.pov_vector(camera),
            helpers.pov_vector(rotation),
            extent,
            P.num_vertices,
            helpers.pov_vector_list(P.vertex_coords),
            size_func,
            face_max,
            face_min,
            helpers.pov_array(face_index),
            vert_macros,
            edge_macros,
            face_macros))


def draw(coxeter_diagram,
         trunc_type,
         description="polychora",
         extra_relations=(),
         **kwargs):
    coxeter_matrix = helpers.make_symmetry_matrix([x.numerator for x in coxeter_diagram])
    mirrors = helpers.get_mirrors(coxeter_diagram)
    P = Polychora(coxeter_matrix, mirrors, trunc_type, extra_relations)
    P.build_geometry()
    write_to_pov(P, **kwargs)

    print("rendering {} with {} vertices, {} edges, {} faces".format(
        description,
        P.num_vertices,
        P.num_edges,
        P.num_faces))

    process = subprocess.Popen(
        POV_COMMAND.format(description),
        shell=True,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)

    _, err = process.communicate()
    if process.returncode:
        print(type(err), err)
        raise IOError("POVRay error: " + err.decode("ascii"))


def main():
    """
    draw((3, 2, 2, 3, 2, 3), (1, 0, 0, 0), "5-cell", camera=(0, 0, 200),
         vertex_size=0.08, edge_size=0.04, rotation=(-30, 60, 0), size_func=1)
    draw((5, 2, 2, 3, 2, 3), (1, 0, 0, 1), "runcinated-120-cell", camera=(0, 0, 105),
         vertex_size=0.028, edge_size=0.014, face_min=20)
    """
    draw((3, 2, 2, 3, 2, 5), (1, 0, 0, 0), "600-cell", camera=(0, 0, 200),
         vertex_size=0.12, edge_size=0.04, size_func=2, face_max=4.0, face_min=3.0)


if __name__ == "__main__":
    main()
