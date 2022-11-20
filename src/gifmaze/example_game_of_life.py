"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make gif animations of Conway's game of life
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For more patterns see

    "https://bitstorm.org/gameoflife/lexicon/"

:copyright (c) 2018 by Zhao Liang
"""
import os
import numpy as np
from tqdm import tqdm

from gifmaze import create_animation_for_size

cell_size = 5
lw = 1
margin = 4


def parse(filename):
    """Read data from a .cells file. Return a 2d array of live/dead cells.
    """
    seed = []
    with open(filename, "r") as f:
        # 1. convert symbols to 0 and 1
        for line in f.readlines():
            if line[0] == "!" or len(line) < 2:
                continue
            else:
                row = []
                for x in line:
                    if x == ".":
                        row.append(0)
                    if x == "O":
                        row.append(1)
                seed.append(row)

        # 2. make it a 2d rectangular array
        num_cols = max(len(row) for row in seed)
        for row in seed:
            if len(row) < num_cols:
                row.extend([0] * (num_cols - len(row)))

    # 3. rearrange the axis
    return [[seed[y][x] for y in range(len(seed))] for x in range(len(seed[0]))]


def evolve(grid):
    """Evolve the grid one step.
    """
    G = grid.astype(int)
    N = np.zeros_like(G)
    N[1:-1, 1:-1] = (
        G[:-2, :-2]
        + G[:-2, 1:-1]
        + G[:-2, 2:]
        + G[1:-1, :-2]
        + G[1:-1, 2:]
        + G[2:, :-2]
        + G[2:, 1:-1]
        + G[2:, 2:]
    )

    return np.logical_or(N == 3, np.logical_and(G == 1, N == 2))


def main(seed_file, grid_size, offsets, cutoff, frames):
    """
    :param seed_file: the pattern file.
    :param grid_size: (width, height) of the grid in the life world.
    :param offsets: (left, top) position of the initial pattern with
        respect to the grid.
    :param cutoff: cutoff of the image relative to the actual grid.
    :param frames: number of frames in the animation.
    """
    seed = np.array(parse(seed_file), dtype=np.bool)
    grid = np.zeros(grid_size).astype(np.bool)
    grid[
        offsets[0] : seed.shape[0] + offsets[0], offsets[1] : seed.shape[1] + offsets[1]
    ] = seed
    pattern_name = os.path.splitext(os.path.basename(seed_file))[0]

    ncols, nrows = grid_size
    maze, surface, anim = create_animation_for_size(
        ncols - 2 * cutoff, nrows - 2 * cutoff, cell_size, lw, margin, wall_init=1
    )
    surface.set_palette([0, 0, 0, 200, 200, 200, 255, 255, 255])

    def conway(maze, encode_func, grid, frames):
        bar = tqdm(total=frames, desc="Running the {} pattern".format(pattern_name))

        def copy(grid, maze):
            for x in range(cutoff, grid.shape[0] - cutoff):
                for y in range(cutoff, grid.shape[1] - cutoff):
                    maze.mark_cell((2 * (x - cutoff), 2 * (y - cutoff)), 2 + grid[x][y])

        for _ in range(frames):
            copy(grid, maze)
            yield encode_func(maze)
            grid = evolve(grid)
            bar.update(1)
        bar.close()

    anim.run(conway, maze, grid=grid, frames=frames, mcl=2,
             delay=10, cmap={0: 2, 3: 0})
    anim.pause(500)
    anim.save(pattern_name + ".gif")


if __name__ == "__main__":
    main(
        "./resources/Gosper_glider_gun.cells",
        grid_size=(54, 40),
        offsets=(4, 4),
        cutoff=3,
        frames=200,
    )
    main(
        "./resources/Enterprise.cells",
        grid_size=(80, 80),
        offsets=(50, 50),
        cutoff=15,
        frames=205,
    )
    main(
        "./resources/factory.cells",
        grid_size=(64, 40),
        offsets=(6, 6),
        cutoff=4,
        frames=400,
    )
    main(
        "./resources/filter.cells",
        grid_size=(60, 60),
        offsets=(14, 18),
        cutoff=4,
        frames=80,
    )
    main(
        "./resources/wasp.cells",
        grid_size=(42, 50),
        offsets=(10, 34),
        cutoff=8,
        frames=100,
    )
