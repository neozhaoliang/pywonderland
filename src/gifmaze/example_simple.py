# -*- coding: utf-8 -*-
"""
This example shows the basic usage of this program.

To make a gif animation you need to:

1. declare a surface object to drawn on (set the image size,
   global color table, background color).

2. declare a maze object to run the algorithms (set the size
   of the maze, its position in the image, the mask pattern).

3. declare an animation object to render the animation (set the
   color map, delay between frames, speed, transparent channel).
"""
import gifmaze as gm
from algorithms import prim


width, height = 600, 400
# define the surface to drawn on
surface = gm.GIFSurface(width, height, bg_color=0)
surface.set_palette([0, 0, 0, 255, 255, 255])

# define the maze
maze = gm.Maze(147, 97, mask=None).scale(4).translate((6, 6))

# define the animation environment
anim = gm.Animation(surface)
anim.pause(200)
# run the algorithm
anim.run(prim, maze, speed=30, delay=5)
anim.pause(500)

# save the result
surface.save('prim.gif')
surface.close()
