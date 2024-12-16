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
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


IMAGE_SIZE = (800, 800)
NUM_LINES = 12
PI = np.pi
DIMENSION = 5  # DIMENSION = 4 is the Ammann-Beenker tiling
if DIMENSION % 2 == 0:
    theta = np.pi * np.arange(DIMENSION) / DIMENSION
else:
    theta = 2 * np.pi * np.arange(DIMENSION) / DIMENSION

uv = np.column_stack((np.cos(theta), np.sin(theta)))
SHIFTS = [0.5] * DIMENSION  # np.random.random(DIMENSION) for a random pattern

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

        | uv[r][0]  uv[r][1] |   | x |   | shifts[r] |   | kr |
        |                    | @ |   | + |           | = |    |
        | uv[s][0]  uv[s][1] |   | y |   | shifts[s] |   | ks |
    """
    M = uv[[r, s], :]
    # The (x, y) coordinates of the intersection point
    intersect_point = np.linalg.solve(M, [kr - SHIFTS[r], ks - SHIFTS[s]])
    # Compute the list of integers representing the positions of the intersection points.
    # Specifically, the i-th integer n_i indicates that the point lies in the n_i-th strip
    # within the i-th grid.
    index = np.ceil(uv @ intersect_point + SHIFTS).astype(int)

    # Note: Accuracy issues may arise here due to floating-point precision.
    # Mathematically, the r-th and s-th elements of `index` should be `kr` and `ks`,
    # respectively. However, due to potential computational inaccuracies, 
    # we need to manually set these values to ensure correctness.
    return [
        np.dot(index, uv)
        for index[r], index[s] in [
            (kr, ks),
            (kr + 1, ks),
            (kr + 1, ks + 1),
            (kr, ks + 1),
        ]
    ]


xmin, xmax = -12, 12
ymin, ymax = -8, 8
ax = plt.gca()
ax.axis("off")
ax.axis([xmin, xmax, ymin, ymax])
ax.set_aspect("equal")


for r, s in itertools.combinations(range(DIMENSION), repeat=2):
    for kr, ks in itertools.product(range(-NUM_LINES, NUM_LINES), repeat=2):
        if s - r == 1 or s - r == DIMENSION - 1:
            color = FAT_COLOR
            shape = 0
        else:
            color = THIN_COLOR
            shape = 1

        vertices = compute_rhombus(r, s, kr, ks)
        poly = Polygon(vertices, closed=True, fc=color, ec=EDGE_COLOR, lw=1)
        ax.add_patch(poly)

plt.savefig("debruijn.svg", bbox_inches="tight")

try:
    import subprocess

    subprocess.call(
        "convert debruijn.svg +shade 20x20 -modulate 250 debruijn.png", shell=True
    )
except ImportError:
    print("Add shading effect to image failed, `convert` command not found")
