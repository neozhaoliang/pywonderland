from struct import pack
import random, argparse
from lzw import lzw_encoder


LZW_palette_bits = 2
LZW_clear_code = 4
LZW_end_code = 5
LZW_max_codes = 4096

bg_index = 0
fg_index = 1
alt_fg_index = 2
trans_index = 3


class Bitmap:
    def __init__ (self, width, height):
	self.width = width
	self.height = height
        self.canvas_width = width * thickness
        self.canvas_height = height * thickness
	self.data = [[0] * self.canvas_height for _ in range(self.canvas_width)]
	self.num_changes = 0
	self.diff_box = None
        self.cells = []
        for y in range(0, height, 2):
            for x in range(0, width, 2):
                self.cells.append((x, y))

    def encode_image (self, left, top, *color_indexes):
        imagedata = [self.data[x][y] for y in range(self.canvas_height) for x in range(self.canvas_width)]

        stream = lzw_encoder(imagedata, *color_indexes)

	descriptor = image_descriptor_block(left * thickness,
					    top * thickness,
					    self.canvas_width,
					    self.canvas_height)
	return descriptor + stream

    def set_color(self, x, y, color_index):
        for ox in range(thickness):
	    for oy in range(thickness):
		self.data[x*thickness + ox][y*thickness + oy] = color_index


    def fill(self, x, y, color_index):
        self.set_color(x, y, color_index)
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
	mask = Bitmap(width, height)

	for y in range(top, bottom+1):
            for x in range(left, right+1):
	        mask.fill(x - left, y - top, self.data[x*thickness][y*thickness])

	self.num_changes = 0
	self.diff_box = None
	return mask.encode_image(left, top, bg_index, fg_index, alt_fg_index)


    def get_connections (self, x, y):
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
                self.fill((a[0]+b[0])/2, (a[1]+b[1])/2, color_index)


def delay_frame (delay):
    return (graphics_control_block(delay) +
	    image_descriptor_block(0, 0, 1, 1) +
	    chr(LZW_palette_bits) +
	    chr(1) +
	    chr(trans_index) +
	    chr(0) )

def loop_control_block():
    return pack('<3B8s3s2BHB', 0x21, 0xFF, 11, 'NETSCAPE', '2.0', 3, 1, 0, 0)

def global_palette_block(*color_list):
    palette = []
    for color in color_list:
        palette.extend(color)
    return pack('{:d}B'.format(len(palette)), *palette);

def graphics_control_block(delay):
    return pack("<4BH2B", 0x21, 0xF9, 4, 0b00000100, delay, 0, 0)

def image_descriptor_block(left, top, width, height):
    return pack('<B4HB', 0x2C, left, top, width, height, 0)

def logical_screen_descriptor_block(width, height):
    return pack('<2H3B', width, height, 0b10010001, 0, 0)


width, height = (151, 121)
thickness = 4
cells_per_frame = 10
fg_color = [255, 0, 255]
bg_color = [10, 10, 10]
alt_color = [0, 0, 255]
trans_color = [0, 255, 0]
stream = str()
bitmap = Bitmap(width, height)
x, y = (0, 0)
tree = set([(x, y)])
for x, y in bitmap.cells:
    ox, oy = x, y
    path = [(ox, oy)]
    while (ox, oy) not in tree:
        nx, ny = random.choice(bitmap.get_connections(ox, oy))
        if (nx, ny) in path:
            index = path.index((nx, ny))
            bitmap.fillpath(path[index:], bg_index)
            bitmap.fill(path[index][0], path[index][1], alt_fg_index)
            path = path[:index+1]

        else:
            path.append((nx, ny))
            bitmap.fill(nx, ny, alt_fg_index)
            bitmap.fill((nx+ox)/2, (ny+oy)/2, alt_fg_index)

        ox, oy = nx, ny

        if bitmap.num_changes >= cells_per_frame:
	    stream += graphics_control_block(2) + bitmap.get_diffmask()


    for v in path:
        tree.add(v)

    bitmap.fillpath(path, fg_index)

if bitmap.num_changes > 0:
    stream += graphics_control_block(2) + bitmap.get_diffmask()
'''
stream = (delay_frame(50) +
	  stream +
          delay_frame(300) )
'''
#stream = Bitmap(width, height).encode_image(0, 0, bg_index, fg_index, alt_fg_index) + stream
image_descriptor = logical_screen_descriptor_block(bitmap.canvas_width, bitmap.canvas_height)
palette = global_palette_block(bg_color, fg_color, alt_color)
open('anim.gif', 'w').write('GIF89a' +
			    image_descriptor +
			    palette +
                            loop_control_block() +
                            stream +
			    '\x3B')
