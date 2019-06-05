"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make animations of 3d rotating polyhedron
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script computes the data of a given polyhedra and writes it
into a POV-Ray .inc file, then automatically calls POV-Ray
to render the frames and finally calls FFmpeg to convert the frames to
a mp4 movie. You need to have POV-Ray and FFmpeg installed and
set the paths to their executables in `POV_EXE` and `FFMPEG_EXE`.

:copyright (c) 2018 by Zhao Liang.
"""
import subprocess
import os
from fractions import Fraction
from models import Polyhedra, Snub, Catalan3D
import helpers


IMAGE_DIR = "polyhedra_frames"            # directory to save the frames
POV_EXE = "povray"                        # povray command
FFMPEG_EXE = "ffmpeg"                     # ffmpeg command
SCENE_FILE = "polyhedra_animation.pov"    # scene file to render
FRAMES = 1                                # number of frames (120 is quite good)
IMAGE_SIZE = 500                          # image size

# POV-Ray command line options
POV_COMMAND = " cd povray &&" + \
              " {} {}".format(POV_EXE, SCENE_FILE) + \
              " +W{} +H{}".format(IMAGE_SIZE, IMAGE_SIZE) + \
              " +Q11 +A0.001 +R3" + \
              " +KFI0" + \
              " +KFF{}".format(FRAMES - 1) + \
              " -V" + \
              " +O../{}/".format(IMAGE_DIR) + "{}"

# FFmpeg command line options
FFMPEG_COMMAND = " cd {} && ".format(IMAGE_DIR) + \
                 " {} -framerate 15".format(FFMPEG_EXE) + \
                 " -y" + \
                 " -i {}" + \
                 "%0{}d.png".format(len(str(FRAMES - 1))) + \
                 " -crf 18 -c:v libx264" + \
                 " ../{}.mp4"

POV_TEMPLATE = """
#declare nvertices = {};
#declare vertices = array[{}] {{{}}};

{}

{}

{}

rotate <720*clock, 0, 360*clock>
"""


if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)


VERT_MACRO = "Vert(vertices, {}, {})"          # Vert(vertices, ind, v)
EDGE_MACRO = "Edge(vertices, {}, {}, {})"  # Edge(vertices, ind, v1, v2)
FACE_MACRO = "Face(vertices, {}, {}, {})"  # Face(vertices, ind, nsides, indices)


def write_to_pov(P):
    """
    Write the data of a polytope to a POV-Ray include file for rendering.

    :param P: a polytope instance.
    """
    if isinstance(P, Catalan3D):
        vert_macros = "\n".join(VERT_MACRO.format(i, v + sum(len(vlist) for vlist in P.vertex_coords[:i]))
                                for i, vlist in enumerate(P.vertex_coords)
                                for v in range(len(vlist)))
        face_macros = "\n".join(FACE_MACRO.format(0, len(face), helpers.pov_array(face))
                                for face in P.face_indices)
        vertex_coords = helpers.pov_vector_list(P.vertex_coords_flatten)
    else:
        vert_macros = "\n".join(VERT_MACRO.format(0, i) for i in range(P.num_vertices))
        face_macros = "\n".join(FACE_MACRO.format(i, len(face), helpers.pov_array(face))
                                for i, flist in enumerate(P.face_indices)
                                for face in flist)
        vertex_coords = helpers.pov_vector_list(P.vertex_coords)

    edge_macros = "\n".join(EDGE_MACRO.format(i, e[0], e[1])
                            for i, elist in enumerate(P.edge_indices)
                            for e in elist)

    with open("./povray/polyhedra-data.inc", "w") as f:
        f.write(POV_TEMPLATE.format(
            P.num_vertices,
            P.num_vertices,
            vertex_coords,
            vert_macros,
            edge_macros,
            face_macros)
        )


def anim(coxeter_diagram,
         trunc_type,
         description="polyhedra",
         snub=False,
         catalan=False,
         extra_relations=()):
    """Call POV-Ray to render the frames and FFmpeg to generate the movie.
    """
    coxeter_matrix = helpers.make_symmetry_matrix([x.numerator for x in coxeter_diagram])
    mirrors = helpers.get_mirrors(coxeter_diagram)

    if snub:
        P = Snub(coxeter_matrix, mirrors, trunc_type)
    else:
        P = Polyhedra(coxeter_matrix, mirrors, trunc_type, extra_relations)

    if catalan:
        P = Catalan3D(P)

    P.build_geometry()
    write_to_pov(P)

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

    subprocess.call(FFMPEG_COMMAND.format(description, description), shell=True)


# NB: by default this script draws only one frame for each example,
# change `FRAMES` at the beginning of this file to what you want.
def main():
    """
    # Platonic solids
    anim((3, 2, 3), (1, 0, 0), description="tetrahedron")
    anim((4, 2, 3), (1, 0, 0), description="cube")
    anim((3, 2, 4), (1, 0, 0), description="octahedron")
    anim((5, 2, 3), (1, 0, 0), description="dodecahedron")
    anim((3, 2, 5), (1, 0, 0), description="icosahedron")

    # Archimedean solids
    anim((3, 2, 3), (1, 1, 0), description="truncated-tetrahedron")
    anim((4, 2, 3), (1, 1, 0), description="truncated-cube")
    anim((3, 2, 4), (1, 1, 0), description="truncated-octahedron")
    anim((5, 2, 3), (1, 1, 0), description="truncated-dodecahedron")
    anim((3, 2, 5), (1, 1, 0), description="truncated-icosahedron")
    anim((4, 2, 3), (0, 1, 0), description="cuboctahedron")
    anim((5, 2, 3), (0, 1, 0), description="icosidodecahedron")
    anim((4, 2, 3), (1, 0, 1), description="rhombicuboctahedron")
    anim((5, 2, 3), (1, 0, 1), description="rhombicosidodecahedron")
    anim((4, 2, 3), (1, 1, 1), description="truncated-cuboctahedron")
    anim((5, 2, 3), (1, 1, 1), description="truncated-icosidodecahedron")
    anim((4, 2, 3), (1, 1, 1), description="snub-cube", snub=True)
    anim((5, 2, 3), (1, 1, 1), description="snub-dodecahedron", snub=True)

    # prism and antiprism
    anim((7, 2, 2), (1, 0, 1), description="7-prism")
    anim((8, 2, 2), (1, 1, 1), description="8-antiprism", snub=True)

    # Kepler-Poinsot solids
    anim((5, 2, Fraction(5, 2)), (1, 0, 0),
         extra_relations=((0, 1, 2, 1) * 3,), description="great-dodecahedron")
    anim((5, 2, Fraction(5, 2)), (0, 0, 1),
         extra_relations=((0, 1, 2, 1) * 3,), description="small-stellated-dodecahedron")
    anim((3, 2, Fraction(5, 2)), (0, 0, 1), description="great-stellated-dodecahedron")

    # some uniform star polyhedron
    anim((4, 4, Fraction(3, 2)), (1, 1, 0),
         extra_relations=((0, 1, 2, 1) * 2,), description="small-cubicuboctahedron")
    anim((5, 2, Fraction(5, 2)), (1, 1, 0),
         extra_relations=((0, 1, 2, 1) * 3,), description="truncated-great-dodecahedron")
    """
    anim((3, 2, Fraction(5, 2)), (1, 0, 0), description="great-icosahedron")

    """
    # Catalan solids
    anim((3, 2, 3), (1, 1, 0), catalan=True, description="triakis-tetrahedron")
    anim((4, 2, 3), (0, 1, 0), catalan=True, description="rhombic-dodecahedron")
    anim((4, 2, 3), (1, 1, 0), catalan=True, description="triakis-octahedron")
    anim((4, 2, 3), (0, 1, 1), catalan=True, description="tetrakis-hexahedron")
    anim((4, 2, 3), (1, 0, 1), catalan=True, description="deltoidal-icositetrahedron")
    anim((4, 2, 3), (1, 1, 1), catalan=True, description="disdyakis-dodecahedron")
    anim((5, 2, 3), (0, 1, 0), catalan=True, description="rhombic-triacontahedron")
    anim((5, 2, 3), (1, 1, 0), catalan=True, description="triakis-icosahedron")
    anim((5, 2, 3), (0, 1, 1), catalan=True, description="pentakis-dodecahedron")
    anim((5, 2, 3), (1, 0, 1), catalan=True, description="deltoidal-hexecontahedron")
    anim((5, 2, 3), (1, 1, 1), catalan=True, description="disdyakis-triacontahedron")
    anim((4, 2, 3), (1, 1, 1), snub=True, catalan=True, description="pentagonal-icositetrahedron")
    """
    anim((5, 2, 3), (1, 1, 1), snub=True, catalan=True, description="pentagonal-hexecontahedron")


if __name__ == "__main__":
    main()
