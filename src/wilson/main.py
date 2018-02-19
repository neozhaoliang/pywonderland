# -*- coding: utf-8 -*-

from colorsys import hls_to_rgb
import gifmaze as gm
from gentext import generate_text_mask
from algorithms import wilson, bfs


surface = gm.GIFSurface.from_image('teacher.png')

# set the 0-th color to be the same with the blackboard's.
palette = [52, 51, 50, 200, 200, 200, 255, 0, 255]
for i in range(256):
    rgb = hls_to_rgb((i / 360.0) % 1, 0.5, 1.0)
    palette += [int(round(255 * x)) for x in rgb]

surface.set_palette(palette)
anim = gm.Animation(surface)

size = (surface.width, surface.height)
mask = generate_text_mask(size, 'UST', 'ubuntu.ttf', 350)

# define the region that to put the maze into.
left, top, width, height = 66, 47, 475, 297
maze = gm.Maze(117, 73, mask=mask).scale(4).translate((69, 49))

# here `trans_index=1` is for compatible with eye of chrome under linux.
# you may always use the default 0 for chrome and firefox.
anim.pause(100, trans_index=1)
anim.paint(left, top, width, height, 0)
anim.pause(100)

# run the maze generation algorithm.
# only three colors are used in this animation hence the minimal
# code length can be set to 2.
anim.run(wilson, maze, speed=50, delay=2, mcl=2,
         cmap={0: 0, 1: 1, 2: 2}, trans_index=None, root=(0, 0))

anim.pause(300)

# in the bfs animation we want to color the cells according to their
# distance to the starting cell. the walls, tree and path are colored
# by the 0th, 0th and 2th color respectively, hence the flooded cells
# are colored by colors >=3.
cmap = {i: max(i % 256, 3) for i in range(len(maze.cells))}
cmap.update({0: 0, 1: 0, 2: 2})

# run the maze solving algorithm.
# the full 256 colors are used hence the minimal code length is 8.
anim.run(bfs, maze, speed=30, delay=5, mcl=8, cmap=cmap,
         trans_index=0, start=(0, 0), end=(maze.width - 1, maze.height - 1))

anim.pause(500)

surface.save('wilson-bfs.gif')
surface.close()
