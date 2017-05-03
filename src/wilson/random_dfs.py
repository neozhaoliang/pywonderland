import random
from maze import *



def random_dfs(width, height, margin, scale, speed, loop):
    maze = Maze(width, height, margin)
    canvas = Animation(maze, scale, speed, loop)

    canvas.set_delay(5)
    canvas.set_transparent(3)

    # note here the walls are colored with the transparent color!
    # this is because we inserted the resulting maze as background at the beginning
    # so the walls of the maze will show through.
    canvas.set_colors(wall_color=3, tree_color=2)
    canvas.pad_delay_frame(200)

    stack = [(maze.start, v) for v in maze.get_neighbors(maze.start)]
    maze.mark_cell(maze.start, TREE)

    while stack:
        parent, child = stack.pop()
        if maze.check_tree(child):
            continue
        maze.mark_cell(child, TREE)
        maze.mark_wall(parent, child, TREE)

        neighbors = maze.get_neighbors(child)
        random.shuffle(neighbors)
        for v in neighbors:
            stack.append((child, v))
        canvas.refresh_frame()

    canvas.clear()
    canvas.pad_delay_frame(300)
    canvas.paint_background(wall_color=0, tree_color=1)
    canvas.write_to_gif('random_dfs.gif')


random_dfs(width=101, height=81, margin=2,
           scale=5, speed=10, loop=0)
