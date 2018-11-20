"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Draw Hilbert's curve using Gray code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from colorsys import hls_to_rgb
import gifmaze as gm


class Hilbert(object):
    """Multi-dimensional Hilbert space-filling curve.
    """

    def __init__(self, n):
        """Create an n-dimensional Hilbert space-filling curve.
        """
        self.n = n
        self.mask = (1 << n) - 1

    def encode(self, index):
        """Convert index to coordinates of a point on the Hilbert curve.
        """

        # Compute base-n digits of index.
        digits = []
        while True:
            index, digit = divmod(index, self.mask + 1)
            digits.append(digit)
            if index == 0:
                break

        # Start with largest hypercube orientation that preserves
        # orientation of smaller order curves.
        vertex, edge = (0, -len(digits) % self.n)

        # Visit each base-n digit of index, most significant first.
        coords = [0] * self.n
        for digit in reversed(digits):

            # Compute position in current hypercube, distributing the n
            # bits across n coordinates.
            bits = self.subcube_encode(digit, vertex, edge)
            for bit in range(self.n):
                coords[bit] = (coords[bit] << 1) | (bits & 1)
                bits = bits >> 1

            # Compute orientation of next sub-cube.
            vertex, edge = self.rotate(digit, vertex, edge)
        return tuple(2 * x + 1 for x in coords)

    def decode(self, coords):
        """Convert coordinates to index of a point on the Hilbert curve.
        """

        # Convert n m-bit coordinates to m base-n digits.
        coords = list(coords)
        m = self.log2(max(coords)) + 1
        digits = []
        for i in range(m):
            digit = 0
            for bit in range(self.n - 1, -1, -1):
                digit = (digit << 1) | (coords[bit] & 1)
                coords[bit] = coords[bit] >> 1
            digits.append(digit)

        # Start with largest hypercube orientation that preserves
        # orientation of smaller order curves.
        vertex, edge = (0, -m % self.n)

        # Visit each base-n digit, most significant first.
        index = 0
        for digit in reversed(digits):

            # Compute index of position in current hypercube.
            bits = self.subcube_decode(digit, vertex, edge)
            index = (index << self.n) | bits

            # Compute orientation of next sub-cube.
            vertex, edge = self.rotate(bits, vertex, edge)
        return index

    def subcube_encode(self, index, vertex, edge):
        h = self.gray_encode(index)
        h = (h << (edge + 1)) | (h >> (self.n - edge - 1))
        return (h & self.mask) ^ vertex

    def subcube_decode(self, code, vertex, edge):
        k = code ^ vertex
        k = (k >> (edge + 1)) | (k << (self.n - edge - 1))
        return self.gray_decode(k & self.mask)

    def rotate(self, index, vertex, edge):
        v = self.subcube_encode(max((index - 1) & ~1, 0), vertex, edge)
        w = self.subcube_encode(min((index + 1) | 1, self.mask), vertex, edge)
        return (v, self.log2(v ^ w))

    def gray_encode(self, index):
        return index ^ (index >> 1)

    def gray_decode(self, code):
        index = code
        while code > 0:
            code = code >> 1
            index = index ^ code
        return index

    def log2(self, x):
        y = 0
        while x > 1:
            x = x >> 1
            y = y + 1
        return y


def color_pixel(index):
    """Color the vertex by its index.
    """
    return max(index % 256, 1)


def pixels_hilbert(size):
    """Return the pixels of a 2d Hilbert curve.
    """
    h = Hilbert(2)
    for k in range(size * size):
        yield h.encode(k)


def hilbert(maze, render, pixels, speed=30):
    for i in range(len(pixels) - 1):
        maze.mark_cell(pixels[i], color_pixel(i))
        maze.mark_space(pixels[i], pixels[i + 1], color_pixel(i))
        if maze.num_changes >= speed:
            yield render(maze)

    maze.mark_cell(pixels[-1], color_pixel(len(pixels) - 1))
    if maze.num_changes > 0:
        yield render(maze)


order = 6
curve_size = (1 << order)
maze_size = 2 * curve_size + 1
cell_size = 4
margin = 6
image_size = cell_size * maze_size + 2 * margin

pixels = tuple(pixels_hilbert(curve_size))
colors = [0, 0, 0]
for i in range(255):
    rgb = hls_to_rgb((i / 360.0) % 1, 0.5, 1.0)
    colors += [int(round(255 * x)) for x in rgb]

surface = gm.GIFSurface(image_size, image_size, bg_color=0)
surface.set_palette(colors)
maze = gm.Maze(maze_size, maze_size, mask=None).scale(cell_size).translate((margin, margin))

anim = gm.Animation(surface)
anim.pause(100)
anim.run(hilbert, maze, speed=15, delay=5, pixels=pixels)
anim.pause(500)
surface.save("hilbert.gif")
surface.close()
