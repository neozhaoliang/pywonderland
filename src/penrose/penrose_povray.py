# pylint: disable=unused-import

from itertools import combinations, product
import numpy as np
from vapory import *


SHIFT = np.random.random(5)
GRIDS = [np.exp(2j * np.pi * i / 5) for i in range(5)]
THIN_RHOMBUS_COLOR = (1, 0, 1)
FAT_RHOMBUS_COLOR = (0, 1, 1)
EDGE_COLOR = (1, 1, 1)
EDGE_THICKNESS = 0.05
NUM_LINES = 15
SCALE = 10
DEFAULT = Finish('ambient', 0.3, 'diffuse', 0.7, 'phong', 1)


def rhombus(r, s, kr, ks):
    if (s - r)**2 % 5 == 1:
        color = THIN_RHOMBUS_COLOR
    else:
        color = FAT_RHOMBUS_COLOR

    point = (GRIDS[r] * (ks - SHIFT[s])
             - GRIDS[s] * (kr - SHIFT[r])) *1j / GRIDS[s-r].imag
    index = [np.ceil((point/grid).real + shift)
             for grid, shift in zip(GRIDS, SHIFT)]
    vertices = []
    for index[r], index[s] in [(kr, ks), (kr+1, ks), (kr+1, ks+1), (kr, ks+1)]:
        vertices.append(np.dot(index, GRIDS))

    vertices_real = [(z.real, z.imag) for z in vertices]
    return vertices_real, color


def tile(num_lines):
    for r, s in combinations(range(5), 2):
        for kr, ks in product(range(-num_lines, num_lines+1), repeat=2):
            yield rhombus(r, s, kr, ks)



camera = Camera('location', (0, 60, -100), 'look_at', (0, 0, 40))
light1 = LightSource((50, -50, -50), 'color', (1, 1, 1))
light2 = LightSource((-50, 50, -50), 'color', (1, 1, 1))



objects =[light1, light2]

for rhombi, color in tile(NUM_LINES):
    p1, p2, p3, p4 = rhombi
    polygon = Polygon(5, p1, p2, p3, p4, p1,
                      Texture(Pigment('color', color), DEFAULT),
                      'rotate', (90, 0, 0),
                      'scale', SCALE)

    for p, q in zip(rhombi, [p2, p3, p4, p1]):
        cylinder = Cylinder(p, q, EDGE_THICKNESS,
                            Texture(Pigment('color', EDGE_COLOR), DEFAULT),
                            'rotate', (90, 0, 0),
                            'scale', SCALE)
        objects.append(cylinder)
    objects.append(polygon)


THIN_RHOMBUS_COLOR = (0.75, 0.25, 1)
FAT_RHOMBUS_COLOR = (1, 0.25, 0.5)
for rhombi, color in tile(NUM_LINES):
    p1, p2, p3, p4 = rhombi
    polygon = Polygon(5, p1, p2, p3, p4, p1,
                      Texture(Pigment('color', color), DEFAULT),
                      'rotate', (0, -60, 0),
                      'translate', (-10, 0, 10),
                      'scale', SCALE)

    for p, q in zip(rhombi, [p2, p3, p4, p1]):
        cylinder = Cylinder(p, q, EDGE_THICKNESS,
                            Texture(Pigment('color', EDGE_COLOR), DEFAULT),
                            'rotate', (0, -60, 0),
                            'translate', (-10, 0, 10),
                            'scale', SCALE)
        objects.append(cylinder)
    objects.append(polygon)

THIN_RHOMBUS_COLOR = (0.5, 0, 1)
FAT_RHOMBUS_COLOR = (0, 0.5, 1)
for rhombi, color in tile(NUM_LINES):
    p1, p2, p3, p4 = rhombi
    polygon = Polygon(5, p1, p2, p3, p4, p1,
                      Texture(Pigment('color', color), DEFAULT),
                      'rotate', (0, 60, 0),
                      'translate', (10, 0, 10),
                      'scale', SCALE)

    for p, q in zip(rhombi, [p2, p3, p4, p1]):
        cylinder = Cylinder(p, q, EDGE_THICKNESS,
                            Texture(Pigment('color', EDGE_COLOR), DEFAULT),
                            'rotate', (0, 60, 0),
                            'translate', (10, 0, 10),
                            'scale', SCALE)
        objects.append(cylinder)
    objects.append(polygon)


scene = Scene(camera, objects)
scene.render('penrose_povray.png', width=600, height=480, antialiasing=0.001, remove_temp=False)
