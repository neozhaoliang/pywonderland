"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make animations of rotating 4d polychoron
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script computes the data of a given polychora and writes it
into a POV-Ray .inc file, then automatically calls POV-Ray
to render the frames and finally calls FFmpeg to convert the frames to
a mp4 movie. You need to have POV-Ray and FFmpeg installed and
set the paths to their executables in `POV_EXE` and `FFMPEG_EXE`.

:copyright (c) 2018 by Zhao Liang.
"""
import subprocess
import os
from fractions import Fraction
from models import Polychora, Snub24Cell
import helpers


IMAGE_DIR = "4drotation_frames"           # directory to save the frames
POV_EXE = "povray"                        # povray command
FFMPEG_EXE = "ffmpeg"                     # ffmpeg command
SCENE_FILE = "4drotation_animation.pov"   # scene file to render
FRAMES = 1                                # number of frames (120 is quite good)
IMAGE_SIZE = 500                          # image size

# POV-Ray command line options
POV_COMMAND = " cd povray &&" + \
              " {} {}".format(POV_EXE, SCENE_FILE) + \
              " +W{} +H{}".format(IMAGE_SIZE, IMAGE_SIZE) + \
              " +Q11 +A0.005 +R4" + \
              " +KFI0" + \
              " +KFF{}".format(FRAMES - 1) + \
              " -V" + \
              " +O../{}/".format(IMAGE_DIR) + "{}"

# FFmpeg command line options
FFMPEG_COMMAND = " cd {} && ".format(IMAGE_DIR) + \
                 " {} -framerate 12".format(FFMPEG_EXE) + \
                 " -y" + \
                 " -i {}" + \
                 "%0{}d.png".format(len(str(FRAMES - 1))) + \
                 " -crf 18 -c:v libx264" + \
                 " ../{}.mp4"

# POV-Ray template string
POV_TEMPLATE = """
#declare vertexColor = {};
#declare edgeColor = {};

#declare nvertices = {};
#declare vertices = array[{}] {{{}}};

#macro Vertices(theta, phi, xi)
    #local out = array[nvertices];
    #for(i, 0, nvertices-1)
        #local out[i] = proj3d(rotate4d(theta, phi, xi, vertices[i]));
    #end
    out
#end

#declare rvs = Vertices(2*clock*pi, 0, 2*clock*pi);

{}

{}

{}
"""


if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)


VERT_MACRO = "Vert(rvs, {}, {})"      # Vert(rvs, ind, color)
EDGE_MACRO = "Edge(rvs, {}, {}, {})"  # Edge(rvs, v1, v2, color)
FACE_MACRO = "Face(rvs, {}, {}, {})"  # Face(rvs, nsides, indices, color)


def write_to_pov(P, glass_tex, face_index, vertex_color, edge_color):
    """Write the data of a polytope to a POV-Ray include file for rendering.

    :param P: a polytope instance.

    :param glass_tex: glass texture defined in POV-Ray's "textures.inc".

    :param face_index: controls which type of faces are rendered.
        This input can be either an integer or a list/tuple of integers,
        for example if face_index=1 then the second list of faces will be
        rendered, or if face_index=(0, 1) then the first and second lists
        of faces will be rendered.

    :param vertex_color && edge_color: colors defined in POV-Ray's "colors.inc".
    """
    vert_macros = "\n".join(VERT_MACRO.format(i, vertex_color) for i in range(P.num_vertices))
    edge_macros = "\n".join(EDGE_MACRO.format(e[0], e[1], edge_color) for elist in P.edge_indices for e in elist)

    faces = []
    for i, flist in enumerate(P.face_indices):
        try:
            if (face_index == "all" or i == face_index or i in face_index):
                faces += flist
        except:
            pass

    face_macros = "\n".join(FACE_MACRO.format(len(face), helpers.pov_array(face), glass_tex) for face in faces)

    with open("./povray/polychora-data.inc", "w") as f:
        f.write(POV_TEMPLATE.format(
            vertex_color,
            edge_color,
            P.num_vertices,
            P.num_vertices,
            helpers.pov_vector_list(P.vertex_coords),
            vert_macros,
            edge_macros,
            face_macros))


def anim(coxeter_diagram,
         trunc_type,
         description="polychora-rotation4d",
         glass_tex="NBglass",
         face_index=0,
         vertex_color="SkyBlue",
         edge_color="Orange",
         extra_relations=()):
    """Call POV-Ray to render the frames and FFmpeg to generate the movie.
    """
    coxeter_matrix = helpers.make_symmetry_matrix([x.numerator for x in coxeter_diagram])
    mirrors = helpers.get_mirrors(coxeter_diagram)
    P = Polychora(coxeter_matrix, mirrors, trunc_type, extra_relations)
    P.build_geometry()
    write_to_pov(P, glass_tex, face_index, vertex_color, edge_color)
    subprocess.call(POV_COMMAND.format(description), shell=True)
    subprocess.call(FFMPEG_COMMAND.format(description, description), shell=True)


def snub24cell(description="snub-24-cell",
               glass_tex="NBglass",
               face_index="all",
               vertex_color="SkyBlue",
               edge_color="Orange"):
    """Handle the special case snub 24-cell.
    """
    P = Snub24Cell()
    P.build_geometry()
    write_to_pov(P, glass_tex, face_index, vertex_color, edge_color)
    subprocess.call(POV_COMMAND.format(description), shell=True)
    subprocess.call(FFMPEG_COMMAND.format(description, description), shell=True)


# NB: set `FRAMES = 1` at the beginning if you want to run a quick view of these examples,
def main():
    # 5-cell family, symmetry group A_4
    anim((3, 2, 2, 3, 2, 3), (1, 0, 0, 0), "5-cell", vertex_color="Orange", edge_color="Pink")
    """
    anim((3, 2, 2, 3, 2, 3), (1, 1, 0, 0), "truncated-5-cell", vertex_color="Orange", edge_color="Pink")
    anim((3, 2, 2, 3, 2, 3), (0, 1, 0, 0), "rectified-5-cell", vertex_color="Orange", edge_color="Pink", face_index="all")
    anim((3, 2, 2, 3, 2, 3), (0, 1, 1, 0), "bitruncated-5-cell", vertex_color="Orange", edge_color="Pink")
    anim((3, 2, 2, 3, 2, 3), (1, 0, 0, 1), "runcinated-5-cell", vertex_color="Orange", edge_color="Pink")

    # tesseract family, symmetry group B_4
    anim((4, 2, 2, 3, 2, 3), (1, 0, 0, 0), "tesseract", vertex_color="Orange", edge_color="Pink")
    anim((4, 2, 2, 3, 2, 3), (1, 1, 0, 0), "truncated-tesseract", "Dark_Green_Glass", 1)
    anim((4, 2, 2, 3, 2, 3), (1, 0, 1, 0), "cantellated-tesseract", "Dark_Green_Glass", 1)

    # 16-cell family, dual to tesseract
    anim((3, 2, 2, 3, 2, 4), (1, 0, 0, 0), "16-cell", vertex_color="Orange", edge_color="Pink")
    anim((3, 2, 2, 3, 2, 4), (1, 1, 0, 0), "truncated-16-cell", vertex_color="Orange", edge_color="Pink")
    anim((3, 2, 2, 3, 2, 4), (1, 0, 0, 1), "runcinated-16-cell",
         glass_tex="Yellow_Glass", face_index=(0, 1), vertex_color="Orange", edge_color="Pink")

    # 24-cell family, symmetry group F_4
    anim((3, 2, 2, 4, 2, 3), (1, 0, 0, 0), "24-cell", vertex_color="Orange", edge_color="Pink")
    anim((3, 2, 2, 4, 2, 3), (1, 0, 1, 0), "cantellated-24-cell", vertex_color="Orange", edge_color="Pink")
    snub24cell()

    # 120-cell family, symmetry group H_4
    anim((5, 2, 2, 3, 2, 3), (1, 0, 0, 0), "120-cell")

    # 600-cell family, dual to 120-cell
    anim((3, 2, 2, 3, 2, 5), (1, 0, 0, 0), "600-cell")

    # prism and duoprism
    anim((5, 2, 2, 3, 2, 2), (1, 1, 0, 1), "truncated-dodecahedron-prism", glass_tex="Ruby_Glass",
         vertex_color="Coral", edge_color="Violet", face_index=2)
    anim((3, 2, 2, 2, 2, 20), (1, 0, 0, 1), "3-20-duoprism", "Dark_Green_Glass")
    anim((4, 4, 2, Fraction(3, 2), 2, 2), (1, 1, 0, 1),
         extra_relations=((0, 1, 2, 1) * 2,), face_index="all", description="small-cubicuboctahedron-prism")


    # some regular star polytopes (there are 10 of them, all can be rendered in this way)
    anim((3, 2, 2, 5, 2, Fraction(5, 2)), (1, 0, 0, 0), "icosahedral-120-cell", extra_relations=((1, 2, 3, 2)*3,))
    anim((5, 2, 2, Fraction(5, 2), 2, 5), (1, 0, 0, 0), "great-120-cell",
         extra_relations=((0, 1, 2, 1)*3, (1, 2, 3, 2)*3))
    anim((5, 2, 2, 3, 2, Fraction(5, 2)), (1, 0, 0, 0), "grand-120-cell",
         extra_relations=((0, 1, 2, 3, 2, 1)*3,))
    anim((Fraction(5, 2), 2, 2, 5, 2, Fraction(5, 2)), (1, 0, 0, 0),
         "grand-stellated-120-cell", extra_relations=((0, 1, 2, 1)*3, (1, 2, 3, 2)*3))

    # you can also render a 3d polyhedra by embedding it into 4d and project back.
    anim((5, 2, 2, 3, 2, 2), (1, 1, 0, 0), "truncated-dodecahedron",
         glass_tex="NBwinebottle", face_index=(0, 1))
    anim((3, 2, 2, Fraction(5, 2), 2, 2), (1, 0, 0, 0), "great-dodecahedron")
    """

if __name__ == "__main__":
    main()
