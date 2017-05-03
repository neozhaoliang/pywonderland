import argparse
import random
from maze import *



class WilsonMaze(Maze):
    '''
    If you want to implement your own maze generating algorithms,
    simply inherit the 'Maze' class in maze.py and add attributes
    and methods you need.
    '''

    def __init__(self, width, height, margin):
        Maze.__init__(self, width, height, margin)
        # hold the path in the loop erased random walk.
        self.path = []
        # hold the cells that are already in the tree
        self.set = {}


    def move_one_step(self, cell):
        '''
        The most fundamental operation in wilson algorithm:
        choose a random neighbor z of current cell, and move to z.
        1. if z already in current path, then a loop is found, erase this loop
           and continue the walk from z again.
        2. if z is not in current path, then add z to current path.
           repeat this procedure until z 'hits' the tree.
        '''
        next_cell = random.choice(self.get_neighbors(cell))

        # if next_cell is already in path, then we have found a loop in our path, erase it!
        if next_cell in self.path:
            self.erase_loop(next_cell)

        # else add this cell to the path, so we need to implement two
        # more functions that 'erase loops' and 'add to path'.
        else:
            self.add_to_path(next_cell)

        return next_cell


    def erase_loop(self, cell):
        index = self.path.index(cell)

        # erase the loop
        self.mark_path(self.path[index:], WALL)

        # re-mark this cell
        self.mark_cell(self.path[index], PATH)

        self.path = self.path[:index+1]


    def add_to_path(self, cell):
        self.mark_cell(cell, PATH)
        self.mark_wall(self.path[-1], cell, PATH)
        self.path.append(cell)



def Wilson_and_DFS(width, height, margin, loop, scale, speed):
    maze = WilsonMaze(width, height, margin)
    canvas = Animation(maze, scale, speed, loop)

    # here we need to paint the blank background because the region that has not been
    # covered by any frame will be set to transparent by decoders.
    # comment this line and watch the result if you don't understand this.
    canvas.paint_background()

    # pad one second delay, get ready!
    canvas.pad_delay_frame(100)

    canvas.set_delay(2)
    canvas.set_transparent(3)
    canvas.set_colors(wall_color=0, tree_color=1, path_color=2)

    # initially the tree only contains the root (i.e. the starting cell)
    maze.tree = set([maze.start])
    maze.mark_cell(maze.start, TREE)

    for cell in maze.cells:
        if cell not in maze.tree:
            # once this cell is not in the tree,
            # then start a loop erased random walk from this cell.
            maze.path = [cell]
            maze.mark_cell(cell, PATH)
            current_cell = cell

            while current_cell not in maze.tree:
                current_cell = maze.move_one_step(current_cell)
                canvas.refresh_frame()

            # add the path to the tree.
            maze.mark_path(maze.path, TREE)
            maze.tree = maze.tree.union(maze.path)

    canvas.clear()

    # The wilson algorithm part is finished, pad three seconds delay to
    # help to see the resulting maze clearly.
    canvas.pad_delay_frame(300)

    # now let's go on to make the dfs animation.
    # in the dfs algorithm step the walls are unchanged throughout,
    # hence it's safe to use color 0 as the transparent color.
    canvas.set_delay(5)
    canvas.set_transparent(0)
    canvas.set_colors(wall_color=0, tree_color=0, path_color=2, fill_color=3)
    canvas.set_speed(10)


    # besides a stack to run the dfs, we need a dict to remember each step.
    from_to = dict()
    stack = [(maze.start, maze.start)]
    visited = set([maze.start])

    while stack:
        parent, child = stack.pop()
        from_to[parent] = child
        maze.mark_cell(child, FILL)
        maze.mark_wall(parent, child, FILL)

        if child == maze.end:
            break
        else:
            for next_cell in maze.get_neighbors(child):
                if (next_cell not in visited) and (not maze.check_wall(child, next_cell)):
                    stack.append((child, next_cell))
                    visited.add(next_cell)

        canvas.refresh_frame()
    canvas.clear()

    # retrieve the path
    path = [maze.start]
    tmp = maze.start
    while tmp != maze.end:
        tmp = from_to[tmp]
        path.append(tmp)

    maze.mark_path(path, PATH)
    # show the path
    canvas.refresh_frame()

    # pad a five-seconds delay to help to see the resulting path clearly.
    canvas.pad_delay_frame(500)

    # finally save the bits stream in 'wb' mode.q
    canvas.write_to_gif('wilson_and_dfs.gif')


Wilson_and_DFS(width=101, height=81, margin=2,
               loop=0, scale=5, speed=30)
