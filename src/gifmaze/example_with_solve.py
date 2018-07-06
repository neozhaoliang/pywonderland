# -*- coding: utf-8 -*-
"""
Generate a maze and solve it.
"""
import gifmaze as gm
from algorithms import kruskal, dfs


width, height = 600, 400
# define the surface to drawn on
surface = gm.GIFSurface(width, height, bg_color=0)
surface.set_palette([0, 0, 0, 255, 255, 255, 255, 0, 255, 150, 200, 100])

# define the maze
maze = gm.Maze(147, 97, mask=None).scale(4).translate((6, 6))

# define the animation environment
anim = gm.Animation(surface)
anim.pause(200)
# run the algorithm
anim.run(kruskal, maze, speed=50, delay=5)
anim.pause(300)

start = (0, 0)
end = (maze.width - 1, maze.height - 1)
# run the maze solving algorithm.
# the tree and walls are unchanged throughout this process
# hence we color them using the transparent channel 0.
anim.run(dfs, maze, speed=20, delay=5, trans_index=0,
         cmap={0: 0, 1: 0, 2: 2, 3: 3}, start=start, end=end)
anim.pause(500)

# save the result
surface.save('kruskal-dfs.gif')
surface.close()
