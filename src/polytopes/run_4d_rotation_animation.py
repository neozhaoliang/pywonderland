"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make animations of 4d polychora rotations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import subprocess
import os
from models import Polychora
import helpers


IMAGE_DIR = "rotation4d"
POV_EXE = "povray"
FRAMES = 120

# POV-Ray command line options
POV_COMMAND = " cd povray &&" + \
              " {} polychora-rotation.pov".format(POV_EXE) + \
              " +W500 +H500" + \
              " +Q11 +A0.005 +R3" + \
              " +KFI0" + \
              " +KFF{}".format(FRAMES - 1) + \
              " -V" + \
              " +O../rotation4d/{}"

# ImageMagick command line options
IM_COMMAND = " cd {} && ".format(IMAGE_DIR) + \
             " convert -layers Optimize" + \
             " -delay 10 {}%03d.png[0-{}]" + \
             " ../{}.gif"

# POV-Ray template string
POV_TEMPLATE = """
#declare vertexColor = {};
#declare edgeColor = {};

#declare nvertices = {};
#declare vertices = array[{}] {{{}}};

#declare nedges = {};
#declare adjacencies = array[{}][2] {{{}}};

#macro Vertices(theta, phi, xi)
    #local out = array[nvertices];
    #for(i, 0, nvertices-1)
        #local out[i] = proj3d(rotate4d(theta, phi, xi, vertices[i]));
    #end
    out
#end

#declare rvs = Vertices(0, 0, 2*clock*pi);

{}
"""


if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)


def write_to_pov(P, glass_tex, face_index, vertex_color, edge_color):
    """
    Write the data of a polytope `P` to a POV-Ray include file for rendering.

    parameter
    ---------
    :P: a polychora instance.

    glass_tex: glass texture for the faces, as defined in POV-Ray's "textures.inc".

    face_index: controls which type of faces are rendered. This input can be either
        an integer or a list/tuple of integers, for example if face_index=1 then
        the second list of faces will be rendered, or if face_index=(0, 1) then the
        first and second lists of faces will be rendered.

    vertex_color && edge_color: must be colors defined in POV-Ray's "colors.inc".
    """
    macro = "Face(rvs, {}, {}, {})"
    faces = []
    for i, flist in enumerate(P.face_indices):
        try:
            if (i == face_index or i in face_index):
                faces += flist
        except:
            pass

    face_macros = "\n".join(macro.format(
        len(face),
        helpers.format_face(face),
        glass_tex)
        for face in faces)

    with open("./povray/polychora-data.inc", "w") as f:
        f.write(POV_TEMPLATE.format(
            vertex_color,
            edge_color,
            P.num_vertices,
            P.num_vertices,
            helpers.pov_vector_list(P.vertex_coords),
            P.num_edges,
            P.num_edges,
            helpers.pov_edge_list(P.edge_indices),
            face_macros
            )
        )


def anim(coxeter_diagram,
         trunc_type,
         description="polychora-rotation4d",
         glass_tex="NBglass",
         face_index=0,
         vertex_color="SkyBlue",
         edge_color="Orange"):
    """Call POV-Ray to render the frames and then call ImageMagick
       to convert them to GIF.
    """
    coxeter_matrix = helpers.fill_matrix(coxeter_diagram)
    mirrors = helpers.get_mirrors(coxeter_diagram)
    P = Polychora(coxeter_matrix, mirrors, trunc_type)
    P.build_geometry()
    write_to_pov(P, glass_tex, face_index, vertex_color, edge_color)
    subprocess.call(POV_COMMAND.format(description), shell=True)
    subprocess.call(IM_COMMAND.format(description, FRAMES - 1, description), shell=True)


if __name__ == "__main__":
    #anim((4, 2, 2, 3, 2, 3), (1, 1, 0, 0), "truncated-tesseract", "Dark_Green_Glass", 1)
    #anim((3, 2, 2, 2, 2, 20), (1, 0, 0, 1), "3-20-duoprism", "Dark_Green_Glass", None)
    #anim((3, 2, 2, 3, 2, 4), (1, 0, 0, 0), "16-cell")
    #anim((3, 2, 2, 3, 2, 4), (1, 0, 0, 1), "runcinated-16-cell",
    #     glass_tex="Yellow_Glass", face_index=(0, 1), vertex_color="Orange", edge_color="Pink")
    #anim((3, 2, 2, 3, 2, 3), (1, 0, 0, 0), "5-cell", vertex_color="Orange", edge_color="Pink")
    #anim((5, 2, 2, 3, 2, 2), (1, 1, 0, 1), "prism", glass_tex="Ruby_Glass",
    #     vertex_color="Coral", edge_color="Violet", face_index=2)
    anim((4, 2, 2, 3, 2, 3), (1, 0, 0, 0), "tesseract", vertex_color="Orange", edge_color="Pink")
