# -*- coding: utf-8 -*-
"""
This example shows how to use a mask pattern in the maze.
"""
import gifmaze as gm
from algorithms import random_dfs
from gentext import generate_text_mask


width, height = 600, 400
surface = gm.GIFSurface(width, height, bg_color=0)
surface.set_palette([0, 0, 0, 255, 255, 255])

mask = generate_text_mask((width, height), 'UNIX', './resources/ubuntu.ttf', 280)
maze = gm.Maze(147, 97, mask=mask).scale(4).translate((6, 6))

anim = gm.Animation(surface)
anim.pause(200)
anim.run(random_dfs, maze, start=(0, 0), speed=20, delay=5)
anim.pause(500)

surface.save('random_dfs.gif')
surface.close()
