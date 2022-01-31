"""
Draw a random lozenge tiling and its non-intersecting lattice paths
"""
import matplotlib.pyplot as plt
from cftp import LozengeTiling
import cftp.utils as utils


def main(hexagon_size, figsize):
    T = LozengeTiling(hexagon_size)
    paths = T.run()
    tiles = T.get_tiles(paths)

    X, Y, Z = utils.dir(-30), utils.dir(90), utils.dir(30)
    a, b, c = hexagon_size

    # six vertices of the hexagon
    A = a * X
    B = c * Y
    C = b * Z
    verts = [0, A, A + C, A + B + C, B + C, B, 0]
    N = sum(hexagon_size)

    xmin = -1
    xmax = a * X.real + b * Z.real + 1
    ymin = a * X.imag - 1
    ymax = b * Z.imag + c + 1
    fig = plt.figure(figsize=figsize, dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], aspect=1)
    ax.axis([xmin, xmax, ymin, ymax])
    ax.axis("off")

    patch = utils.draw_bounding_polygon(ax, verts)
    lines = utils.draw_background_triangle_lattice(
        ax, (X, Y, Z), N
    )
    for line in lines:
        line.set_clip_path(patch)

    # add text annotations
    fs = 20
    z = B + C + A / 2
    ax.text(z.real + 0.5, z.imag + 0.8, "$a$", fontsize=fs)
    z = B + C / 2
    ax.text(z.real - 0.8, z.imag + 0.7, "$b$", fontsize=fs)
    z = B / 2
    ax.text(z.real - 1, z.imag, "$c$", fontsize=fs)

    # draw the background hexagon
    fig.savefig("hexagon.png")

    # remove background grid lines
    for line in lines:
        line.remove()

    # draw the random lozenge tiling
    for key, li in tiles.items():
        for verts in li:
            utils.draw_lozenge(ax, verts, key)

    fig.savefig("random_lozenge_tiling.svg")

    # draw the non-intersecting path system
    utils.draw_paths_on_hexagon(ax, (X, Y, Z), paths)

    fig.savefig("non-intersecting_paths_lozenge.svg")


if __name__ == "__main__":
    main(hexagon_size=(10, 10, 10), figsize=(8, 8))
