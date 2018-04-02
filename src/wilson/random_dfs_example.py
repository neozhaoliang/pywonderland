# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make GIF Animation of Random DFS Algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import gifmaze as gm
from algorithms import random_dfs
from gentext import generate_text_mask


width, height = 600, 400
# define the surface to drawn on
surface = gm.GIFSurface(width, height, bg_color=0)
surface.set_palette([0, 0, 0, 255, 255, 255])

# define the maze
mask = generate_text_mask((width, height), 'UNIX', 'ubuntu.ttf', 280)
maze = gm.Maze(147, 97, mask=mask).scale(4).translate((6, 6))

# define the animation environment
anim = gm.Animation(surface)
anim.pause(200)
# run the algorithm
anim.run(random_dfs, maze, start=(0, 0), speed=20, delay=5)
anim.pause(500)

# save the result
surface.save('random_dfs.gif')
surface.close()
