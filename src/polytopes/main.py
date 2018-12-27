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
from fractions import Fraction
import models
import helpers


# use higher supersampling level and smaller
# antialiasing level to get better images
POVRAY_EXE = "povray"
IMAGE_SIZE = 600
IMAGE_QUALITY_LEVEL = 11  # between 0-11
SUPER_SAMPLING_LEVEL = 3  # between 1-9
ANTIALIASING_LEVEL = 0.001

POV_COMMAND = "cd povray && " + \
              POVRAY_EXE + \
              " +I{}" + \
              " +W{}".format(IMAGE_SIZE) + \
              " +H{}".format(IMAGE_SIZE) + \
              " +Q{}".format(IMAGE_QUALITY_LEVEL) + \
              " +A{}".format(ANTIALIASING_LEVEL) + \
              " +R{}".format(SUPER_SAMPLING_LEVEL) + \
              " +O../{}"


def _render_model(P, render_file, output=None):
    """
    parameters
    ----------
    :P: a polyhedra/polychora that has been initialized.
    :render_file: the POV-Ray scene decription file.
    :output: output file name.
    """
    if output is None:
        output = render_file[:-4]

    P.build_geometry()
    P.export_pov()
    print("rendering {} with {} vertices, {} edges, {} faces".format(output,
                                                                     P.num_vertices,
                                                                     P.num_edges,
                                                                     P.num_faces))
    command = POV_COMMAND.format(render_file, output)
    process = subprocess.Popen(command,
                               shell=True,
                               stderr=subprocess.PIPE,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE)

    out, err = process.communicate()
    if process.returncode:
        print(type(err), err)
        raise IOError("POVRay rendering failed with the following error: " + err.decode("ascii"))


def render_polyhedra(coxeter_diagram,
                     trunc_type,
                     render_file="polyhedra.pov",
                     output=None,
                     snub=False):
    """
    The main entrance for rendering 3d polyhedron.
    """
    coxeter_matrix = helpers.fill_matrix(coxeter_diagram)
    mirrors = helpers.get_mirrors(coxeter_diagram)
    if snub:
        P = models.Snub(coxeter_matrix, mirrors, trunc_type)
    else:
        P = models.Polyhedra(coxeter_matrix, mirrors, trunc_type)

    _render_model(P, render_file, output)


def render_polychora(coxeter_diagram,
                     trunc_type,
                     render_file,
                     output=None):
    """
    The main entrance for rendering 4d polychoron.
    """
    coxeter_matrix = helpers.fill_matrix(coxeter_diagram)
    mirrors = helpers.get_mirrors(coxeter_diagram)
    P = models.Polychora(coxeter_matrix, mirrors, trunc_type)
    _render_model(P, render_file, output)


def render_star_polyhedra(coxeter_diagram,
                          trunc_type,
                          extra_relation=(),
                          render_file="star-polyhedra.pov",
                          output=None):
    """
    The main entrance for rendering 3d star polyhedron.
    """
    coxeter_matrix = helpers.fill_matrix([x.numerator for x in coxeter_diagram])
    mirrors = helpers.get_mirrors(coxeter_diagram)
    P = models.StarPolyhedra(coxeter_matrix, mirrors, trunc_type, extra_relation)
    _render_model(P, render_file, output)


def main():
    # platonic solids
    """
    render_polyhedra((3, 2, 3), (1, 0, 0), output="tetrahedron")
    render_polyhedra((4, 2, 3), (1, 0, 0), output="cube")
    render_polyhedra((3, 2, 4), (1, 0, 0), output="octahedron")
    """
    render_polyhedra((5, 2, 3), (1, 0, 0), output="dodecahedron")
    render_polyhedra((3, 2, 5), (1, 0, 0), output="icosahedron")

    # archimedean solids
    """
    render_polyhedra((3, 2, 3), (1, 1, 0), output="truncated-tetrahedron")
    render_polyhedra((4, 2, 3), (1, 1, 0), output="truncated-cube")
    render_polyhedra((3, 2, 4), (1, 1, 0), output="truncated-octahedron")
    render_polyhedra((5, 2, 3), (1, 1, 0), output="truncated-dodecahedron")
    render_polyhedra((3, 2, 5), (1, 1, 0), output="truncated-icosahedron")
    render_polyhedra((4, 2, 3), (0, 1, 0), output="cuboctahedron")
    render_polyhedra((5, 2, 3), (0, 1, 0), output="icosidodecahedron")
    render_polyhedra((4, 2, 3), (1, 0, 1), output="rhombicuboctahedron")
    render_polyhedra((5, 2, 3), (1, 0, 1), output="rhombicosidodecahedron")
    """
    render_polyhedra((4, 2, 3), (1, 1, 1), output="truncated-cuboctahedron")
    render_polyhedra((5, 2, 3), (1, 1, 1), output="truncated-icosidodecahedron")
    render_polyhedra((4, 2, 3), (1, 1, 1), output="snub-cube", snub=True)
    render_polyhedra((5, 2, 3), (1, 1, 1), output="snub-dodecahedron", snub=True)

    # prism and antiprism
    render_polyhedra((7, 2, 2), (1, 0, 1), output="7-prism")
    render_polyhedra((8, 2, 2), (1, 1, 1), output="8-antiprism", snub=True)

    # Kepler-Poinsot solids
    render_star_polyhedra((5, 2, Fraction(5, 2)),
                          (1, 0, 0),
                          extra_relation=(0, 1, 2, 1) * 3,
                          output="great-dodecahedron")
    render_star_polyhedra((5, 2, Fraction(5, 2)),
                          (0, 0, 1),
                          extra_relation=(0, 1, 2, 1) * 3,
                          output="small-stellated-dodecahedron")
    render_star_polyhedra((3, 2, Fraction(5, 2)), (0, 0, 1), output="great-stellated-dodecahedron")
    render_star_polyhedra((3, 2, Fraction(5, 2)), (1, 0, 0), output="great-icosahedron")

    # regular polychora
    render_polychora((3, 2, 2, 3, 2, 3), (1, 0, 0, 0), "5-cell-1000.pov", "5-cell")
    """
    render_polychora((4, 2, 2, 3, 2, 3), (1, 0, 0, 0), "8-cell-1000.pov", "8-cell")
    render_polychora((3, 2, 2, 3, 2, 4), (1, 0, 0, 0), "16-cell-1000.pov", "16-cell")
    render_polychora((3, 2, 2, 4, 2, 3), (1, 0, 0, 0), "24-cell-1000.pov", "24-cell")
    render_polychora((5, 2, 2, 3, 2, 3), (1, 0, 0, 0), "120-cell-1000.pov", "120-cell")
    """
    render_polychora((3, 2, 2, 3, 2, 5), (1, 0, 0, 0), "600-cell-1000.pov", "600-cell")

    # some truncated polychoron. for more examples see the .pov files in the povray directory
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

    # you can also embed a 3d polyhedra in 4d and then project it back to 3d
    render_polychora((3, 2, 2, 5, 2, 2), (1, 1, 0, 0), "polyhedra-ball.pov", output="buckyball")


if __name__ == "__main__":
    main()
