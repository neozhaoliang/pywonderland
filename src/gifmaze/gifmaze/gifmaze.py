"""
This file contains three main classes:
1. `Maze` is the top layer object on which we run the algorithms.
2. `GIFSurface` is the bottom layer object which holds the information
   of the output GIF image.
3. `Animation` is the middle layer object that controls how a `Maze`
   object is rendered to a `GIFSurface` object.
"""
from functools import partial
from io import BytesIO
from PIL import Image

from . import encoder


class Maze:

    """
    This class defines the basic structure of a maze and some operations on it.
    A maze with `height` rows and `width` columns is represented by a larger 2d
    array with (2 * height - 1) rows and (2 * width - 1) columns: we also pad
    entries for the 'wall's between adjacent cells, so adjacent cells are spaced
    out by one cell in the larger grid.
    Each cell has 4 possible states:
    0: it's a wall
    1: it's in the tree
    2: it's in the path
    3: it's filled (this will not be used until the maze-searching animation)
    Initially all cells are walls.
    """

    WALL = 0
    TREE = 1
    PATH = 2
    FILL = 3

    def __init__(self, width, height, mask=None, cell_init=0, wall_init=0):
        """
        :param width & height: size of the maze.
        :param mask: `None` or a file-like image or an instance of PIL's Image class.
            If not `None` then this mask image must have binary type:
            the black pixels are considered as `walls` and are overlayed on top of the
            grid graph. These walls must preserve the connectivity of the grid graph,
            otherwise the program will not terminate.
        :param cell_init: an integer to initialize the cells of the maze.
        :param wall_init: an integer to initialize the walls of the maze.
        """
        self.width = 2 * width - 1
        self.height = 2 * height - 1
        self._frame_box = None  # a 4-tuple maintains the region that to be updated.
        self._num_changes = 0  # a counter holds how many cells are changed.

        self.scaling = 1  # size of a cell in pixels.
        self.translation = (0, 0)  # (left, top) translation about the image in pixels.
        self.lw = 1  # line width of the walls in pixels.

        if mask is not None:
            if isinstance(mask, Image.Image):
                mask = mask.convert("L").resize((self.width, self.height))
            else:
                mask = Image.open(mask).convert("L").resize((self.width, self.height))

        def get_mask_pixel(cell):
            return mask is None or mask.getpixel(cell) == 255

        self.cells = []
        for y in range(0, self.height, 2):
            for x in range(0, self.width, 2):
                if get_mask_pixel((x, y)):
                    self.cells.append((x, y))

        # initialize the cells
        self._grid = [[wall_init] * self.height for _ in range(self.width)]
        for x, y in self.cells:
            self._grid[x][y] = cell_init

        def neighborhood(cell):
            x, y = cell
            neighbors = []
            if x >= 2 and get_mask_pixel((x - 2, y)):
                neighbors.append((x - 2, y))
            if y >= 2 and get_mask_pixel((x, y - 2)):
                neighbors.append((x, y - 2))
            if x <= self.width - 3 and get_mask_pixel((x + 2, y)):
                neighbors.append((x + 2, y))
            if y <= self.height - 3 and get_mask_pixel((x, y + 2)):
                neighbors.append((x, y + 2))
            return neighbors

        self._graph = {v: neighborhood(v) for v in self.cells}

    def get_neighbors(self, cell):
        return self._graph[cell]

    def mark_cell(self, cell, value):
        """Mark a cell and update `frame_box` and `num_changes`.
        """
        x, y = cell
        self._grid[x][y] = value
        self._num_changes += 1
        if self._frame_box is not None:
            left, top, right, bottom = self._frame_box
            self._frame_box = (min(x, left), min(y, top), max(x, right), max(y, bottom))
        else:
            self._frame_box = (x, y, x, y)

    def get_cell(self, cell):
        x, y = cell
        return self._grid[x][y]

    def mark_space(self, c1, c2, value):
        """Mark the space between two adjacent cells.
        """
        c = ((c1[0] + c2[0]) // 2, (c1[1] + c2[1]) // 2)
        self.mark_cell(c, value)

    def mark_path(self, path, value):
        """Mark the cells in a path and the spaces between them.
        """
        for cell in path:
            self.mark_cell(cell, value)
        for c1, c2 in zip(path[1:], path[:-1]):
            self.mark_space(c1, c2, value)

    def barrier(self, c1, c2):
        """Check if two adjacent cells are connected.
        """
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
        self._frame_box = None
        self._num_changes = 0

    @property
    def frame_box(self):
        return self._frame_box

    @property
    def num_changes(self):
        return self._num_changes

    def scale(self, c):
        self.scaling *= c
        return self

    def translate(self, v):
        self.translation = (self.translation[0] + v[0], self.translation[1] + v[1])
        return self

    def setlinewidth(self, l):
        self.lw = l
        return self


class GIFSurface:

    """
    A GIFSurface is an object on which the animations are drawn, and
    which can be saved as GIF images. Each instance opens a BytesIO file
    in memory when it's created. The frames are temporarily written to
    this in-memory file for speed. When the animation is finished one should
    call the `finish()` method to close the io.
    """

    def __init__(self, width, height, loop=0, bg_color=None):
        """
        :param width & height: size of the image in pixels.
        :param loop: number of loops of the image.
        :param bg_color: background color index.
        """
        self.width = width
        self.height = height
        self.loop = loop
        self.palette = None
        self._io = BytesIO()

        # one can insert data at the beginning while the animation is running
        self.init_data = bytearray()
        if bg_color is not None:
            self.init_data += encoder.rectangle(0, 0, width, height, bg_color)

    @classmethod
    def from_image(cls, img_file, loop=0):
        """
        Create a surface from a given image file. The size of the returned surface
        is the same with the image's. The image is then painted as the background.
        """
        # the image file usually contains more than 256 colors
        # so we need to convert it to gif format first.
        with BytesIO() as temp_io:
            Image.open(img_file).convert("RGB").save(temp_io, format="gif")
            img = Image.open(temp_io).convert("RGB")
            surface = cls(img.size[0], img.size[1], loop=loop)
            surface.write(encoder.parse_image(img))
        return surface

    def write(self, data):
        self._io.write(data)

    def set_palette(self, palette):
        """
        Set the global color table of the GIF image. The user must specify at least
        one rgb color for it. `palette` must be a 1-d list of integers between 0-255.
        Example:
            palette = [255, 0, 0,  # red
                       0, 255, 0,  # green
                       0, 0, 255]  # blue

        A gif image can have at most 256 colors in the global color table, redundant
        colors will be discarded if the input `palette` contains more than 256 colors.
        """
        try:
            palette = bytearray(palette)
        except:
            raise ValueError("A 1-d list of integers in range 0-255 is expected.")

        if len(palette) < 3:
            raise ValueError("At least one (r, g, b) triple is required.")

        nbits = (len(palette) // 3 - 1).bit_length()
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
        Get the `logical screen descriptor`, `global color table` and `loop
        control block`.
        """
        if self.palette is None:
            raise ValueError("Missing global color table.")

        color_depth = (len(self.palette) // 3).bit_length() - 1
        screen = encoder.screen_descriptor(self.width, self.height, color_depth)
        loop = encoder.loop_control_block(self.loop)
        return screen + self.palette + loop

    def save(self, filename):
        """Save the animation to a .gif file, note the 'wb' mode here!
        """
        with open(filename, "wb") as f:
            f.write(self._gif_header)
            f.write(self.init_data)
            f.write(self._io.getvalue())
            f.write(bytearray([0x3B]))

    def finish(self):
        self._io.close()


def encode_maze(maze, mcl=8, cmap=None):
    """
    Encode a maze into one frame in the gif image.

    :param maze: a Maze object.
    :param mcl: minimal code length for lzw compression.
    :param cmap: a dict for mapping the cells to color indices,
        the items are like {value: color_index}.

    Note: if we know exactly how many colors are there in this frame then
    we can choose the most economical minimal code length for it. For example
    if a frame contains 12 different colors, then since 2^3 < 12 < 2^4,
    `mcl=4` is the shortest valid minimal code length for this frame.
    """
    colormap = {i: i for i in range(1 << mcl)}
    if cmap is not None:
        colormap.update(cmap)

    if maze.frame_box is not None:
        left, top, right, bottom = maze.frame_box
    else:
        left, top, right, bottom = 0, 0, maze.width - 1, maze.height - 1

    def enum_pixels(k, l):
        """
        Compute how many pixels are there from the k-th cell to the l-th
        cell (k < l) in a row (or column).
        """
        w = l - k + 1  # total number of cells in this interval
        if w % 2 == 0:  # cells and walls are one-half to one-half
            return (w // 2) * (maze.scaling + maze.lw)
        if l % 2 == 0:  # cells are exactly one more than the walls
            return (w - 1) // 2 * (maze.scaling + maze.lw) + maze.scaling
        # cells are exactly one less than the walls
        return (w - 1) // 2 * (maze.scaling + maze.lw) + maze.lw

    # the image descriptor for this frame
    descriptor = encoder.image_descriptor(
        enum_pixels(0, left - 1) + maze.translation[0],
        enum_pixels(0, top - 1) + maze.translation[1],
        enum_pixels(left, right),
        enum_pixels(top, bottom),
    )

    def map_pixel(x, y):
        """
        Map a pixel (x, y) in this frame to the cell that contains it
        and assign a color to this pixel by the value of the cell.
        """
        # find the horizontal coordinate
        q, r = divmod(x, maze.scaling + maze.lw)
        if left % 2 == 0:
            dx = 2 * q if r < maze.scaling else 2 * q + 1
        else:
            dx = 2 * q if r < maze.lw else 2 * q + 1

        # find the vertical coordinate
        q, r = divmod(y, maze.scaling + maze.lw)
        if top % 2 == 0:
            dy = 2 * q if r < maze.scaling else 2 * q + 1
        else:
            dy = 2 * q if r < maze.lw else 2 * q + 1

        return colormap[maze.get_cell((left + dx, top + dy))]

    # a 1-d list holds all pixels in this frame
    pixels = [
        map_pixel(x, y)
        for y in range(enum_pixels(top, bottom))
        for x in range(enum_pixels(left, right))
    ]

    # the compressed image data of this frame
    data = encoder.lzw_compress(pixels, mcl)
    # clear `num_changes` and `frame_box`
    maze.reset()

    return descriptor + data


class Animation:

    """
    This class is the main entrance for calling algorithms to
    run and rendering the Maze into the gif image.
    """

    def __init__(self, surface):
        self._gif_surface = surface

    def pause(self, delay, trans_index=0):
        """Pause the animation by padding a 1x1 invisible frame.
        """
        self._gif_surface.write(encoder.pause(delay, trans_index))

    def paint(self, left, top, width, height, color):
        """Paint a rectangular region in the surface.
        """
        self._gif_surface.write(encoder.rectangle(left, top, width, height, color))

    def insert_frame(self, data):
        """One can insert data at the beginning of the image while the animation
        is running.
        """
        self._gif_surface.init_data += data

    def run(self, algo, maze, delay=5, trans_index=None,
            cmap=None, mcl=8, **kwargs):
        """This is the main entrance for using this class to encode an animation
        into frames.

        :param algo: a maze generating/solving algorithm implemented as a generator.
        :param maze: an instance of the maze class.
        :param delay: delay between consecutive frames.
        :trans_index: transparent color index used in this animation.
        :cmap: a dict that maps cells to color indices.
        :mcl: minimal code length for lzw compression.
        """
        encode_func = partial(encode_maze, cmap=cmap, mcl=mcl)
        control = encoder.graphics_control_block(delay, trans_index)
        for frame in algo(maze, encode_func, **kwargs):
            self._gif_surface.write(control + frame)

    def save(self, filename):
        """A simple wrapper for saving and closing a `GIFSurface`.
        """
        self._gif_surface.save(filename)
        self._gif_surface.finish()

    def show_grid(self, maze, bg_color, line_color, **kwargs):
        """Draw the background grid of a Maze.

        :param maze: a Maze object.
        :param bg_color: background color (for the cells)
        :param line_color: line color (for the walls between adjacent cells)
        """
        new_maze = Maze(
            (maze.width + 1) // 2,
            (maze.height + 1) // 2,
            cell_init=bg_color,
            wall_init=line_color,
        )
        new_maze.scale(maze.scaling).translate(maze.translation).setlinewidth(maze.lw)
        self.insert_frame(encode_maze(new_maze, **kwargs))
