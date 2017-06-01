# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make GIF Animations of Wilson's Uniform Spanning Tree Algorithm
and the Depth-First Search Algorithm.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage: python wilson.py [-width] [-height] [-scale]
                        [-marign] [-loop] [-filename]

Optional arguments:
    width, height: size of the maze (not the image), should both be odd.
    scale: the size of the image will be (width * scale) * (height * scale).
           In other words, each cell in the maze will occupy (scale * scale)
           pixels in the image.
    margin: size of the border of the image.
    loop: number of loops of the image, default to 0 (loop infinitely).
    filename: the output file.

:copyright (c) 2016 by Zhao Liang.
"""
import time
import os
import argparse
import random
from encoder import GIFWriter

# four possible states of a cell.
WALL = 0
TREE = 1
PATH = 2
FILL = 3

# a dict for mapping cells to colors.
CELL_TO_COLOR = {'wall_color': 0, 'tree_color': 1,
                 'path_color': 2, 'fill_color': 3}


class BaseMaze(object):
    """This class defines the structure of a maze and
    some methods we will need for running algorithms on it."""

    def __init__(self, width, height, margin):
        """
        width, height: size of the maze, should both be odd numbers.
        margin: size of the border of the maze.

        The maze is represented by a matrix with `height` rows and `width` columns,
        each cell in the maze has 4 possible states:

        0: it's a wall
        1: it's in the tree
        2: it's in the path
        3: it's filled (this will not be used until the depth-first search animation)

        Initially all cells are walls.
        Adjacent cells in the maze are spaced out by one cell.

        frame_box: maintains the region that to be updated.
        num_changes: output the frame once this number of cells are changed.
        """
        self.width = width
        self.height = height
        self.grid = [[0]*height for _ in range(width)]
        self.num_changes = 0
        self.frame_box = None

        # shrink the maze a little to pad some margin at the border of the window.
        self.cells = []
        for y in range(margin, height - margin, 2):
            for x in range(margin, width - margin, 2):
                self.cells.append((x, y))

        def neighborhood(cell):
            x, y = cell
            neighbors = []
            if x >= 2 + margin:
                neighbors.append((x-2, y))
            if y >= 2 + margin:
                neighbors.append((x, y-2))
            if x <= width - 3 - margin:
                neighbors.append((x+2, y))
            if y <= height - 3 - margin:
                neighbors.append((x, y+2))
            return neighbors

        self.graph = {v: neighborhood(v) for v in self.cells}

        # we will look for a path between this start and end.
        self.start = (margin, margin)
        self.end = (width - margin - 1, height - margin -1)

    def get_neighbors(self, cell):
        return self.graph[cell]

    def mark_cell(self, cell, index):
        """Mark a cell and update `frame_box` and `num_changes`."""
        x, y = cell
        self.grid[x][y] = index

        self.num_changes += 1

        if self.frame_box:
            left, top, right, bottom = self.frame_box
            self.frame_box = (min(x, left), min(y, top),
                              max(x, right), max(y, bottom))
        else:
            self.frame_box = (x, y, x, y)

    def mark_wall(self, cellA, cellB, index):
        """Mark the space between two adjacent cells."""
        wall = ((cellA[0] + cellB[0])//2,
                (cellA[1] + cellB[1])//2)
        self.mark_cell(wall, index)

    def check_wall(self, cellA, cellB):
        """Check if two adjacent cells are connected."""
        x = (cellA[0] + cellB[0]) // 2
        y = (cellA[1] + cellB[1]) // 2
        return self.grid[x][y] == WALL

    def mark_path(self, path, index):
        """Mark the cells in a path and the spaces between them."""
        for cell in path:
            self.mark_cell(cell, index)
        for cellA, cellB in zip(path[1:], path[:-1]):
            self.mark_wall(cellA, cellB, index)


class WilsonAlgoAnimation(BaseMaze):
    """Our animation contains two parts: run the algorithms and write to the file.
    """

    def __init__(self, width, height, margin, scale, loop):
        """
        scale: a cell in the maze will occupy (scale * scale) pixels in the image.
        loop: number of loops of the GIF image, 0 means loop infinitely.
        speed: control how often a frame is rendered.
        trans_index: index of the transparent color in the global color table.
        delay: delay between two successive frames.
        colormap: a dict that maps the maze to an image.
        """
        BaseMaze.__init__(self, width, height, margin)
        self.scale = scale
        self.speed = 30
        self.delay = 2
        self.trans_index = 3
        self.colormap = {i: i for i in range(4)}
        self.writer = GIFWriter(width * scale, height * scale, loop)

    def run_wilson_algorithm(self, speed, delay, trans_index, **kwargs):
        """Animating Wilson's uniform spanning tree algorithm."""
        self.speed = speed
        self.delay = delay
        self.trans_index = trans_index
        self.set_colors(**kwargs)

        # initially the tree only contains the root.
        self.mark_cell(self.start, TREE)
        self.tree = set([self.start])

        # for each cell that is not in the tree,
        # start a loop erased random walk from this cell until the walk hits the tree.
        for cell in self.cells:
            if cell not in self.tree:
                self.loop_erased_random_walk(cell)

        self.clear_remaining_changes()

    def loop_erased_random_walk(self, cell):
        """Start a loop erased random walk from a
        given cell until it hits the tree."""
        self.path = [cell]
        self.mark_cell(cell, PATH)
        current_cell = cell

        while current_cell not in self.tree:
            current_cell = self.move_one_step(current_cell)
            self.refresh_frame()

        # once the walk meets the tree, add the path to the tree.
        self.mark_path(self.path, TREE)
        self.tree = self.tree.union(self.path)

    def move_one_step(self, cell):
        """The most fundamental step in Wilson's algorithm:
        1. choose a random neighbor z of current cell and move to z.
        2. (i) if z is already in current path then a loop is found, erase this loop
           and continue the walk from z.
           (ii) if z is not in current path then append it to current path.
           in both cases current cell is updated to be z.
        3. repeat this procedure until z 'hits' the tree.
        """
        next_cell = random.choice(self.get_neighbors(cell))
        if next_cell in self.path:
            self.erase_loop(next_cell)
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

    def run_dfs_algorithm(self, speed, delay, trans_index, **kwargs):
        """Animating the depth-first search algorithm."""
        self.speed = speed
        self.delay = delay
        self.trans_index = trans_index
        self.set_colors(**kwargs)

        # we use a dict to remember each step.
        from_to = dict()
        stack = [(self.start, self.start)]
        visited = set([self.start])

        while stack:
            parent, child = stack.pop()
            from_to[parent] = child
            self.mark_cell(child, FILL)
            self.mark_wall(parent, child, FILL)

            if child == self.end:
                break
            else:
                for next_cell in self.get_neighbors(child):
                    if (next_cell not in visited) and (not self.check_wall(child, next_cell)):
                        stack.append((child, next_cell))
                        visited.add(next_cell)

            self.refresh_frame()
        self.clear_remaining_changes()

        # retrieve the path
        path = [self.start]
        tmp = self.start
        while tmp != self.end:
            tmp = from_to[tmp]
            path.append(tmp)

        self.mark_path(path, PATH)
        # show the path
        self.refresh_frame()

    def set_colors(self, **kwargs):
        for key, val in kwargs.items():
            self.colormap[CELL_TO_COLOR[key]] = val

    def pad_delay_frame(self, delay):
        self.writer.data += self.writer.pad_delay_frame(delay, self.trans_index)

    def encode_frame(self):
        """Encode current maze into a frame but not write to the file.
        Note the graphics control block is not added here."""
        if self.frame_box:
            left, top, right, bottom = self.frame_box
        else:
            left, top, right, bottom = 0, 0, self.width - 1, self.height - 1

        width = right - left + 1
        height = bottom - top + 1
        descriptor = self.writer.image_descriptor(left * self.scale, top * self.scale,
                                                  width * self.scale, height * self.scale)

        # flatten the pixels of the region into a 1D list.
        input_data = [0] * width * height * self.scale * self.scale
        for i in range(len(input_data)):
            y = i // (width * self.scale * self.scale)
            x = (i % (width * self.scale)) // self.scale
            value = self.grid[x + left][y + top]
            # map the value of the cell to the color index.
            input_data[i] = self.colormap[value]

        # and don't forget to reset `frame_box` and `num_changes`.
        self.num_changes = 0
        self.frame_box = None
        return descriptor + self.writer.LZW_encode(input_data)

    def paint_background(self, **kwargs):
        """Insert current frame at the beginning to use it as the background.
        This does not require the graphics control block."""
        if kwargs:
            self.set_colors(**kwargs)
        self.writer.data = self.encode_frame() + self.writer.data

    def output_current_frame(self):
        """Output current frame to the data stream. Note the graphics control
        block here. This method will not be directly called: it's called by
        `refresh_frame()` and `clear_remaining_changes()`."""
        control = self.writer.graphics_control_block(self.delay, self.trans_index)
        self.writer.data += control + self.encode_frame()

    def refresh_frame(self):
        if self.num_changes >= self.speed:
            self.output_current_frame()

    def clear_remaining_changes(self):
        if self.num_changes > 0:
            self.output_current_frame()

    def write_to_gif(self, filename):
        self.writer.save(filename)


def main():
    start = time.time()
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
    parser.add_argument('-filename', type=str, default='wilson.gif',
                        help='output file name')

    args = parser.parse_args()
    anim = WilsonAlgoAnimation(args.width, args.height, args.margin,
                               args.scale, args.loop)

    # here we need to paint the blank background because the region that has not been
    # covered by any frame will be set to transparent by decoders.
    # comment this line and watch the result if you don't understand this.
    anim.paint_background()

    # pad one second delay, get ready!
    anim.pad_delay_frame(100)

    # in the wilson algorithm step no cells are 'filled',
    # hence it's safe to use color 3 as the transparent color.
    anim.run_wilson_algorithm(speed=30, delay=2, trans_index=3,
                              wall_color=0, tree_color=1, path_color=2)

    # pad three seconds delay to help to see the resulting maze clearly.
    anim.pad_delay_frame(300)

    # in the dfs algorithm step the walls are unchanged throughout,
    # hence it's safe to use color 0 as the transparent color.
    anim.run_dfs_algorithm(speed=10, delay=5, trans_index=0, wall_color=0,
                           tree_color=0, path_color=2, fill_color=3)

    # pad five seconds delay to help to see the resulting path clearly.
    anim.pad_delay_frame(500)

    # finally save the bytestream in 'wb' mode.
    anim.write_to_gif(args.filename)
    runtime = (time.time() - start) / 60.0
    fsize = os.path.getsize(args.filename) / 1024.0
    print('runtime: {:.1f} minutes, size: {:.1f} kb, bitrate: {:.2f} kb/min'.format(runtime, fsize, fsize/runtime))

if __name__ == '__main__':
    main()
