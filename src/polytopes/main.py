# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Render 3D and 4D Polytopes using Python and POV-Ray
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage:
  1. Make sure the free raytracer POV-Ray is installed on your
     computer and can be found in system environment variables.

  2. Run python main.py and wait for amazing things to happen!
"""
import subprocess
import models


# use higher supersampling level (e.g. 5) and smaller antialiasing level
# (e.g. 0.001) to get betweer images
POVRAY_EXE = "povray"
IMAGE_SIZE = 600
IMAGE_QUALITY_LEVEL = 11  # between 0-11
SUPER_SAMPLING_LEVEL = 2  # between 1-9
ANTIALIASING_LEVEL = 0.01

TEMPLATE = "cd povray/ && " + \
           POVRAY_EXE + \
           " +I{}"+ \
           " +W" + str(IMAGE_SIZE) + \
           " +H" + str(IMAGE_SIZE) + \
           " +Q" + str(IMAGE_QUALITY_LEVEL) + \
           " +A" + str(ANTIALIASING_LEVEL) + \
           " +R" + str(SUPER_SAMPLING_LEVEL) + \
           " +O{}"


def render_polyhedra(coxeter_diagram,
                     trunc_type,
                     render_file="polyhedra.pov",
                     description=None,
                     snub=False):
    if snub:
        P = models.Snub(coxeter_diagram, trunc_type)
    else:
        P = models.Polyhedra(coxeter_diagram, trunc_type)

    if not description:
        description = render_file[:-4]

    P.build_geometry()
    P.export_pov()
    command = TEMPLATE.format(render_file, description)
    subprocess.call(command, shell=True)


def render_polychora(coxeter_diagram,
                     trunc_type,
                     render_file,
                     description=None):
    if not description:
        description = render_file[:-4]

    P = models.Polychora(coxeter_diagram, trunc_type)
    P.build_geometry()
    P.export_pov()
    command = TEMPLATE.format(render_file, description)
    subprocess.call(command, shell=True)


if __name__ == "__main__":
    # platonic solids
    """
    render_polyhedra((3, 2, 3), (1, 0, 0), description="tetrahedron")
    render_polyhedra((4, 2, 3), (1, 0, 0), description="cube")
    render_polyhedra((3, 2, 4), (1, 0, 0), description="octahedron")
    render_polyhedra((5, 2, 3), (1, 0, 0), description="dodecahedron")
    """
    render_polyhedra((3, 2, 5), (1, 0, 0), description="icosahedron")

    # archimedean solids
    """
    render_polyhedra((3, 2, 3), (1, 1, 0), description="truncated-tetrahedron")
    render_polyhedra((4, 2, 3), (1, 1, 0), description="truncated-cube")
    render_polyhedra((3, 2, 4), (1, 1, 0), description="truncated-octahedron")
    render_polyhedra((5, 2, 3), (1, 1, 0), description="truncated-dodecahedron")
    render_polyhedra((3, 2, 5), (1, 1, 0), description="truncated-icosahedron")
    render_polyhedra((4, 2, 3), (0, 1, 0), description="cuboctahedron")
    render_polyhedra((5, 2, 3), (0, 1, 0), description="icosidodecahedron")
    render_polyhedra((4, 2, 3), (1, 0, 1), description="rhombicuboctahedron")
    render_polyhedra((5, 2, 3), (1, 0, 1), description="rhombicosidodecahedron")
    render_polyhedra((4, 2, 3), (1, 1, 1), description="truncated-cuboctahedron")
    """
    render_polyhedra((5, 2, 3), (1, 1, 1), description="truncated-icosidodecahedron")
    render_polyhedra((4, 2, 3), (1, 1, 1), description="snub-cube", snub=True)
    render_polyhedra((5, 2, 3), (1, 1, 1), description="snub-dodecahedron", snub=True)

    # prism and antiprism
    render_polyhedra((7, 2, 2), (1, 0, 1), description="7-prism")
    render_polyhedra((8, 2, 2), (1, 1, 1), description="8-antiprism", snub=True)

    # regular polychora
    render_polychora((3, 2, 2, 3, 2, 3), (1, 0, 0, 0), "5-cell-1000.pov", "5-cell")
    """
    render_polychora((4, 2, 2, 3, 2, 3), (1, 0, 0, 0), "8-cell-1000.pov", "8-cell")
    render_polychora((3, 2, 2, 3, 2, 4), (1, 0, 0, 0), "16-cell-1000.pov", "16-cell")
    render_polychora((3, 2, 2, 4, 2, 3), (1, 0, 0, 0), "24-cell-1000.pov", "24-cell")
    render_polychora((5, 2, 2, 3, 2, 3), (1, 0, 0, 0), "120-cell-1000.pov", "120-cell")
    render_polychora((3, 2, 2, 3, 2, 5), (1, 0, 0, 0), "600-cell-1000.pov", "600-cell")
    """
    # some truncated polychora
    # for more examples see the .pov files in the povray directory
    """
    render_polychora((3, 2, 2, 3, 2, 3), (1, 1, 1, 0), "5-cell-1110.pov", "cantitruncated-5-cell")
    render_polychora((4, 2, 2, 3, 2, 3), (1, 1, 0, 0), "8-cell-1100.pov", "truncated-8-cell")
    render_polychora((3, 2, 2, 3, 2, 4), (1, 0, 0, 1), "16-cell-1001.pov", "runcinated-16-cell")
    render_polychora((3, 2, 2, 4, 2, 3), (1, 1, 1, 0), "24-cell-1110.pov", "cantitruncated-24-cell")
    """
    render_polychora((3, 2, 2, 3, 2, 5), (1, 1, 0, 0), "600-cell-1100.pov", "truncated-600-cell")

    # 4d prism and duoprism
    render_polychora((6, 2, 2, 2, 2, 8), (1, 0, 1.6, 0), "duoprism.pov", "6-8-duoprism")
    render_polychora((5, 2, 2, 3, 2, 2), (1, 1, 0, 1), "prism.pov", "5-3-prism")
