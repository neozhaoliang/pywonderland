"""
This script utilizes Knuth's Dancing Links X (DLX) algorithm to find all solutions 
for the IQ Puzzler Pro puzzle by SmartGames:

    https://www.smartgames.eu/uk/one-player-games/iq-puzzler-pro-0

The goal is to tile an 11x5 board using 12 unique pieces.

The total number of solutions (excluding those symmetric under horizontal or vertical reflections) is 1082785.

The DLX implementation is borrowed from:

    https://www.cs.mcgill.ca/~aassaf9/python/algorithm_x.html
"""

import os
from collections import defaultdict
from itertools import combinations, chain
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Shadow

try:
    from shapely.geometry import Point, box
    from shapely.ops import unary_union
    from shapely.plotting import plot_polygon
except ImportError:
    raise ("please run `pip install shapely` to install")


board_width = 11
board_height = 5

# save output solutions
current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, "solutions")
os.makedirs(output_dir, exist_ok=True)

# for drawing figures
shaft_width = 0.2
shadow_offset = (0.1, -0.1)


class Piece:
    """
    A class to represent a piece used in the IQ Puzzler Pro game.
    It computes the piece's variants (after reflection and rotation) and
    its valid placements on the board.
    """

    def __init__(self, name, data, freeze=False):
        self.name = name
        self.variants = self.get_variants(data, freeze)
        self.placements = []

    def get_variants(self, data, freeze):
        """
        Generates all unique variants of the piece by applying reflection and rotation.

        Args:
            data (np.ndarray): 2D array representing the initial layout of the piece.

        Returns:
            list of np.ndarray: List of unique piece variants after transformations.
        """
        if freeze:
            return [np.array(data)]

        variants = []
        for piece in [data, np.fliplr(data)]:
            for k in range(4):
                candidate = np.rot90(piece, k)
                for existing in variants:
                    if np.array_equal(existing, candidate):
                        break  # candidate is equal to existing
                else:
                    variants.append(candidate)
        return variants

    def get_all_placements(self, board_width, board_height):
        """Finds all valid placements of the piece on the board."""
        self.placements = []
        for piece in self.variants:
            indices = np.where(piece != 0)
            coords = tuple(zip(*indices))
            for x in range(board_width):
                for y in range(board_height):
                    current_placement = [(x + dx, y + dy) for dx, dy in coords]
                    if all(
                        0 <= cx < board_width and 0 <= cy < board_height
                        for cx, cy in current_placement
                    ):
                        # Add a virtual cell that is covered by all placements of this piece to
                        # ensure the piece is used exactly once. The name of the virtual cell is
                        # not critical, as long as it is hashable and unique for each piece.
                        # In total, there are 12 virtual cells, one for each piece.
                        current_placement.append(self.name)
                        self.placements.append(current_placement)

        return self.placements


# fmt:off

# By restricting the blue piece to a single orientation, we eliminate redundant 
# solutions that are equivalent under horizontal or vertical reflections. 
# The blue piece is special in that all its possible orientations can be obtained 
# by applying horizontal and vertical reflections. You can also use the 'green' or
# 'skyblue' piece instead.
blue = Piece("blue", 
    [[1, 1, 1],
     [1, 0, 0],
     [1, 0, 0]], freeze=True
)

pink = Piece("pink", 
    [[1, 1, 0, 0],
     [0, 1, 1, 1]]
)

cyan = Piece("cyan", 
    [[1, 1, 1],
     [1, 1, 0]]
)

orange = Piece("orange",
    [[1, 0, 0],
     [1, 1, 1],
     [0, 1, 0]]
)

purple = Piece("purple", 
    [[1, 1, 0],
     [0, 1, 1],
     [0, 0, 1]]
)

yellow = Piece("yellow", 
    [[1, 1, 1, 1],
     [0, 1, 0, 0]]
)

crimson = Piece("crimson",
    [[1, 1, 0],
     [0, 1, 1]]
)

green = Piece("green", 
    [[1, 1, 1],
     [0, 1, 0]]
)

red = Piece("red",
    [[1, 1, 1, 1],
     [1, 0, 0, 0]]
)

olive = Piece("olive",
    [[1, 1, 1],
     [1, 0, 1]]
)

darkBlue = Piece("darkblue",
    [[1, 1, 1],
     [1, 0, 0]]
)

skyblue = Piece("skyblue",
    [[1, 1],
     [1, 0]]
)


pieces = [
    pink, cyan, orange, purple, yellow, crimson,
    green, blue, red, olive, darkBlue, skyblue
]

# fmt:on

# The `X`, `Y` dicts and the `solve`, `select`, `dselect` function follow from
# https://www.cs.mcgill.ca/~aassaf9/python/algorithm_x.html
# but with some modifications: we can directly use the list `all_placements` for `Y`.
# This list is never changed throughout the whole process.
all_placements = list(
    chain(*(piece.get_all_placements(board_width, board_height) for piece in pieces))
)
X = defaultdict(set)
for i, cells in enumerate(all_placements):
    for cell in cells:
        X[cell].add(i)


def solve(X, solution=[]):
    if not X:
        yield solution
    else:
        for row in list(min(X.values(), key=len)):
            solution.append(row)
            cols = select(X, row)
            for s in solve(X, solution):
                yield s
            deselect(X, row, cols)
            solution.pop()


def select(X, row):
    cols = []
    # Find all columns covered by this placement
    for col in all_placements[row]:
        # remove other rows that conflict with the selected one 
        for other_rows in X[col]:
            for k in all_placements[other_rows]:
                if k != col:
                    X[k].remove(other_rows)
        cols.append(X.pop(col))
    return cols


def deselect(X, row, cols):
    for j in reversed(all_placements[row]):
        X[j] = cols.pop()
        for i in X[j]:
            for k in all_placements[i]:
                if k != j:
                    X[k].add(i)


def plot_solution(solution, filename):
    """Plots the solution to a SVG file."""
    ax = plt.gca()
    ax.clear()
    ax.axis([-0.5, board_width - 0.5, -0.5, board_height - 0.5])
    ax.axis("off")
    ax.set_aspect("equal")
    ax.set_facecolor("lightgray")
    ax.patch.set_edgecolor("black")
    ax.patch.set_linewidth(3)
    for ind in solution:
        piece_with_name = all_placements[ind]
        cells = piece_with_name[:-1]
        name = piece_with_name[-1]
        shapes = []
        for A, B in combinations(cells, 2):  # check cells adjacency
            x1, y1 = A
            x2, y2 = B
            if abs(x1 - x2) == 1 and y1 == y2 or abs(y1 - y2) == 1 and x1 == x2:
                width = abs(x2 - x1) or shaft_width
                height = abs(y2 - y1) or shaft_width
                lower_left_x = min(x1, x2) - shaft_width / 2
                lower_left_y = min(y1, y2) - shaft_width / 2
                upper_right_x = lower_left_x + width
                upper_right_y = lower_left_y + height
                b = box(lower_left_x, lower_left_y, upper_right_x, upper_right_y)
                shapes.append(b)
        for i, j in cells:
            shapes.append(Point(i, j).buffer(0.35))

        merged_shape = unary_union(shapes)
        patch = plot_polygon(
            merged_shape,
            ax=plt.gca(),
            facecolor=name,  # piece name is a valid color
            edgecolor="k",
            add_points=False,
            linewidth=2,
        )
        shadow = Shadow(patch, *shadow_offset, fc="gray", ec="none", lw=0, zorder=-1)
        ax.add_artist(shadow)

    plt.gcf().patch.set_linewidth(4)
    plt.gcf().patch.set_edgecolor("black")
    plt.savefig(os.path.join(output_dir, filename), bbox_inches="tight")


for count, solution in enumerate(solve(X, []), start=1):
    print(f"found {count} solutions", end="\r")
    # I assume you don't want to plot all one million solutions
    if count <= 100:
        plot_solution(solution, f"solution-{count:06d}.svg")

print(f"total number of solutions: {count}")
