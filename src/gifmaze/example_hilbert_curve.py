"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Hilbert curve animation based on Gray code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on code at

"https://possiblywrong.wordpress.com/2014/04/18/allrgb-hilbert-curves-and-random-spanning-trees/"

:copyright (c) 2018 by Zhao Liang
"""
from colorsys import hls_to_rgb

from gifmaze import create_animation_for_size


class Hilbert:

    """
    Multi-dimensional Hilbert space-filling curve.
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
        while index:
            index, digit = divmod(index, self.mask + 1)
            digits.append(digit)

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
        return tuple(2 * x for x in coords)

    def decode(self, coords):
        """Convert coordinates to index of a point on the Hilbert curve.
        """
        # Convert n m-bit coordinates to m base-n digits.
        coords = list(coords)
        m = self.log2(max(coords)) + 1
        digits = []
        for _ in range(m):
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
    """
    Color the vertex by its index. Note the color index must lie between
    0-255 since gif allows at most 256 colors in the global color table.
    """
    return max(index % 256, 1)


def pixels_hilbert(size):
    """Generate the pixels of a 2d Hilbert curve.
    """
    h = Hilbert(2)  # 2d curve
    for k in range(size * size):
        yield h.encode(k)


def hilbert(maze, encode_func, pixels, speed=30):
    """We just traverse the curve and color the pixels along the way.
    """
    for i in range(len(pixels) - 1):
        maze.mark_cell(pixels[i], color_pixel(i))
        maze.mark_space(pixels[i], pixels[i + 1], color_pixel(i))
        if i % speed == 0:
            yield encode_func(maze)

    maze.mark_cell(pixels[-1], color_pixel(len(pixels) - 1))
    yield encode_func(maze)


order = 6
curve_size = 1 << order
cell_size = 4
lw = 4
margin = 6

pixels = tuple(pixels_hilbert(curve_size))

maze, surface, anim = create_animation_for_size(
    curve_size, curve_size, cell_size, lw, margin
)
colors = [0, 0, 0]
for i in range(1, 256):
    rgb = hls_to_rgb(i / 256.0, 0.5, 1.0)
    colors += [int(round(255 * x)) for x in rgb]
surface.set_palette(colors)

anim.pause(100)
anim.run(hilbert, maze, speed=5, delay=5, pixels=pixels)
anim.pause(500)
anim.save("hilbert_curve.gif")
