# -*- coding: utf-8 -*-

"""
A helper class for building environment for making animations.
"""
from encoder import GIFWriter


class Canvas(object):

    def __init__(self, width, height, scale, min_bits, palette, loop):
        self.width = width
        self.height = height
        self.grid = [[0]*height for _ in range(width)]
        self.scale = scale
        self.num_changes = 0   # a counter holds how many cells are changed.
        self.frame_box = None  # maintains the region that to be updated.
        self.writer = GIFWriter(width * scale, height * scale, min_bits, palette, loop)
        self.colormap = {i: i for i in range(1 << min_bits)}
        
        self.speed = 10        # output the frame once this number of cells are changed.
        self.trans_index = 3   # the index of the transparent color in the global color table.
        self.delay = 5         # delay between successive frames.

    def mark_cell(self, cell, index):
        """Mark a cell and update `frame_box` and `num_changes`."""
        x, y = cell
        self.grid[x][y] = index

        if self.frame_box is not None:
            left, top, right, bottom = self.frame_box
            self.frame_box = (min(x, left), min(y, top),
                              max(x, right), max(y, bottom))
        else:
            self.frame_box = (x, y, x, y)

        self.num_changes += 1

    def encode_frame(self):
        if self.frame_box is not None:
            left, top, right, bottom = self.frame_box
        else:
            left, top, right, bottom = 0, 0, self.width - 1, self.height - 1

        width = right - left + 1
        height = bottom - top + 1
        descriptor = GIFWriter.image_descriptor(left * self.scale, top * self.scale,
                                                width * self.scale, height * self.scale)
        
        def get_frame_pixels():
            for i in range(width * height * self.scale * self.scale):
                y = i // (width * self.scale * self.scale)
                x = (i % (width * self.scale)) // self.scale
                val = self.grid[x + left][y + top]
                c = self.colormap[val]
                yield c

        frame = self.writer.LZW_encode(get_frame_pixels())
        self.num_changes = 0
        self.frame_box = None
        return descriptor + frame

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
        self.writer.data += self.writer.pad_delay_frame(delay, self.trans_index)

    def write_to_gif(self, filename):
        self.writer.save_gif(filename)


def test():
    palette = [0, 0, 0, 255, 255, 255, 255, 0, 0, 255, 0, 255]
    canvas = Canvas(width=50, height=50, scale=5,
                    min_bits=2, palette=palette, loop=0)
    # use the 3rd color in the palette to paint all cells with value 0.
    canvas.paint_background(wc=2)
    canvas.pad_delay_frame(300)

    canvas.delay = 5
    canvas.speed = 50
    # change the colormap, now use the 1st color in the palette
    # to paint cells with value 0.
    canvas.set_colors(wc=0)
    for y in range(canvas.height):
        for x in range(canvas.width):
            canvas.mark_cell((x, y), (x + y) % 2)
            canvas.refresh_frame()

    canvas.clear_remaining_changes()
    canvas.pad_delay_frame(500)
    canvas.write_to_gif('test.gif')


if __name__ == '__main__':
    test()
