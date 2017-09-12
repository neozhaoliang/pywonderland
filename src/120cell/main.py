# pylint: disable=unused-import
# pylint: disable=undefined-variable

import numpy as np
from vapory import *
from palettable.colorbrewer.qualitative import Set1_6
from penrose import Penrose
from cell120 import Cell_120

# 'Media' was not implemented yet when this script was written
class Media(POVRayElement):
    """Media()"""


colorlist = Set1_6.mpl_colors
default = Finish('ambient', 0.3, 'diffuse', 0.7, 'phong', 1)

penrose_config = {'vertex_size': 0.05,
                  'vertex_texture': Texture(Pigment('color', 'White'), default),
                  'edge_thickness': 0.05,
                  'edge_texture': Texture(Pigment('color', 'White'), default),
                  'default': default}

cell_120_config = {'vertex_size': 0.05,
                   'vertex_texture': Texture(Pigment('color', 'White'), default),
                   'edge_thickness': 0.08,
                   'edge_texture': Texture(Pigment('color', 'White', 'transmit', 0),
                                           Finish('reflection', 0.4, 'brilliance', 0.4)),
                   'face_texture': Texture(Pigment('color', 'Blue', 'transmit', 0.7),
                                           Finish('reflection', 0, 'brilliance', 0)),
                   'interior': Interior(Media('intervals', 1, 'samples', 1, 1, 'emission', 1))}


# shift = [0.5] * 5: the star pattern
leftwall = Penrose(num_lines=10,
                   shift=(0.5, 0.5, 0.5, 0.5, 0.5),
                   thin_color=colorlist[0],
                   fat_color=colorlist[1],
                   **penrose_config).put_objs('scale', 1.5,
                                              'rotate', (0, -45, 0),
                                              'translate', (-18, 0, 18))

# a random pattern
rightwall = Penrose(num_lines=10,
                    shift=np.random.random(5),
                    thin_color=colorlist[2],
                    fat_color=colorlist[3],
                    **penrose_config).put_objs('scale', 1.5,
                                               'rotate', (0, 45, 0),
                                               'translate', (18, 0, 18))

# when the numbers in shift sums to zero (mod 1), it's the standard Penrose tiling.
floor = Penrose(num_lines=10,
                shift=(0.1, 0.2, -0.3, 0.6, -0.6),
                thin_color=colorlist[4],
                fat_color=colorlist[5],
                **penrose_config).put_objs('scale', 1.5,
                                           'rotate', (90, 0, 0))

cell_120 = Cell_120(**cell_120_config).put_objs('scale', 2.2,
                                                'translate',
                                                (0, -Cell_120.bottom, 0))

camera = Camera('location', (0, 12, -30), 'look_at', (0, 0, 20))
light = LightSource((-30, 30, -30), 'color', (1, 1, 1))
objects = [light, leftwall, rightwall, floor, cell_120]
scene = Scene(camera, objects, included=['colors.inc'])
scene.render('penrose_120cell.png', width=600, height=480, antialiasing=0.001)
