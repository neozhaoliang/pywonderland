"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Draw aperiodic tilings using de Bruijn's algebraic approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Reference:

  "Algebraic theory of Penrose's non-periodic tilings of the plane".
                                                     N.G. de Bruijn.

Some params you can tweak with:

    1. 'DIMENSION'.
    2. 'SHIFTS' of the grids.
    3. Colors for the different rhombus.

:copyright: by Zhao Liang, 2018.
"""
import itertools

import numpy as np

try:
    import cairocffi as cairo
except ImportError:
    import cairo


IMAGE_SIZE = (800, 800)
NUM_LINES = 12
PI = np.pi
DIMENSION = 5  # DIMENSION = 4 is the Ammann-Beenker tiling

if DIMENSION % 2 == 0:
    GRIDS = [np.exp(PI * 1j * i / DIMENSION) for i in range(DIMENSION)]
else:
    GRIDS = [np.exp(PI * 2j * i / DIMENSION) for i in range(DIMENSION)]

SHIFTS = [0.5] * 5  # you can use np.random.random(5) to draw a random pattern

FAT_COLOR = (0.894, 0.102, 0.11)
THIN_COLOR = (1.0, 0.5, 0.0)
EDGE_COLOR = (0.216, 0.494, 0.72)


def compute_rhombus(r, s, kr, ks):
    """
    Compute the coordinates of the four vertices of the rhombus that
    correspondes to the intersection point of the kr-th line in the r-th
    grid and the ks-th line in the s-th grid. Here r, s, kr, ks are all
    integers and 0 <= r < s <= DIMENSION and -NUM_LINES <= kr, ks <= NUM_LINES.

    The intersection point is the solution to a 2x2 linear equation:
        Re(z/grids[r]) + shifts[r] = kr
        Re(z/grids[s]) + shifts[s] = ks
    """
    # The intersection point
    intersect_point = (
        (GRIDS[r] * (ks - SHIFTS[s]) - GRIDS[s] * (kr - SHIFTS[r]))
        * 1j
        / GRIDS[s - r].imag
    )

    # the list of integers that indicate the position of the intersection point.
    # the i-th integer n_i indicates that this point lies in the n_i-th strip
    # in the i-th grid.
    index = [
        np.ceil((intersect_point / grid).real + shift)
        for grid, shift in zip(GRIDS, SHIFTS)
    ]

    # Be careful of the accuracy problem here.
    # Mathematically the r-th and s-th item of index should be kr and ks,
    # but programmingly it might not be the case,
    # so we have to manually set them to correct values.
    return [
        np.dot(index, GRIDS)
        for index[r], index[s] in [
            (kr, ks),
            (kr + 1, ks),
            (kr + 1, ks + 1),
            (kr, ks + 1),
        ]
    ]


surface = cairo.SVGSurface("debruijn.svg", IMAGE_SIZE[0], IMAGE_SIZE[1])
ctx = cairo.Context(surface)
ctx.set_line_cap(cairo.LINE_CAP_ROUND)
ctx.set_line_join(cairo.LINE_JOIN_ROUND)
ctx.set_line_width(0.1)
scale = max(IMAGE_SIZE) / (2.0 * NUM_LINES)
ctx.scale(scale, scale)
ctx.translate(NUM_LINES, NUM_LINES)


for r, s in itertools.combinations(range(DIMENSION), 2):
    for kr, ks in itertools.product(range(-NUM_LINES, NUM_LINES), repeat=2):
        if s - r == 1 or s - r == DIMENSION - 1:
            color = FAT_COLOR
            shape = 0
        else:
            color = THIN_COLOR
            shape = 1

        ctx.set_source_rgb(*color)
        A, B, C, D = compute_rhombus(r, s, kr, ks)
        ctx.move_to(A.real, A.imag)
        ctx.line_to(B.real, B.imag)
        ctx.line_to(C.real, C.imag)
        ctx.line_to(D.real, D.imag)
        ctx.close_path()
        ctx.fill_preserve()

        ctx.set_source_rgb(*EDGE_COLOR)
        ctx.stroke()

surface.finish()

try:
    import subprocess

    subprocess.call(
        "convert debruijn.svg +shade 20x20 -modulate 250 debruijn.png", shell=True
    )
except ImportError:
    print("Add shading effect to image failed, `convert` command not found")
