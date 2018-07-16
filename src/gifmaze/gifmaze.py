# -*- coding: utf-8 -*-
"""
`Maze` is the top layer object on which we run the algorithms.

`GIFSurface` is the bottom layer object that handles the information
about the output GIF image.

`Animation` is the middle layer object that controls how
a `Maze` object is rendered to a `GIFSurface` object.
"""
from io import BytesIO
from functools import partial
from PIL import Image
import encoder


class Maze(object):
    """
    This class defines the basic structure of a maze and some operations on it.
    A maze is represented by a grid with `height` rows and `width` columns,
    each cell in the maze has 4 possible states:
    0: it's a wall
    1: it's in the tree
    2: it's in the path
    3: it's filled (this will not be used until the maze-searching animation)
    Initially all cells are walls.
    Adjacent cells in the maze are spaced out by one cell.
    """

    WALL = 0
    TREE = 1
    PATH = 2
    FILL = 3

    def __init__(self, width, height, mask):
        """
        Parameters
        ----------
        width, height: size of the maze, must both be odd integers.

        mask: `None` or an file-like image or an instance of PIL's Image class.
              If not `None` then this mask image must be of binary type:
              the black pixels are considered as `walls` and are overlayed
              on top of the grid graph. Note the walls must preserve the
              connectivity of the grid graph, otherwise the program will
              not terminate.
        """
        if (width * height % 2 == 0):
            raise ValueError('The width and height must both be odd integers.')

        self.width = width
        self.height = height
        self._grid = [[0] * height for _ in range(width)]
        self._num_changes = 0   # a counter holds how many cells are changed.
        self._frame_box = None  # a 4-tuple maintains the region that to be updated.

        if mask is not None:
            if isinstance(mask, Image.Image):
                mask = mask.convert('L').resize((width, height))
            else:
                mask = Image.open(mask).convert('L').resize((width, height))

        def get_mask_pixel(cell):
            return mask is None or mask.getpixel(cell) == 255

        self.cells = []
        for y in range(0, height, 2):
            for x in range(0, width, 2):
                if get_mask_pixel((x, y)):
                    self.cells.append((x, y))

        def neighborhood(cell):
            x, y = cell
            neighbors = []
            if x >= 2 and get_mask_pixel((x - 2, y)):
                neighbors.append((x - 2, y))
            if y >= 2 and get_mask_pixel((x, y - 2)):
                neighbors.append((x, y - 2))
            if x <= width - 3 and get_mask_pixel((x + 2, y)):
                neighbors.append((x + 2, y))
            if y <= height - 3 and get_mask_pixel((x, y + 2)):
                neighbors.append((x, y + 2))
            return neighbors

        self._graph = {v: neighborhood(v) for v in self.cells}
        self.scaling = 1
        self.translation = (0, 0)

    def get_neighbors(self, cell):
        return self._graph[cell]

    def mark_cell(self, cell, value):
        """Mark a cell and update `frame_box` and `num_changes`."""
        x, y = cell
        self._grid[x][y] = value
        self._num_changes += 1

        if self._frame_box is not None:
            left, top, right, bottom = self._frame_box
            self._frame_box = (min(x, left),  min(y, top),
                               max(x, right), max(y, bottom))
        else:
            self._frame_box = (x, y, x, y)

    def mark_space(self, c1, c2, value):
        """Mark the space between two adjacent cells."""
        c = ((c1[0] + c2[0]) // 2, (c1[1] + c2[1]) // 2)
        self.mark_cell(c, value)

    def mark_path(self, path, value):
        """Mark the cells in a path and the spaces between them."""
        for cell in path:
            self.mark_cell(cell, value)
        for c1, c2 in zip(path[1:], path[:-1]):
            self.mark_space(c1, c2, value)

    def get_cell(self, cell):
        x, y = cell
        return self._grid[x][y]

    def barrier(self, c1, c2):
        """Check if two adjacent cells are connected."""
        x = (c1[0] + c2[0]) // 2
        y = (c1[1] + c2[1]) // 2
        return self._grid[x][y] == Maze.WALL

    def is_wall(self, cell):
        x, y = cell
        return self._grid[x][y] == Maze.WALL

    def in_tree(self, cell):
        x, y = cell
        return self._grid[x][y] == Maze.TREE

    def in_path(self, cell):
        x, y = cell
        return self._grid[x][y] == Maze.PATH

    def reset(self):
        self._num_changes = 0
        self._frame_box = None

    @property
    def frame_box(self):
        return self._frame_box

    @property
    def num_changes(self):
        return self._num_changes

    def scale(self, c):
        self.scaling = c
        return self

    def translate(self, v):
        self.translation = v
        return self


class GIFSurface(object):
    """
    A GIFSurface is an object on which the animations are drawn,
    and which can be saved as GIF images.
    Each instance opens a BytesIO file in memory once it's created.
    The frames are temporarily written to this in-memory file for speed.
    When the animation is finished one should call the `close()` method
    to close the io.
    """
    def __init__(self, width, height, loop=0, bg_color=None):
        """
        ----------
        Parameters

        width, height: size of the image in pixels.

        loop: number of loops of the image.

        bg_color: background color index.
        """
        self.width = width
        self.height = height
        self.loop = loop
        self.palette = None
        self._io = BytesIO()

        if bg_color is not None:
            self.write(encoder.rectangle(0, 0, width, height, bg_color))

    @classmethod
    def from_image(cls, img_file, loop=0):
        """
        Create a surface from a given image file.
        The size of the returned surface is the same with the image's.
        The image is then painted as the background.
        """
        # the image file usually contains more than 256 colors
        # so we need to convert it to gif format first.
        with BytesIO() as temp_io:
            Image.open(img_file).convert('RGB').save(temp_io, format='gif')
            img = Image.open(temp_io).convert('RGB')
            surface = cls(img.size[0], img.size[1], loop=loop)
            surface.write(encoder.parse_image(img))
        return surface

    def write(self, data):
        self._io.write(data)

    def set_palette(self, palette):
        """
        Set the global color table of the GIF image.
        The user must specify at least one rgb color in it.
        `palette` must be a 1-d list of integers between 0-255.
        """
        try:
            palette = bytearray(palette)
        except:
            raise ValueError('A 1-d list of integers in range 0-255 is expected.')

        if len(palette) < 3:
            raise ValueError('At least one (r, g, b) triple is required.')

        nbits = (len(palette) // 3).bit_length() - 1
        nbits = min(max(nbits, 1), 8)
        valid_len = 3 * (1 << nbits)
        if len(palette) > valid_len:
            palette = palette[:valid_len]
        else:
            palette.extend([0] * (valid_len - len(palette)))

        self.palette = palette

    @property
    def _gif_header(self):
        """
        Get the `logical screen descriptor`, `global color table`
        and `loop control block`.
        """
        if self.palette is None:
            raise ValueError('Missing global color table.')

        color_depth = (len(self.palette) // 3).bit_length() - 1
        screen = encoder.screen_descriptor(self.width, self.height, color_depth)
        loop = encoder.loop_control_block(self.loop)
        return screen + self.palette + loop

    def save(self, filename):
        """
        Save the animation to a .gif file, note the 'wb' mode here!
        """
        with open(filename, 'wb') as f:
            f.write(self._gif_header)
            f.write(self._io.getvalue())
            f.write(bytearray([0x3B]))

    def close(self):
        self._io.close()


class Render(object):
    """
    This class encodes the region specified by the `frame_box` attribute of a maze
    into one frame in the GIF image.
    """
    def __init__(self, cmap, mcl):
        """
        cmap: a dict that maps the value of the cells to their color indices.

        mcl: the minimum code length for the LZW compression.

        A default dict is initialized so that one can set the colormap by
        just specifying what needs to be specified.
        """
        self.colormap = {i: i for i in range(1 << mcl)}
        if cmap:
            self.colormap.update(cmap)
        self.compress = partial(encoder.lzw_compress, mcl=mcl)

    def __call__(self, maze):
        """
        Encode current maze into one frame and return the encoded data.
        Note the graphics control block is not added here.
        """
        # the image descriptor
        if maze.frame_box is not None:
            left, top, right, bottom = maze.frame_box
        else:
            left, top, right, bottom = 0, 0, maze.width - 1, maze.height - 1

        width = right - left + 1
        height = bottom - top + 1
        descriptor = encoder.image_descriptor(maze.scaling * left + maze.translation[0],
                                              maze.scaling * top + maze.translation[1],
                                              maze.scaling * width,
                                              maze.scaling * height)

        pixels = [self.colormap[maze.get_cell((x // maze.scaling + left,
                                               y // maze.scaling + top))]
                  for y in range(height * maze.scaling)
                  for x in range(width * maze.scaling)]

        # the compressed image data of this frame
        data = self.compress(pixels)
        # clear `num_changes` and `frame_box`
        maze.reset()

        return descriptor + data


class Animation(object):
    """
    This class is the main entrance for calling algorithms to
    run and rendering the maze into the image.
    """

    def __init__(self, surface):
        self._gif_surface = surface

    def pause(self, delay, trans_index=0):
        """Pause the animation by padding a 1x1 invisible frame."""
        self._gif_surface.write(encoder.pause(delay, trans_index))

    def paint(self, *args):
        """Paint a rectangular region in the surface."""
        self._gif_surface.write(encoder.rectangle(*args))

    def run(self, algo, maze, delay=5, trans_index=None,
            cmap=None, mcl=8, **kwargs):
        """
        The entrance for running the animations.

        --------
        Parameters:

        algo: name of the algorithm.

        maze: an instance of the `Maze` class.

        delay: delay time between successive frames.

        trans_index: the transparent channel.
            `None` means there is no transparent color.

        cmap: a dict that maps the values of the cells in a maze
            to their color indices.

        mcl: see the doc for the lzw_compress.
        """
        render = Render(cmap, mcl)
        control = encoder.graphics_control_block(delay, trans_index)
        for frame in algo(maze, render, **kwargs):
            self._gif_surface.write(control + frame)
