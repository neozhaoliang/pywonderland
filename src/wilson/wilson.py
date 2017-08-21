#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make GIF animations of Wilson's uniform spanning tree algorithm
and the depth-first search algorithm.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Usage: python wilson.py [-width] [-height] [-scale]
                        [-margin] [-loop] [-filename]

Optional arguments:
    width, height: size of the maze (not the image), should both be odd integers.
    scale: the size of the image will be (width * scale) * (height * scale).
           In other words, each cell in the maze will occupy a square of
           (scale * scale) pixels in the image.
    margin: size of the border of the image.
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
from struct import pack


# constants for LZW encoding.
PALETTE_BITS = 2
CLEAR_CODE = 2**PALETTE_BITS
END_CODE = CLEAR_CODE + 1
MAX_CODES = 4096

BYTE = 1  # the packed byte in the logical screen descriptor.
BYTE = BYTE << 3 | (PALETTE_BITS - 1)  # color resolution.
BYTE = BYTE << 1 | 0                   # sorted flag.
BYTE = BYTE << 3 | (PALETTE_BITS - 1)  # size of the global color table.

# four possible states of a cell.
WALL = 0
TREE = 1
PATH = 2
FILL = 3


class DataBlock(object):
    """Write bits into a bytearray and then pack this bytearray into data blocks.
    This class is used in the LZW algorithm when encoding maze into frames."""

    def __init__(self):
        self._bitstream = bytearray()  # write bits into this array.
        self._nbits = 0  # a counter holds how many bits have been written.

    def encode_bits(self, num, size):
        """Given a number `num`, encode it as a binary string of length `size`,
        and pack it at the end of bitstream.
        Example: num = 3, size = 5. The binary string for 3 is '00011',
        here we padded extra zeros at the left to make its length to be 5.
        The tricky part is that in a gif file, the encoded binary data stream
        increase from lower (least significant) bits to higher
        (most significant) bits, so we have to reverse it as '11000' and pack
        this string at the end of bitstream!
        """
        string = bin(num)[2:].zfill(size)
        for digit in reversed(string):
            if len(self._bitstream) * 8 == self._nbits:
                self._bitstream.append(0)
            if digit == '1':
                self._bitstream[-1] |= 1 << self._nbits % 8
            self._nbits += 1

    def dump_bytes(self):
        """Pack the LZW encoded image data into blocks.
        Each block is of length <= 255 and is preceded by a byte
        in 0-255 that indicates the length of this block.
        """
        bytestream = bytearray()
        while len(self._bitstream) > 255:
            bytestream += bytearray([255]) + self._bitstream[:255]
            self._bitstream = self._bitstream[255:]
        if len(self._bitstream) > 0:
            bytestream += bytearray([len(self._bitstream)]) + self._bitstream
        return bytestream


class GIFWriter(object):
    """
    Structure of a GIF file: (in the order they appear)
    1. always begins with the logical screen descriptor.
    2. then follows the global color table.
    3. then follows the loop control block (specify the number of loops)
    4. then follows the image data of the frames, each frame is further divided into:
       (i) a graphics control block that specify the delay and transparent color of this frame.
       (ii) the image descriptor.
       (iii) the LZW enconded data.
    5. finally the trailor '0x3B'.
    """

    def __init__(self, width, height, loop):
        """Attributes are listed in the order they appear in the GIF file."""
        self.logical_screen_descriptor = pack('<6s2H3B', b'GIF89a', width, height, BYTE, 0, 0)
        self.global_color_table = bytearray([0, 0, 0,         # wall color
                                             100, 100, 100,   # tree color
                                             255, 0, 255,     # path color
                                             150, 200, 100])  # fill color
        self.loop_control = pack('<3B8s3s2BHB', 0x21, 0xFF, 11, b'NETSCAPE', b'2.0', 3, 1, loop, 0)
        self.data = bytearray()
        self.trailor = bytearray([0x3B])

    @staticmethod
    def graphics_control_block(delay, trans_index):
        """This block specifies the delay and transparent color of a frame."""
        return pack("<4BH2B", 0x21, 0xF9, 4, 0b00000101, delay, trans_index, 0)

    @staticmethod
    def image_descriptor(left, top, width, height):
        """This block specifies the position of a frame (relative to the window).
        The ending packed byte field is 0 since we do not need a local color table."""
        return pack('<B4HB', 0x2C, left, top, width, height, 0)

    @staticmethod
    def pad_delay_frame(delay, trans_index):
        """Pad a 1x1 pixel frame for delay. The image data could be written as
        `bytearray([PALETTE_BITS, 1, trans_index, 0])`, this works fine for decoders
        like firefox and chrome but fails for some decoders like eye of gnome
        when `PALETTE_BITS` is 7 or 8. Using the LZW encoding is a bit tedious but it's
        safe for all possible values of `PALETTE_BITS` (1-8) and all decoders.
        """
        control = GIFWriter.graphics_control_block(delay, trans_index)
        descriptor = GIFWriter.image_descriptor(0, 0, 1, 1)
        stream = DataBlock()
        code_length = PALETTE_BITS + 1
        stream.encode_bits(CLEAR_CODE, code_length)
        stream.encode_bits(trans_index, code_length)
        stream.encode_bits(END_CODE, code_length)
        data = bytearray([PALETTE_BITS]) + stream.dump_bytes() + bytearray([0])
        return control + descriptor + data

    def save_gif(self, filename):
        """Note the 'wb' mode here!"""
        with open(filename, 'wb') as f:
            f.write(self.logical_screen_descriptor +
                    self.global_color_table +
                    self.loop_control +
                    self.data +
                    self.trailor)


class WilsonAlgoAnimation(object):
    """The main class for making the animation. Basically it contains two parts:
    run the algorithms, and write to the GIF file."""

    def __init__(self, width, height, margin, scale, loop):
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
        """
        self.width = width
        self.height = height
        self.grid = [[0]*height for _ in range(width)]
        self.num_changes = 0   # a counter holds how many cells are changed.
        self.frame_box = None  # maintains the region that to be updated.

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
        self.end = (width - margin - 1, height - margin - 1)
        self.path = []  # a list holds the path in the loop erased random walk.

        self.scale = scale     # each cell will occupy (scale * scale) pixels in the GIF image.
        self.speed = 10        # output the frame once this number of cells are changed.
        self.trans_index = 3   # the index of the transparent color in the global color table.
        self.delay = 5         # delay between successive frames.

        # a dict that maps the state of the cells to the colors.
        # the keys are the states of the cells and the values are the index of the colors.
        self.colormap = {i: i for i in range(2**PALETTE_BITS)}
        self.writer = GIFWriter(width * scale, height * scale, loop)  # size of the image is scaled.

    def get_neighbors(self, cell):
        return self.graph[cell]

    def mark_cell(self, cell, index):
        """Mark a cell and update `frame_box` and `num_changes`."""
        x, y = cell
        self.grid[x][y] = index

        self.num_changes += 1

        if self.frame_box is not None:
            left, top, right, bottom = self.frame_box
            self.frame_box = (min(x, left), min(y, top),
                              max(x, right), max(y, bottom))
        else:
            self.frame_box = (x, y, x, y)

    def mark_wall(self, cell_a, cell_b, index):
        """Mark the space between two adjacent cells."""
        wall = ((cell_a[0] + cell_b[0]) // 2,
                (cell_a[1] + cell_b[1]) // 2)
        self.mark_cell(wall, index)

    def barrier(self, cell_a, cell_b):
        """Check if two adjacent cells are connected."""
        x = (cell_a[0] + cell_b[0]) // 2
        y = (cell_a[1] + cell_b[1]) // 2
        return self.grid[x][y] == WALL

    def is_wall(self, cell):
        """Check if a cell is wall."""
        x, y = cell
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
            if child == self.end:
                break
            else:
                for next_cell in self.get_neighbors(child):
                    if (next_cell not in visited) and (not self.barrier(child, next_cell)):
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

    def encode_frame(self):
        """Use LZW algorithm to encode the region bounded by `frame_box`
        into one frame of the image."""
        if self.frame_box is not None:
            left, top, right, bottom = self.frame_box
        else:
            left, top, right, bottom = 0, 0, self.width - 1, self.height - 1

        width = right - left + 1
        height = bottom - top + 1
        descriptor = GIFWriter.image_descriptor(left * self.scale, top * self.scale,
                                                width * self.scale, height * self.scale)

        stream = DataBlock()
        code_length = PALETTE_BITS + 1
        next_code = END_CODE + 1
        code_table = {(i,): i for i in range(2**PALETTE_BITS)}
        stream.encode_bits(CLEAR_CODE, code_length)  # always start with the clear code.

        pattern = tuple()
        for i in range(width * height * self.scale * self.scale):
            y = i // (width * self.scale * self.scale)
            x = (i % (width * self.scale)) // self.scale
            val = self.grid[x + left][y + top]
            c = self.colormap[val]
            pattern += (c,)
            if pattern not in code_table:
                code_table[pattern] = next_code  # add new code in the table.
                stream.encode_bits(code_table[pattern[:-1]], code_length)  # output the prefix.
                pattern = (c,)  # suffix becomes the current pattern.

                next_code += 1
                if next_code == 2**code_length + 1:
                    code_length += 1
                if next_code == MAX_CODES:
                    next_code = END_CODE + 1
                    stream.encode_bits(CLEAR_CODE, code_length)
                    code_length = PALETTE_BITS + 1
                    code_table = {(i,): i for i in range(2**PALETTE_BITS)}

        stream.encode_bits(code_table[pattern], code_length)
        stream.encode_bits(END_CODE, code_length)

        self.num_changes = 0
        self.frame_box = None
        return descriptor + bytearray([PALETTE_BITS]) + stream.dump_bytes() + bytearray([0])

    def paint_background(self, **kwargs):
        """Insert current frame at the beginning to use it as the background.
        This does not require the graphics control block."""
        if kwargs:
            self.set_colors(**kwargs)
        self.writer.data = self.encode_frame() + self.writer.data

    def output_frame(self):
        """Output current frame to the data stream. This method will not be directly called:
        it's called by `refresh_frame()` and `clear_remaining_changes()`."""
        control = self.writer.graphics_control_block(self.delay, self.trans_index)
        self.writer.data += control + self.encode_frame()

    def refresh_frame(self):
        if self.num_changes >= self.speed:
            self.output_frame()

    def clear_remaining_changes(self):
        if self.num_changes > 0:
            self.output_frame()

    def set_colors(self, **kwargs):
        """`wc` is short for wall color, `tc` is short for tree color, etc."""
        color_dict = {'wc': 0, 'tc': 1, 'pc': 2, 'fc': 3}
        for key, val in kwargs.items():
            self.colormap[color_dict[key]] = val

    def pad_delay_frame(self, delay):
        self.writer.data += GIFWriter.pad_delay_frame(delay, self.trans_index)

    def write_to_gif(self, filename):
        self.writer.save_gif(filename)


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
    parser.add_argument('-filename', type=str, default='wilson.gif',
                        help='output file name')

    args = parser.parse_args()

    if (args.width * args.height % 2 == 0):
        raise ValueError('The width and height of the maze must both be odd integers!')

    anim = WilsonAlgoAnimation(args.width, args.height, args.margin, args.scale, args.loop)

    # here we need to paint the blank background because the region that has not been
    # covered by any frame will be set to transparent by decoders.
    # comment this line and watch the result if you don't understand this.
    anim.paint_background(wc=0)

    # pad one second delay, get ready!
    anim.pad_delay_frame(100)

    # in the Wilson's algorithm animation no cells are filled,
    # hence it's safe to use color 3 as the transparent color.
    anim.run_wilson_algorithm(speed=30, delay=2, trans_index=3,
                              wc=0, tc=1, pc=2)

    # pad three seconds delay to help to see the resulting maze clearly.
    anim.pad_delay_frame(300)

    # in the DFS algorithm animation the walls are unchanged throughout,
    # hence it's safe to use color 0 as the transparent color.
    anim.run_dfs_algorithm(speed=10, delay=5, trans_index=0,
                           wc=0, tc=0, pc=2, fc=3)

    # pad five seconds delay to help to see the resulting path clearly.
    anim.pad_delay_frame(500)

    # finally save the bytestream in 'wb' mode.
    anim.write_to_gif(args.filename)


if __name__ == '__main__':
    main()
