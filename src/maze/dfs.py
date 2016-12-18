from maze import *
from lzw import *
import random

width = 101
height = 81
speed = 5
maze = Maze(width, height)
start = (margin, margin)
stack = [(start, cell) for cell in maze.get_neighbors(start)]
visited = set([start])
maze.mark_cell(start, intree)

while stack:
    current, child = stack.pop()
    if child in visited:
        continue
    maze.mark_cell(child, intree)
    maze.mark_wall(current, child, intree)
    visited.add(child)

    neighbors = maze.get_neighbors(child)
    random.shuffle(neighbors)
    stack.extend([(child, cell) for cell in neighbors])

    if maze.num_changes >= speed:
        maze.stream += (graphics_control_block(delay=5, trans_index=3)
                        + maze.encode_frame(wall_color=3, tree_color=2))

if maze.num_changes > 0:
    maze.stream += (graphics_control_block(delay=5, trans_index=3)
                    + maze.encode_frame(wall_color=3, tree_color=2))
maze.stream = (pad_delay_frame(delay=100, trans_index=3)
               + maze.stream
               + pad_delay_frame(delay=500, trans_index=3))
maze.stream = maze.encode_frame(wall_color=0, tree_color=1) + maze.stream
maze.write_to_gif('random_dfs.gif')

