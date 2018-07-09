"""
This script generates some example images, make sure POV-Ray is installed
and can be found in system path.
"""
from subprocess import call
import models


template = "cd povray/ && povray {} +W600 +H600 +Q11 +A0.001 +R5 -V +O{}"


# omnitrncated dodecahedron
P = models.Polyhedra((5, 2, 3), (1, 1, 1))
print("Computing data for the omnitruncated dodecahedron")
P.build_geometry()
P.export_pov()
command = template.format("polyhedra.pov", "ominitruncated-dodecahedron.png")
call(command, shell=True)

# dodecahedral prism
P = models.Polychora((5, 2, 2, 3, 2, 2), (1, 0, 0, 1))
print("Computing data for the dodecahedral prism")
P.build_geometry()
P.export_pov()
command = template.format("flat_polychora.pov", "dodecahedral-prism.png")
call(command, shell=True)

# 4-3 duoprism
P = models.Polychora((4, 2, 2, 2, 2, 3), (1, 0, 1, 1))
print("Computing data for the 4-3 duoprism")
P.build_geometry()
P.export_pov()
command = template.format("flat_polychora.pov", "duoprism4-3.png")
call(command, shell=True)

# 120-cell in the dimensions video
P = models.Polychora((5, 2, 2, 3, 2, 3), (1, 0, 0, 0))
print("Computing data for the 120-cell")
P.build_geometry()
P.export_pov()
command = template.format("dimensions_120_cell.pov", "120-cell.png")
call(command, shell=True)

# omnitruncated hypercube
P = models.Polychora((4, 2, 2, 3, 2, 3), (1, 1, 1, 1))
print("Computing data for the omnitruncated hypercube")
P.build_geometry()
P.export_pov()
command = template.format("flat_polychora.pov", "omnitruncated-hypercube.png")
call(command, shell=True)
