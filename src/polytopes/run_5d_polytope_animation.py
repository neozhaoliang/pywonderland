"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make animations of rotating 5d uniform polytopes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script computes the data of a given 5d polytope and writes it
into a POV-Ray .inc file, then automatically calls POV-Ray
to render the frames and finally calls FFmpeg to convert the frames to
a mp4 movie. You need to have POV-Ray and FFmpeg installed and
set the paths to their executables in `POV_EXE` and `FFMPEG_EXE`.

:copyright (c) 2020 by Zhao Liang.
"""
import subprocess
import os
from models import Polytope5D
import helpers


IMAGE_DIR = "5drotation_frames"           # directory to save the frames
POV_EXE = "povray"                        # povray command
FFMPEG_EXE = "ffmpeg"                     # ffmpeg command
SCENE_FILE = "5drotation_animation.pov"   # scene file to render
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
            helpers.pov_vector_list([helpers.proj4d(v) for v in P.vertex_coords]),
            vert_macros,
            edge_macros,
            face_macros))


def anim(coxeter_diagram,
         trunc_type,
         description="polychora-rotation5d",
         glass_tex="NBglass",
         face_index=0,
         vertex_color="SkyBlue",
         edge_color="Orange",
         extra_relations=()):
    """Call POV-Ray to render the frames and FFmpeg to generate the movie.
    """
    P = Polytope5D(coxeter_diagram, trunc_type, extra_relations)
    P.build_geometry()
    write_to_pov(P, glass_tex, face_index, vertex_color, edge_color)
    subprocess.call(POV_COMMAND.format(description), shell=True)
    subprocess.call(FFMPEG_COMMAND.format(description, description), shell=True)


# NB: set `FRAMES = 1` at the beginning if you want to run a quick view of these examples,
def main():
    anim((4, 2, 2, 2, 3, 2, 2, 3, 2, 3), (1, 0, 0, 0, 0), description="5-cube")
    anim((3, 2, 2, 2, 3, 2, 2, 3, 2, 3), (1, 0, 0, 0, 0), description="5-simplex")
    anim((3, 2, 2, 2, 3, 2, 2, 3, 2, 4), (1, 0, 0, 0, 0), description="5-orthoplex")
    anim((3, 2, 2, 2, 3, 2, 3, 3, 2, 2), (1, 0, 0, 0, 0), description="5-demicube")
    anim((3, 2, 2, 2, 4, 2, 2, 3, 2, 2), (1, 0, 0, 0, 1), description="24-cell-prism")


if __name__ == "__main__":
    main()
