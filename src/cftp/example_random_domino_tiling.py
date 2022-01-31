"""
Draw a random domino tiling and its non-intersecting lattice paths.
"""
import matplotlib.pyplot as plt
from cftp import DominoTiling
import cftp.utils as utils


def main(rect_size, figsize):
    T = DominoTiling(rect_size)
    paths = T.run()
    tiles = T.get_tiles(paths)
    X, Y, Z = utils.dir(0), utils.dir(90), utils.dir(45) * 2**0.5
    a, b = rect_size
    A = a * X
    B = b * Y
    verts = [0, A, A + B, B, 0]

    fig = plt.figure(figsize=figsize, dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], aspect=1)
    ax.axis([-1, a + 1, -1, b + 1])
    ax.axis("off")

    utils.draw_bounding_polygon(ax, verts)
    for key, li in tiles.items():
        for verts in li:
            utils.draw_domino(ax, verts, key)

    fig.savefig("random_domino_tiling.svg")

    utils.draw_paths_on_rectangle(ax, (X, Y, Z), paths)

    fig.savefig("non-intersecting_paths_domino.svg")


if __name__ == "__main__":
    main(rect_size=(20, 20), figsize=(8, 8))
