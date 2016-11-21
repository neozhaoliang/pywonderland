from struct import pack
import random
from lzw import lzw_encoder, PALETTE_BITS


BACKGROUND_COLOR = [0, 0, 0]
TREE_COLOR = [200, 200, 200]
PATH_COLOR = [255, 0, 255]
TRANS_COLOR = [0, 255, 0]

BACKGROUND_COLOR_INDEX = 0
TREE_COLOR_INDEX = 1
PATH_COLOR_INDEX = 2
TRANS_COLOR_INDEX = 3

SCALE = 5


class Maze(object):

    def __init__ (self, width, height):
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


    def fill(self, x, y, color_index):
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


    def get_diffmask(self):
        left, top, right, bottom = self.diff_box
        width = (right - left) + 1
        height = (bottom - top) + 1
        mask = Maze(width, height)

        for y in range(top, bottom+1):
            for x in range(left, right+1):
                mask.fill(x - left, y - top, self.data[x*SCALE][y*SCALE])

        self.num_changes = 0
        self.diff_box = None
        return mask.encode_image(left, top, BACKGROUND_COLOR_INDEX,
                                 TREE_COLOR_INDEX, PATH_COLOR_INDEX)


    def get_neighbors(self, x, y):
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


    def fillpath(self, path, color_index):
        if len(path) == 1:
            x, y = path[0]
            self.fill(x, y, color_index)
        else:
            for x, y in path:
                self.fill(x, y, color_index)
            for a, b in zip(path[1:], path[:-1]):
                self.fill((a[0]+b[0])//2, (a[1]+b[1])//2, color_index)



def delay_frame(delay):
    return (graphics_control_block(delay) +
            image_descriptor(0, 0, 1, 1) +
            chr(PALETTE_BITS) +
            chr(1) +
            chr(TRANS_COLOR_INDEX) +
            chr(0))


def loop_control_block():
    return pack('<3B8s3s2BHB', 0x21, 0xFF, 11, 'NETSCAPE', '2.0', 3, 1, 0, 0)


def global_color_table(*color_list):
    palette = []
    for color in color_list:
        palette.extend(color)
    return pack('{:d}B'.format(len(palette)), *palette);


def graphics_control_block(delay):
    return pack("<4BH2B", 0x21, 0xF9, 4, 0b00000101, delay, 3, 0)


def image_descriptor(left, top, width, height):
    return pack('<B4HB', 0x2C, left, top, width, height, 0)


def logical_screen_descriptor(width, height):
    return pack('<2H3B', width, height, 0b10010001, 0, 0)


width, height = (101, 81)
speed = 10
stream = str()
maze = Maze(width, height)
root = (0, 0)
tree = set([root])

for x, y in maze.cells:
    if (x, y) not in tree:
        path = [(x, y)]
        maze.fill(x, y, PATH_COLOR_INDEX)

        ox, oy = x, y
        while (ox, oy) not in tree:
            nx, ny = random.choice(maze.get_neighbors(ox, oy))
            if (nx, ny) in path:
                index = path.index((nx, ny))
                maze.fillpath(path[index:], BACKGROUND_COLOR_INDEX)
                maze.fill(path[index][0], path[index][1], PATH_COLOR_INDEX)
                path = path[:index+1]

            else:
                path.append((nx, ny))
                maze.fill(nx, ny, PATH_COLOR_INDEX)
                maze.fill((nx+ox)//2, (ny+oy)//2, PATH_COLOR_INDEX)

            ox, oy = nx, ny

            if maze.num_changes >= speed:
                stream += graphics_control_block(2) + maze.get_diffmask()

        for v in path:
            tree.add(v)

        maze.fillpath(path, TREE_COLOR_INDEX)


if maze.num_changes > 0:
    stream += graphics_control_block(2) + maze.get_diffmask()

stream = delay_frame(50) + stream + delay_frame(300)
stream = Maze(width, height).encode_image(0, 0, BACKGROUND_COLOR_INDEX) + stream
screen_descriptor = logical_screen_descriptor(maze.canvas_width, maze.canvas_height)
palette = global_color_table(BACKGROUND_COLOR, TREE_COLOR,
                               PATH_COLOR, TRANS_COLOR)
open('wilson.gif', 'w').write('GIF89a' +
                            screen_descriptor +
                            palette +
                            loop_control_block() +
                            stream +
                            '\x3B')
