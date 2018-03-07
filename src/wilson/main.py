# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make GIF animations of various maze generation
and maze solving algorithms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from colorsys import hls_to_rgb
import gifmaze as gm
from gentext import generate_text_mask
from algorithms import wilson, bfs


# -----------------------------------------------
# create a GIFSurface instance and set the colors
# -----------------------------------------------
surface = gm.GIFSurface.from_image('teacher.png')

palette = [52, 51, 50,  # wall color, the same with the color of the blackboard
           200, 200, 200,  # tree color
           255, 0, 255]  # path color

for i in range(256):
    rgb = hls_to_rgb((i / 360.0) % 1, 0.5, 1.0)
    palette += [int(round(255 * x)) for x in rgb]

surface.set_palette(palette)

# --------------------------------------------------------
# create a maze instance and set its position in the image
# --------------------------------------------------------
size = (surface.width, surface.height)
mask = generate_text_mask(size, 'UST', 'ubuntu.ttf', 350)
maze = gm.Maze(117, 73, mask=mask).scale(4).translate((69, 49))

# ------------------------------------------------------------------
# create an animation instance to write the animation to the surface
# ------------------------------------------------------------------
anim = gm.Animation(surface)

# here `trans_index=1` is for compatible with eye of chrome in linux.
# you may always use the default 0 for chrome and firefox.
anim.pause(100, trans_index=1)

# paint the background region that contains the maze.
left, top, width, height = 66, 47, 475, 297
anim.paint(left, top, width, height, 0)
anim.pause(100)

# ---------------------------------
# run the maze generation algorithm
# ---------------------------------
# only three colors are used in the wilson algorithm animation hence
# the minimal code length can be set to 2.
anim.run(wilson, maze, speed=50, delay=2, mcl=2,
         cmap={0: 0, 1: 1, 2: 2}, trans_index=None, root=(0, 0))

anim.pause(300)

# in the bfs animation we want to color the cells according to their
# distance to the starting cell. the walls, tree and path are colored
# by the 0th, 0th and 2th color respectively, hence the flooded cells
# are colored by colors >=3.
# since full 256 colors are used hence the minimal code length is 8.
cmap = {i: max(i % 256, 3) for i in range(len(maze.cells))}
cmap.update({0: 0, 1: 0, 2: 2})
anim.run(bfs, maze, speed=30, delay=5, mcl=8, cmap=cmap,
         trans_index=0, start=(0, 0), end=(maze.width - 1, maze.height - 1))

# pause 5 seconds to help to see the result clearly.
anim.pause(500)
surface.save('wilson-bfs.gif')
surface.close()
