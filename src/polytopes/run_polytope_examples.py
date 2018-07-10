"""
This script generates some example images, make sure POV-Ray is installed
and can be found in system path.
"""
from subprocess import call
import models


template = "cd povray/ && povray {} +W600 +H600 +Q11 +A0.001 +R5 -V +O{}"


def make_polyhedra(coxeter_diagram, trunc_type, output):
    P = models.Polyhedra(coxeter_diagram, trunc_type)
    P.build_geometry()
    P.export_pov()
    command = template.format("polyhedra.pov", output)
    call(command, shell=True)


def make_polychora(coxeter_diagram, trunc_type, output, flat=True):
    P = models.Polychora(coxeter_diagram, trunc_type)
    P.build_geometry()
    P.export_pov()
    script = "flat_polychora.pov" if flat else "curved_polychora.pov"
    command = template.format(script, output)
    call(command, shell=True)


def make_duoprisms(pq, weights=(1.0, 1.0)):
    p, q = pq
    P = models.Polychora((p, 2, 2, 2, 2, q), (weights[0], 0, weights[1], 0))
    P.build_geometry()
    P.export_pov()
    command = template.format("duoprism.pov", "{}-{}-duoprism".format(p, q))
    call(command, shell=True)


def make_120_cell():
    P = models.Polychora((5, 2, 2, 3, 2, 3), (1, 0, 0, 0))
    P.build_geometry()
    P.export_pov()
    command = template.format("dimensions_120_cell.pov", "120-cell")
    call(command, shell=True)


def make_prisms(pq, trunc_type):
    p, q = pq
    P = models.Polychora((p, 2, 2, q, 2, 2), trunc_type + (1,))
    P.build_geometry()
    P.export_pov()
    command = template.format("prism.pov", "{}-{}-prism".format(p, q))
    call(command, shell=True)


if __name__ == "__main__":
    make_polyhedra((5, 2, 3), (1, 1, 1), "omnitruncated-dodecahedron")
    make_120_cell()
    make_duoprisms((6, 6), weights=(1.0, 0.8))
    make_prisms((5, 3), (1, 0, 1))
    make_polychora((5, 2, 2, 3, 2, 3), (1, 0, 1, 1), "120-cell-trunc", flat=False)
