"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Sample a random domino tiling of an Aztec diamond
with uniform probability.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright (c) 2015 by Zhao Liang.
"""
import argparse
from tqdm import trange
import aztec


# Four colors for the four types of dominoes
N_COLOR = (1, 0, 0)
S_COLOR = (0.75, 0.75, 0)
W_COLOR = (0, 0.5, 0)
E_COLOR = (0, 0, 1)


def render_with_cairo(az, imgsize, extent, filename):
    """
    Draw current tiling of an Aztec diamond `az` (possibly have holes) to a
    png image with cairo.

    :param az: an instance of the AztecDiamond class.
    :param imgsize: image size in pixels, e.g. size = 600 means 600x600.
    :param extent: range of the axis: [-extent, extent] x [-extent, extent]
    :param filename: output filename, must be a .png image.
    """
    try:
        import cairocffi as cairo
    except ImportError:
        import cairo

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, imgsize, imgsize)
    surface.set_fallback_resolution(100, 100)
    ctx = cairo.Context(surface)
    ctx.scale(imgsize / (2.0 * extent), -imgsize / (2.0 * extent))
    ctx.translate(extent, -extent)

    ctx.set_source_rgb(1, 1, 1)
    ctx.paint()

    margin = 0.1

    for (i, j) in az.cells:
        if az.is_black(i, j) and az.tile[(i, j)] is not None:
            if az.tile[(i, j)] == "n":
                ctx.rectangle(
                    i - 1 + margin, j + margin, 2 - 2 * margin, 1 - 2 * margin
                )
                ctx.set_source_rgb(*N_COLOR)

            if az.tile[(i, j)] == "s":
                ctx.rectangle(i + margin, j + margin, 2 - 2 * margin, 1 - 2 * margin)
                ctx.set_source_rgb(*S_COLOR)

            if az.tile[(i, j)] == "w":
                ctx.rectangle(i + margin, j + margin, 1 - 2 * margin, 2 - 2 * margin)
                ctx.set_source_rgb(*W_COLOR)

            if az.tile[(i, j)] == "e":
                ctx.rectangle(
                    i + margin, j - 1 + margin, 1 - 2 * margin, 2 - 2 * margin
                )
                ctx.set_source_rgb(*E_COLOR)

            ctx.fill()

    surface.write_to_png(filename)


def render_with_matplotlib(az, imgsize, extent, filename):
    """
    Draw current tiling of `az` to a png image with matplotlib.
    Matplotlib is slower than cairo but it gives optimized results.
    The inputs are the same with those in `render_with_cairo`.
    """
    import matplotlib.patches as mps
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(imgsize / 100.0, imgsize / 100.0), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], aspect=1)
    ax.axis([-extent, extent, -extent, extent])
    ax.axis("off")
    linewidth = fig.dpi * fig.get_figwidth() / (20.0 * extent)

    for i, j in az.cells:
        if az.is_black(i, j) and az.tile[(i, j)] is not None:
            if az.tile[(i, j)] == "n":
                p = mps.Rectangle((i - 1, j), 2, 1, fc=N_COLOR)
            if az.tile[(i, j)] == "s":
                p = mps.Rectangle((i, j), 2, 1, fc=S_COLOR)
            if az.tile[(i, j)] == "w":
                p = mps.Rectangle((i, j), 1, 2, fc=W_COLOR)
            if az.tile[(i, j)] == "e":
                p = mps.Rectangle((i, j - 1), 1, 2, fc=E_COLOR)

            p.set_linewidth(linewidth)
            p.set_edgecolor("w")
            ax.add_patch(p)

    fig.savefig(filename)


def render(program, *args, **kwargs):
    """
    :param program: must be either cairo or matplotlib.
    """
    if program == "cairo":
        render_with_cairo(*args, **kwargs)
    elif program == "matplotlib":
        render_with_matplotlib(*args, **kwargs)
    else:
        raise ValueError("Program must be cairo or matplotlib!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-size", metavar="s", type=int, default=800, help="image size")
    parser.add_argument(
        "-order", metavar="o", type=int, default=60, help="order of az graph"
    )
    parser.add_argument(
        "-filename",
        metavar="f",
        type=str,
        default="random_tiling.png",
        help="output filename",
    )
    parser.add_argument(
        "-prog",
        metavar="p",
        type=str,
        default="cairo",
        help="program to draw the tiling",
    )
    args = parser.parse_args()

    az = aztec.AztecDiamond(0)
    for _ in trange(args.order):
        az = az.delete().slide().create()

    render(args.prog, az, args.size, az.order + 1, args.filename)
