# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make GIF Animation of Prim's Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
