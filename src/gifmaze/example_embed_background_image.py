# -*- coding: utf-8 -*-
"""
This example shows how to embed the animation into a background image.
"""
from colorsys import hls_to_rgb
import gifmaze as gm
from gentext import generate_text_mask
from algorithms import wilson, bfs


# create a GIFSurface instance and set the colors
surface = gm.GIFSurface.from_image('./resources/bg.png')
palette = [38, 92, 66,     # wall color, the same with the blackboard's
           200, 200, 200,  # tree color
           244, 25, 220]   # path color

for i in range(256):
    rgb = hls_to_rgb((i / 360.0) % 1, 0.5, 1.0)
    palette += [int(round(255 * x)) for x in rgb]

surface.set_palette(palette)

# create a maze instance and set its position in the image
size = (surface.width, surface.height)
mask = generate_text_mask(size, 'UST', './resources/ubuntu.ttf', 300)
maze = gm.Maze(119, 75, mask=mask).scale(3).translate((50, 35))

# create an animation environment
anim = gm.Animation(surface)

# here `trans_index=1` is for compatible with eye of gnome in linux,
# you may always use the default 0 for chrome and firefox.
anim.pause(100, trans_index=1)

# paint the background region that contains the maze
left, top, width, height = 48, 32, 361, 231
anim.paint(left, top, width, height, 0)
anim.pause(100)

# Run the maze generation algorithm.
# Only three colors are used in the Wilson's algorithm hence
# the minimal code length can be set to 2.
anim.run(wilson, maze, speed=50, delay=2, mcl=2,
         cmap={0: 0, 1: 1, 2: 2}, trans_index=None, root=(0, 0))
anim.pause(300)

# In the bfs animation we want to color the cells according to their distance
# to the starting cell. The wall, tree and path are colored by the 0th, 1th
# and 2th color respectively, the flooded cells are colored by colors >=3.
# Note since full 256 colors are used the minimal code length must be >=8.
cmap = {i: max(i % 256, 3) for i in range(len(maze.cells))}
# In the maze solving animation the wall and tree are unchanged throughout,
# so we use transparent color for them.
cmap.update({0: 0, 1: 0, 2: 2})
anim.run(bfs, maze, speed=30, delay=5, mcl=8, cmap=cmap,
         trans_index=0, start=(0, 0), end=(maze.width - 1, maze.height - 1))

# pause 5 seconds to help to see the result clearly
anim.pause(500)
surface.save('wilson_bfs.gif')
surface.close()
