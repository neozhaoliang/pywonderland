"""
This script employs integer linear programming to find all solutions
to the IQ Puzzler Pro by SmartGames:

    https://www.smartgames.eu/uk/one-player-games/iq-puzzler-pro-0

The goal is to fill an 11x5 board using 12 distinct pieces.

For each piece and its possible placement on the board, we assign a binary variable x_i
(which can only take values 0 or 1). In total, there are 2140 binary variables.

For every cell on the board, we generate a linear equation ensuring that the sum of the
variables covering it equals 1, meaning each cell is covered exactly once.

Since each piece can be used only once, we require the sum of the variables corresponding to
the placements of any individual piece to be 1. This results in 12 additional equations.

We use the `pulp` library to solve the system of equations and find all possible solutions.
Solutions that are reflections or central inversions of previously found ones are discarded.
"""

import os
import numpy as np
import matplotlib.pyplot as plt

try:
    import pulp
    from pulp.apis import PULP_CBC_CMD
except ImportError:
    raise ("please run `pip install pulp` to install")

try:
    from shapely.geometry import Point, box
    from shapely.ops import unary_union
    from shapely.plotting import plot_polygon
except ImportError:
    raise ("please run `pip install shapely` to install")


board_width = 11
board_height = 5
shaft_width = 0.2

current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, "solutions")
os.makedirs(output_dir, exist_ok=True)
solutions_data_file = os.path.join(output_dir, "solutions.txt")


class Piece:
    """
    A class to represent a piece used in the IQ Puzzler Pro game.
    It computes the piece's variants (after reflection and rotation) and
    its valid placements on the board.
    """

    def __init__(self, data):
        self.variants = self.get_variants(data)
        self.placements = []

    def get_variants(self, data):
        """
        Generates all unique variants of the piece by applying reflection and rotation.

        Args:
            data (np.ndarray): 2D array representing the initial layout of the piece.

        Returns:
            list of np.ndarray: List of unique piece variants after transformations.
        """
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
                        self.placements.append(current_placement)

        return self.placements


pink = Piece([[1, 1, 0, 0], [0, 1, 1, 1]])
cyan = Piece([[1, 1, 1], [1, 1, 0]])
orange = Piece([[1, 0, 0], [1, 1, 1], [0, 1, 0]])
purple = Piece([[1, 1, 0], [0, 1, 1], [0, 0, 1]])
yellow = Piece([[1, 1, 1, 1], [0, 1, 0, 0]])
crimson = Piece([[1, 1, 0], [0, 1, 1]])
green = Piece([[1, 1, 1], [0, 1, 0]])
blue = Piece([[1, 1, 1], [1, 0, 0], [1, 0, 0]])
red = Piece([[1, 1, 1, 1], [1, 0, 0, 0]])
olive = Piece([[1, 1, 1], [1, 0, 1]])
darkBlue = Piece([[1, 1, 1], [1, 0, 0]])
skyblue = Piece([[1, 1], [1, 0]])


pieces = [
    pink, cyan, orange, purple, yellow, crimson,
    green, blue, red, olive, darkBlue, skyblue
]

colors = [
    "pink", "cyan", "orange", "purple", "yellow", "crimson",
    "green", "blue", "red", "olive", "darkblue", "skyblue"
]


def get_piece_prototype_index(intervals, k):
    """
    Retrieves the prototype index for a given piece placement based on its index.
    """
    for i, (start, end) in enumerate(intervals):
        if start <= k < end:
            return i


def get_board_configuration(solution):
    """
    Converts a binary solution vector into a 2D matrix representing the board configuration.

    Args:
        solution (list of int): A binary vector where each entry indicates if a piece is used at a given placement.

    Returns:
        np.ndarray: A matrix representing the board state, with each cell containing the index of the piece.
    """
    global all_placements, intervals
    mat = np.zeros((board_height, board_width), dtype=int)
    for ind, val in enumerate(solution):
        if val != 0:
            piece = all_placements[ind]
            proto_index = get_piece_prototype_index(intervals, ind)
            for i, j in piece:
                mat[j, i] = proto_index
    return mat


def is_duplicate(existing_matrices, candidate_matrix):
    """Check if a matrix is a duplicate (including rotations and reflections) of existing ones."""
    transforms = [
        candidate_matrix,
        np.fliplr(candidate_matrix),
        np.flipud(candidate_matrix),
        np.flipud(np.fliplr(candidate_matrix))
    ]
    return any(np.array_equal(existing, M) for existing in existing_matrices for M in transforms)


def save_solution(output_file, mat, index):
    """
    Saves the current solution matrix to a file.

    Args:
        output_file (str): The file path where the solution should be saved.
        mat (np.ndarray): The matrix representing the solution.
    """
    with open(output_file, "a") as f:
        f.write(f"# solution {index}:\n")
        for row in mat:
            f.write(" ".join(f"{element:>2}" for element in row) + "\n")
        f.write("\n")


def plot_solution(solution, file_path):
    """Plots the solution to a SVG file."""
    global all_placements
    plt.gca().clear()
    plt.gca().axis([-0.5, board_width - 0.5, -0.5, board_height - 0.5])
    plt.gca().axis("off")
    plt.gca().set_aspect("equal")
    for ind, val in enumerate(solution):
        if val != 0:
            piece = all_placements[ind]
            proto_index = get_piece_prototype_index(intervals, ind)
            shapes = []
            for k in range(len(piece)):
                A = piece[k]
                for j in range(k + 1, len(piece)):
                    B = piece[j]
                    x1, y1 = A
                    x2, y2 = B
                    if abs(x1 - x2) == 1 and y1 == y2 or abs(y1 - y2) == 1 and x1 == x2:
                        width = abs(x2 - x1) or shaft_width
                        height = abs(y2 - y1) or shaft_width
                        lower_left_x = min(x1, x2) - shaft_width / 2
                        lower_left_y = min(y1, y2) - shaft_width / 2
                        upper_right_x = lower_left_x + width
                        upper_right_y = lower_left_y + height
                        b = box(
                            lower_left_x, lower_left_y, upper_right_x, upper_right_y
                        )
                        shapes.append(b)
            for i, j in piece:
                shapes.append(Point(i, j).buffer(0.35))

            merged_shape = unary_union(shapes)
            plot_polygon(
                merged_shape,
                ax=plt.gca(),
                facecolor=colors[proto_index],
                edgecolor="k",
                add_points=False,
                linewidth=2
            )

    plt.savefig(file_path, bbox_inches="tight")


# A long list contains all 2140 placements of the 12 pieces
all_placements = []

# Save the starting and ending positions of the placements for each piece in the
# `all_placements`list. This way, we can determine the prototype piece by the index
# of a piece in `all_placements`
intervals = []
for piece in pieces:
    start = len(all_placements)
    all_placements += piece.get_all_placements(board_width, board_height)
    end = len(all_placements)
    intervals.append((start, end))

# One variable for each placement
nvars = len(all_placements)
# One equation of each cell
neqs = board_width * board_height
A = np.zeros((neqs, nvars))
for i, piece in enumerate(all_placements):
    for col, row in piece:
        A[col + row * board_width, i] = 1

prob = pulp.LpProblem("Integer_LP", pulp.LpMinimize)
x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(nvars)]
# each cell is covered exactly once
# Ax = 1 (column vector of all 1's)
for i in range(neqs):
    prob += pulp.lpSum(A[i, j] * x[j] for j in range(nvars)) == 1
# each piece is used only once
for start, end in intervals:
    prob += pulp.lpSum(x[i] for i in range(start, end)) == 1

# store the matrix representation of all solutions found so far (excluding global symmetry)
matrices_found = []
while True:
    prob.solve(PULP_CBC_CMD(msg=False))

    if pulp.LpStatus[prob.status] != "Optimal":
        print(f"No more solutions. Status: {pulp.LpStatus[prob.status]}")
        break

    current_solution = np.array([int(pulp.value(x[i])) for i in range(nvars)])
    mat = get_board_configuration(current_solution)
    if not is_duplicate(matrices_found, mat):
        matrices_found.append(mat)
        N = len(matrices_found)
        print(f"{N} solutions found...", end="\r")
        plot_solution(
            current_solution, os.path.join(output_dir, f"solution-{N:03d}.svg")
        )
        save_solution(solutions_data_file, mat, N)

    # exclude current solution in future search
    prob += (
        pulp.lpSum(
            (1 - current_solution[i]) * x[i] + current_solution[i] * (1 - x[i])
            for i in range(nvars)
        )
        >= 1
    )
