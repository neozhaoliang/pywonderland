#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make GIF animations of Wilson's uniform spanning tree algorithm
and the depth/breadth-first search algorithm.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage:
      python wilson.py [-width] [-height] [-scale]
                       [-margin] [-bits] [-algo]
                       [-loop] [-filename]
Optional arguments:
    width, height: size of the maze (not the image), should both be odd integers.
    scale: the size of the image will be (width * scale) * (height * scale).
           In other words, each cell in the maze will occupy a square of
           (scale * scale) pixels in the image.
    margin: size of the border of the image.
    bits: number of bits needed to represent all colors.
          Its value determines the number of colors used in the image.
    algo: which maze-solving algorithm to run.
    loop: number of loops of the image, default to 0 (loop infinitely).
    filename: the output file.

Reference for Wilson's algorithm:

    Probability on Trees and Networks, by Russell Lyons and Yuval Peres.

Reference for the GIF89a specification:

    http://giflib.sourceforge.net/whatsinagif/index.html

Copyright (c) 2016 by Zhao Liang.
"""
import argparse
import random
from colorsys import hls_to_rgb
from canvas import Canvas


# four possible states of a cell.
WALL = 0
TREE = 1
PATH = 2
FILL = 3

PALETTE = [0, 0, 0,         # wall color
           200, 200, 200,   # tree color
           255, 0, 255]     # path color

# GIF files allows at most 256 colors in the global color table,
# redundant colors will be discarded when we initializing GIF encoders.
for i in range(256):
    r, g, b = hls_to_rgb((i / 360.0) % 1, 0.5, 1.0)
    PALETTE += [int(round(255*r)), int(round(255*g)), int(round(255*b))]


class WilsonAlgoAnimation(Canvas):
    """
    The main class for making the animation. Basically it contains two parts:
    run the algorithms, and write to the GIF file.
    """

    def __init__(self, width, height, margin, scale,
                 min_bits, palette, loop=0, mask=None):
        """
        width, height: size of the maze, should both be odd numbers.
        margin: size of the border of the maze.

        The maze is represented by a matrix with `height` rows and `width` columns,
        each cell in the maze has 4 possible states:

        0: it's a wall
        1: it's in the tree
        2: it's in the path
        3: it's filled (this will not be used until the depth-first search animation)

        Initially all cells are walls. Adjacent cells in the maze are spaced out by one cell.

        mask: must be None or a white/black image instance of PIL's Image class.
              This mask image must preserve the connectivity of the graph,
              otherwise the program will not terminate.
        """
        Canvas.__init__(self, width, height, scale, min_bits, palette, loop)

        def get_mask_pixel(cell):
            if mask is None:
                return True
            else:
                return mask.getpixel(cell) == 255

        self.cells = []
        for y in range(margin, height - margin, 2):
            for x in range(margin, width - margin, 2):
                if get_mask_pixel((x, y)):
                    self.cells.append((x, y))

        def neighborhood(cell):
            x, y = cell
            neighbors = []
            if x >= 2 + margin and get_mask_pixel((x-2, y)):
                neighbors.append((x-2, y))
            if y >= 2 + margin and get_mask_pixel((x, y-2)):
                neighbors.append((x, y-2))
            if x <= width - 3 - margin and get_mask_pixel((x+2, y)):
                neighbors.append((x+2, y))
            if y <= height - 3 - margin and get_mask_pixel((x, y+2)):
                neighbors.append((x, y+2))
            return neighbors

        self.graph = {v: neighborhood(v) for v in self.cells}
        # we will look for a path between this start and end.
        self.start = (margin, margin)
        self.end = (width - margin - 1, height - margin - 1)
        self.path = []  # a list holds the path in the loop erased random walk.
        # map distance to color indices.
        self.dist_to_color = lambda d: max(d % (1 << min_bits), 3)

    def get_neighbors(self, cell):
        return self.graph[cell]

    def mark_wall(self, cell_a, cell_b, index):
        """Mark the space between two adjacent cells."""
        wall = ((cell_a[0] + cell_b[0]) // 2,
                (cell_a[1] + cell_b[1]) // 2)
        self.mark_cell(wall, index)

    def is_wall(self, cell):
        """Check if a cell is wall."""
        x, y = cell
        return self.grid[x][y] == WALL

    def connected(self, cell_a, cell_b):
        """Check if two adjacent cells are connected."""
        x = (cell_a[0] + cell_b[0]) // 2
        y = (cell_a[1] + cell_b[1]) // 2
        return self.grid[x][y] == WALL

    def in_tree(self, cell):
        """Check if a cell is in the tree."""
        x, y = cell
        return self.grid[x][y] == TREE

    def in_path(self, cell):
        """Check if a cell is in the path."""
        x, y = cell
        return self.grid[x][y] == PATH

    def mark_path(self, path, index):
        """Mark the cells in a path and the spaces between them."""
        for cell in path:
            self.mark_cell(cell, index)
        for cell_a, cell_b in zip(path[1:], path[:-1]):
            self.mark_wall(cell_a, cell_b, index)

    def run_wilson_algorithm(self, speed, delay, trans_index, **kwargs):
        """Animating Wilson's uniform spanning tree algorithm."""
        self.speed = speed
        self.delay = delay
        self.trans_index = trans_index
        self.set_colors(**kwargs)

        # initially the tree only contains the root.
        self.mark_cell(self.start, TREE)

        # for each cell that is not in the tree,
        # start a loop erased random walk from this cell until the walk hits the tree.
        for cell in self.cells:
            if not self.in_tree(cell):
                self.loop_erased_random_walk(cell)

        # possibly there are some changes that have not been written to the file.
        self.clear_remaining_changes()

    def loop_erased_random_walk(self, cell):
        """Start a loop erased random walk from a given cell until it hits the tree."""
        self.path = [cell]
        self.mark_cell(cell, PATH)
        current_cell = cell

        while not self.in_tree(current_cell):
            current_cell = self.move_one_step(current_cell)
            self.refresh_frame()

        # once the walk meets the tree, add the path to the tree.
        self.mark_path(self.path, TREE)

    def move_one_step(self, cell):
        """The most fundamental step in Wilson's algorithm:
        1. choose a random neighbor z of current cell and move to z.
        2. (a) if z is already in current path then a loop is found, erase this loop
               and continue the walk from z.
           (b) if z is already in the tree then finish this walk.
           (c) if z is neither in the path nor in the tree then append it to the path
               and continue the walk from z.
        """
        next_cell = random.choice(self.get_neighbors(cell))
        if self.in_path(next_cell):
            self.erase_loop(next_cell)
        elif self.in_tree(next_cell):
            self.add_to_path(next_cell)
            # `add_to_path` will change the cell to `PATH` so we need to reset it.
            self.mark_cell(next_cell, TREE)
        else:
            self.add_to_path(next_cell)
        return next_cell

    def erase_loop(self, cell):
        """When `cell` is visited twice a loop is found. Erase this loop.
        Do not forget the space between path[index] and path[index+1]."""
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

    def run_dfs_algorithm(self, speed, delay, trans_index, **kwargs):
        """Animating the depth-first search algorithm."""
        self.speed = speed
        self.delay = delay
        self.trans_index = trans_index
        self.set_colors(**kwargs)

        from_to = dict()  # a dict to remember each step.
        stack = [(self.start, self.start)]
        self.mark_cell(self.start, FILL)
        visited = set([self.start])

        while len(stack) > 0:
            parent, child = stack.pop()
            from_to[child] = parent
            self.mark_cell(child, FILL)
            self.mark_wall(parent, child, FILL)
            for next_cell in self.get_neighbors(child):
                if (next_cell not in visited) and (not self.connected(child, next_cell)):
                    stack.append((child, next_cell))
                    visited.add(next_cell)

            self.refresh_frame()
        self.clear_remaining_changes()

        # retrieve the path
        path = [self.end]
        parent = self.end
        while parent != self.start:
            parent = from_to[parent]
            path.append(parent)
        self.mark_path(path, PATH)
        # show the path
        self.clear_remaining_changes()

    def run_bfs_algorithm(self, speed, delay, trans_index, **kwargs):
        """Animating the breadth-first search algorithm with colors.
        The maze is colored according to their distance with the start."""
        from collections import deque

        self.speed = speed
        self.delay = delay
        self.trans_index = trans_index
        self.set_colors(**kwargs)

        dist = 0
        from_to = dict()  # a dict to remember each step.
        queue = deque([(self.start, self.start, dist)])
        self.mark_cell(self.start, self.dist_to_color(dist))
        visited = set([self.start])

        while len(queue) > 0:
            parent, child, dist = queue.popleft()
            from_to[child] = parent
            self.mark_cell(child, self.dist_to_color(dist))
            self.mark_wall(parent, child, self.dist_to_color(dist))

            for next_cell in self.get_neighbors(child):
                if (next_cell not in visited) and (not self.connected(child, next_cell)):
                    queue.append((child, next_cell, dist + 1))
                    visited.add(next_cell)

            self.refresh_frame()
        self.clear_remaining_changes()

        # retrieve the path
        path = [self.end]
        parent = self.end
        while parent != self.start:
            parent = from_to[parent]
            path.append(parent)
        self.mark_path(path, PATH)
        # show the path
        self.clear_remaining_changes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-width', type=int, default=121,
                        help='width of the maze')
    parser.add_argument('-height', type=int, default=97,
                        help='height of the maze')
    parser.add_argument('-margin', type=int, default=2,
                        help='border of the maze')
    parser.add_argument('-scale', type=int, default=5,
                        help='size of a cell in pixels')
    parser.add_argument('-loop', type=int, default=0,
                        help='number of loops of the animation, default to 0 (loop infinitely)')
    parser.add_argument('-bits', metavar='b', type=int, default=8,
                        help='an interger beteween 2-8 represents the minimal number of bits needed to\
                        represent the colors, this parameter determines the size of the global color table.')
    parser.add_argument('-algo', metavar='a', type=str, default='bfs',
                        help='choose which maze-solving algorithm to run.')
    parser.add_argument('-filename', type=str, default='wilson.gif',
                        help='output file name')

    args = parser.parse_args()

    if (args.width * args.height % 2 == 0):
        raise ValueError('The width and height of the maze must both be odd integers!')

    # comment out the following two lines if you don't want to show text.
    from gentext import generate_text_mask
    mask = generate_text_mask(args.width, args.height, 'UST', 'ubuntu.ttf', 60)

    anim = WilsonAlgoAnimation(args.width, args.height, args.margin, args.scale,
                               args.bits, PALETTE, args.loop, mask=mask)

    # here we need to paint the blank background because the region that has not been
    # covered by any frame will be set to transparent by decoders.
    # comment this line and watch the result if you don't understand this.
    anim.paint_background(wc=0)

    # pad one second delay, get ready!
    anim.pad_delay_frame(100)

    # in the Wilson's algorithm animation no cells are filled,
    # hence it's safe to use color 3 as the transparent color.
    anim.run_wilson_algorithm(speed=50, delay=2, trans_index=3,
                              wc=0, tc=1, pc=2)

    # pad three seconds delay to help to see the resulting maze clearly.
    anim.pad_delay_frame(300)

    # in the dfs/bfs algorithm animation the walls are unchanged throughout,
    # hence it's safe to use color 0 as the transparent color.
    if args.algo == 'bfs':
        anim.run_bfs_algorithm(speed=50, delay=5, trans_index=0,
                               wc=0, tc=0, pc=2, fc=3)

    elif args.algo == 'dfs':
        anim.run_dfs_algorithm(speed=10, delay=5, trans_index=0,
                               wc=0, tc=0, pc=2, fc=3)

    # more elif for algorithms implemented by the user ...
    else:
        pass

    # pad five seconds delay to help to see the resulting path clearly.
    anim.pad_delay_frame(500)

    # finally save the bytestream in 'wb' mode.
    anim.write_to_gif(args.filename)


if __name__ == '__main__':
    main()
