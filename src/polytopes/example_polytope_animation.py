"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make animations of rotating polytopes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script computes the data of a given polytope and writes it
into a POV-Ray .inc file, then automatically calls POV-Ray
to render the frames and calls FFmpeg to convert the frames to
a mp4 movie. You need to have POV-Ray and FFmpeg installed and
set the path to their executables in `POV_EXE` and `FFMPEG_EXE`.

:copyright (c) 2018 by Zhao Liang.
"""
import os
import subprocess
from fractions import Fraction

import polytopes.models as models

IMAGE_DIR = "polytope_frames"  # directory to save the frames
POV_EXE = "povray"  # povray command
FFMPEG_EXE = "ffmpeg"  # ffmpeg command
FRAMES = 1  # number of frames (120 is quite good)
IMAGE_SIZE = 500  # image size
SUPERSAMPLING_LEVEL = 1  # supersampling level
DATAFILE_NAME = "polytope-data.inc"  # export data to this file

data_file = os.path.join(os.getcwd(), "povray", DATAFILE_NAME)

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# POV-Ray command line options
POV_COMMAND = (
    " cd povray && {}".format(POV_EXE)
    + " {}"
    + " +W{} +H{}".format(IMAGE_SIZE, IMAGE_SIZE)
    + " +Q11 +A0.003 +R{}".format(SUPERSAMPLING_LEVEL)
    + " +KFI0"
    + " +KFF{}".format(FRAMES - 1)
    + " -V"
    + " +O../{}/".format(IMAGE_DIR)
    + "{}"
)

# FFmpeg command line options
FFMPEG_COMMAND = (
    " cd {} && ".format(IMAGE_DIR)
    + " {} -framerate 12".format(FFMPEG_EXE)
    + " -y"
    + " -i {}"
    + "%0{}d.png".format(len(str(FRAMES - 1)))
    + " -crf 18 -c:v libx264"
    + " ../{}.mp4"
)

POV_TEMPLATE = """
#declare vertices = {};

#declare edges = {};

#declare faces = {};
"""


def anim(
    coxeter_diagram,
    trunc_type,
    extra_relations=(),
    snub=False,
    description="polytope-animation",
):
    """
    Call POV-Ray to render the frames and call FFmpeg to generate the movie.
    """
    if len(coxeter_diagram) == 3:
        if snub:
            P = models.Snub(coxeter_diagram, extra_relations=extra_relations)
        else:
            P = models.Polyhedra(coxeter_diagram, trunc_type, extra_relations)
        scene_file = "polyhedra_animation.pov"

    elif len(coxeter_diagram) == 6:
        P = models.Polychora(coxeter_diagram, trunc_type, extra_relations)
        scene_file = "polytope_animation.pov"

    elif len(coxeter_diagram) == 10:
        P = models.Polytope5D(coxeter_diagram, trunc_type, extra_relations)
        scene_file = "polytope_animation.pov"

    else:
        raise ValueError("Invalid Coxeter diagram: {}".format(coxeter_diagram))

    P.build_geometry()

    # POV-Ray does not support 5d vectors well, so project the vertices in python
    if isinstance(P, models.Polytope5D):
        P.proj4d()
    vert_data, edge_data, face_data = P.get_povray_data()
    with open(data_file, "w") as f:
        f.write(POV_TEMPLATE.format(vert_data, edge_data, face_data))

    subprocess.call(POV_COMMAND.format(scene_file, description), shell=True)
    subprocess.call(FFMPEG_COMMAND.format(description, description), shell=True)
    return P


def snub24cell(description="snub-24-cell"):
    """Handle the special case snub 24-cell.
    """
    P = models.Snub24Cell()
    P.build_geometry()
    vert_data, edge_data, face_data = P.get_povray_data()
    with open(data_file, "w") as f:
        f.write(POV_TEMPLATE.format(vert_data, edge_data, face_data))
    scene_file = "polytope_animation.pov"
    subprocess.call(POV_COMMAND.format(scene_file, description), shell=True)
    subprocess.call(FFMPEG_COMMAND.format(description, description), shell=True)
    return P


def main():
    # Platonic solids
    anim((3, 2, 3), (1, 0, 0), description="tetrahedron")
    anim((4, 2, 3), (1, 0, 0), description="cube")
    anim((3, 2, 4), (1, 0, 0), description="octahedron")
    anim((5, 2, 3), (1, 0, 0), description="dodecahedron")
    anim((3, 2, 5), (1, 0, 0), description="icosahedron")
    # Archimedian solids
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
    anim((4, 2, 3), (1, 1, 1), snub=True, description="snub-cube")
    anim((5, 2, 3), (1, 1, 1), snub=True, description="snub-dodecahedron")
    # prism and antiprism
    anim((7, 2, 2), (1, 0, 1), description="7-prism")
    anim((8, 2, 2), (1, 1, 1), snub=True, description="8-antiprism")
    # Kepler-Poinsot solids
    anim(
        (5, 2, Fraction(5, 2)),
        (1, 0, 0),
        extra_relations=((0, 1, 2, 1) * 3,),
        description="great-dodecahedron",
    )
    anim(
        (5, 2, Fraction(5, 2)),
        (0, 0, 1),
        extra_relations=((0, 1, 2, 1) * 3,),
        description="small-stellated-dodecahedron",
    )
    anim((3, 2, Fraction(5, 2)), (0, 0, 1), description="great-stellated-dodecahedron")
    anim((3, 2, Fraction(5, 2)), (1, 0, 0), description="great-icosahedron")
    # 5-cell family, symmetry group A_4
    anim((3, 2, 2, 3, 2, 3), (1, 0, 0, 0), description="5-cell")
    anim((3, 2, 2, 3, 2, 3), (1, 1, 0, 0), description="truncated-5-cell")
    anim((3, 2, 2, 3, 2, 3), (0, 1, 0, 0), description="rectified-5-cell")
    anim((3, 2, 2, 3, 2, 3), (0, 1, 1, 0), description="bitruncated-5-cell")
    anim((3, 2, 2, 3, 2, 3), (1, 0, 0, 1), description="runcinated-5-cell")

    # tesseract family, symmetry group B_4
    anim((4, 2, 2, 3, 2, 3), (1, 0, 0, 0), description="tesseract")
    anim((4, 2, 2, 3, 2, 3), (1, 1, 0, 0), description="truncated-tesseract")
    anim((4, 2, 2, 3, 2, 3), (1, 0, 1, 0), description="cantellated-tesseract")

    # 16-cell family, dual to tesseract
    anim((3, 2, 2, 3, 2, 4), (1, 0, 0, 0), description="16-cell")
    anim((3, 2, 2, 3, 2, 4), (1, 1, 0, 0), description="truncated-16-cell")
    anim((3, 2, 2, 3, 2, 4), (1, 0, 0, 1), description="runcinated-16-cell")

    # 24-cell family, symmetry group F_4
    anim((3, 2, 2, 4, 2, 3), (1, 0, 0, 0), description="24-cell")
    anim((3, 2, 2, 4, 2, 3), (1, 0, 1, 0), description="cantellated-24-cell")
    snub24cell()
    # 120-cell family, symmetry group H_4
    anim((5, 2, 2, 3, 2, 3), (1, 0, 0, 0), description="120-cell")

    # 600-cell family, dual to 120-cell
    P = anim((3, 2, 2, 3, 2, 5), (1, 0, 0, 0), description="600-cell")
    P.draw_on_coxeter_plane(svgpath="600-cell.svg")

    # 4d prism and duoprism
    anim((5, 2, 2, 3, 2, 2), (1, 1, 0, 1), description="truncated-dodecahedron-prism")
    anim((3, 2, 2, 2, 2, 20), (1, 0, 0, 1), description="3-20-duoprism")

    # you can also render a 3d polyhedra by embedding it into 4d and project back.
    anim((5, 2, 2, 3, 2, 2), (1, 1, 0, 0), description="truncated-dodecahedron")
    anim(
        (3, 2, 2, Fraction(5, 2), 2, 2), (1, 0, 0, 0), description="great-dodecahedron"
    )

    # some regular star polytopes (there are 10 of them, all can be rendered in this way)
    anim(
        (3, 2, 2, 5, 2, Fraction(5, 2)),
        (1, 0, 0, 0),
        extra_relations=((1, 2, 3, 2) * 3,),
        description="icosahedral-120-cell",
    )

    anim(
        (5, 2, 2, Fraction(5, 2), 2, 5),
        (1, 0, 0, 0),
        extra_relations=((0, 1, 2, 1) * 3, (1, 2, 3, 2) * 3),
        description="great-120-cell",
    )

    anim(
        (5, 2, 2, 3, 2, Fraction(5, 2)),
        (1, 0, 0, 0),
        extra_relations=((0, 1, 2, 3, 2, 1) * 3,),
        description="grand-120-cell",
    )

    P = anim(
        (Fraction(5, 2), 2, 2, 5, 2, Fraction(5, 2)),
        (1, 0, 0, 0),
        extra_relations=((0, 1, 2, 1) * 3, (1, 2, 3, 2) * 3),
        description="grand-stellated-120-cell",
    )
    P.draw_on_coxeter_plane(svgpath="grand-stellated-120-cell.svg")

    # and 5d polytopes
    P = anim((4, 2, 2, 2, 3, 2, 2, 3, 2, 3), (1, 0, 0, 0, 0), description="5d-cube")
    P.draw_on_coxeter_plane(svgpath="5-cube.svg")

    # some star polyhedron
    anim(
        (Fraction(3, 2), 3, 3),
        (1, 0, 1),
        description="octahemioctahedron",
        extra_relations=((0, 1, 2, 1) * 2,),
    )

    anim(
        (Fraction(3, 2), 5, 5),
        (1, 0, 1),
        description="small-dodecicosidodecahedron",
        extra_relations=((0, 1, 2, 1) * 2,),
    )

    anim(
        (Fraction(3, 2), 4, 4),
        (1, 0, 1),
        description="small-cubicuboctahedron",
        extra_relations=((0, 1, 2, 1) * 2,),
    )

    anim(
        (Fraction(5, 3), 3, 5),
        (0, 1, 0),
        description="ditrigonal-dodecadodecahedron",
        extra_relations=((0, 1, 2, 1) * 2,),
    )


if __name__ == "__main__":
    main()
