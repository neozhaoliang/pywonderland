'''
Animating Wilson's uniform spanning tree algorithm on a 2d grid.
'''

from struct import pack
import random
from lzw import *


BACKGROUND_COLOR = [0, 0, 0]
TREE_COLOR = [200, 200, 200]
PATH_COLOR = [255, 0, 255]
TRANS_COLOR = [0, 255, 0]

BACKGROUND_COLOR_INDEX = 0
TREE_COLOR_INDEX = 1
PATH_COLOR_INDEX = 2
TRANS_COLOR_INDEX = 3

# size of cell in pixels
SCALE = 5
# speed of the animation
SPEED = 10



class Maze(object):

    def __init__ (self, width, height):
        '''
        width, height:  size of the image in cells.
        should both be odd numbers, though works for any positive integers.
        '''
        self.width = width
        self.height = height
        self.canvas_width = width * SCALE
        self.canvas_height = height * SCALE
        self.data = [[0] * self.canvas_height for _ in range(self.canvas_width)]
        self.num_changes = 0
        self.diff_box = None

        self.cells = []
        for y in range(0, height, 2):
            for x in range(0, width, 2):
                self.cells.append((x, y))


    def encode_image(self, left, top, *color_indexes):
        imagedata = [self.data[x][y] for y in range(self.canvas_height) for x in range(self.canvas_width)]

        stream = lzw_encoder(imagedata, *color_indexes)
        descriptor = image_descriptor(left * SCALE, top * SCALE,
                                      self.canvas_width, self.canvas_height)
        return descriptor + stream


    def fill(self, cell, color_index):
        '''
        Note we update the differ box each time we fill a cell
        '''
        x, y = cell
        for ox in range(SCALE):
            for oy in range(SCALE):
                self.data[x*SCALE + ox][y*SCALE + oy] = color_index

        self.num_changes += 1

        if self.diff_box:
            left, top, right, bottom = self.diff_box
            self.diff_box = (min(x, left), min(y, top),
                             max(x, right), max(y, bottom))
        else:
            self.diff_box = (x, y, x, y)


    def output_frame(self):
        left, top, right, bottom = self.diff_box
        width = (right - left) + 1
        height = (bottom - top) + 1
        mask = Maze(width, height)

        for y in range(top, bottom+1):
            for x in range(left, right+1):
                mask.fill((x - left, y - top), self.data[x*SCALE][y*SCALE])

        self.num_changes = 0
        self.diff_box = None
        return mask.encode_image(left, top, BACKGROUND_COLOR_INDEX,
                                 TREE_COLOR_INDEX, PATH_COLOR_INDEX)


    def get_neighbors(self, cell):
        x, y = cell
        neighbors = []
        if x >= 2:
            neighbors.append((x-2, y))
        if y >= 2:
            neighbors.append((x, y-2))
        if x <= self.width-3:
            neighbors.append((x+2, y))
        if y <= self.height-3:
            neighbors.append((x, y+2))
        return neighbors


    def fill_wall(self, cellA, cellB, color_index):
        wall = ((cellA[0] + cellB[0])//2,
                (cellA[1] + cellB[1])//2)
        self.fill(wall, color_index)


    def fill_path(self, path, color_index):
        for cell in path:
            self.fill(cell, color_index)
        for cellA, cellB in zip(path[1:], path[:-1]):
            self.fill_wall(cellA, cellB, color_index)



def delay_frame(delay):
    return (graphics_control_block(delay)
            + image_descriptor(0, 0, 1, 1)
            + chr(PALETTE_BITS)
            + chr(1)
            + chr(TRANS_COLOR_INDEX)
            + chr(0))


def wilson(width, height, root=(0, 0)):
    maze = Maze(width, height)
    stream = str()
    tree = set([root])

    for cell in maze.cells:
        if cell not in tree:
            path = [cell]
            maze.fill(cell, PATH_COLOR_INDEX)

            current_cell = cell
            while current_cell not in tree:
                next_cell = random.choice(maze.get_neighbors(current_cell))
                if next_cell in path:
                    index = path.index(next_cell)
                    # erase path
                    maze.fill_path(path[index:], BACKGROUND_COLOR_INDEX)
                    maze.fill(path[index], PATH_COLOR_INDEX)
                    path = path[:index+1]

                else:
                    path.append(next_cell)
                    maze.fill(next_cell, PATH_COLOR_INDEX)
                    maze.fill_wall(current_cell, next_cell, PATH_COLOR_INDEX)

                current_cell = next_cell

                if maze.num_changes >= SPEED:
                    stream += graphics_control_block(2) + maze.output_frame()
            for v in path:
                tree.add(v)

            maze.fill_path(path, TREE_COLOR_INDEX)


    if maze.num_changes > 0:
        stream += graphics_control_block(2) + maze.output_frame()

    # pad 1x1 pixel frame
    stream = delay_frame(50) + stream + delay_frame(300)
    # add background frame
    stream = Maze(width, height).encode_image(0, 0, BACKGROUND_COLOR_INDEX) + stream
    screen_descriptor = logical_screen_descriptor(maze.canvas_width, maze.canvas_height)
    palette = global_color_table(BACKGROUND_COLOR, TREE_COLOR,
                               PATH_COLOR, TRANS_COLOR)

    with open('wilson.gif', 'w') as f:
        f.write('GIF89a'
                + screen_descriptor
                + palette
                + loop_control_block()
                + stream
                + '\x3B')


if __name__ == '__main__':
    wilson(101, 81)
