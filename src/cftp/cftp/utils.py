"""
Helper functions for drawing figures.
"""
import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch


markersize = 14
labelsize = 11

sq3 = np.sqrt(3)
sq2 = np.sqrt(2)


def dir(angle_in_degree):
    """Return the unit complex cos(a) + i*sin(a).
    """
    theta = np.radians(angle_in_degree)
    return complex(np.cos(theta), np.sin(theta))


def plot_line(ax, points, *args, **kwargs):
    """Connect a list of complex points with piecewise line segments.
    """
    xli = [z.real for z in points]
    yli = [z.imag for z in points]
    return ax.plot(xli, yli, *args, **kwargs)


def draw_bounding_polygon(ax, vertices):
    """Draw the boundary of a polygon, given its vertices as a list
    of complex numbers.
    """
    coords = [(z.real, z.imag) for z in vertices]
    xli, yli = zip(*coords)
    ax.plot(xli, yli, "k-", lw=1)
    n = len(vertices)
    codes = [Path.MOVETO] + (n - 2) * [Path.LINETO] + [Path.CLOSEPOLY]
    patch = PathPatch(Path(coords, codes), facecolor="none", ec="k")
    ax.add_patch(patch)
    return patch


def draw_background_triangle_lattice(ax, dirs, N):
    """Draw the background triangle grids for lozenge tilings.

    :param ax: an instance of matplotlib's axes class.
    :param dirs: three grid directions of the triangle grids.
    :param N: how many lines we draw in each direction.
    """
    lines = []
    d = sq3 / 2
    for v in dirs:
        u = v * 1j
        for i in range(-N, N + 1):
            z1 = u * d * i - N * v
            z2 = u * d * i + N * v
            lines.extend(
                plot_line(ax, [z1, z2], "--", color="gray", lw=1)
            )
    return lines


def draw_marker(ax, z, label):
    plot_line(ax, [z, z], 'go', markersize=markersize)
    ax.text(z.real, z.imag, label, fontsize=labelsize,
            color="w", ha="center", va="center")


def draw_paths_on_hexagon(ax, XYZ, paths):
    """
    Draw the non-intersecting paths of a rhombus tiling on hexagon.

    :param ax: an instance of matplotlib's axes.
    :param XYZ: three directions of the triangle grids.
    :param paths: list of paths.
    """
    X, Y, Z = XYZ
    for i, path in enumerate(paths):
        start = (i - 0.5) * Y
        v1 = start
        draw_marker(ax, v1, str(path[0]))

        for ht1, ht2 in zip(path[:-1], path[1:]):
            if ht1 < ht2:
                v2 = v1 + Z
            else:
                v2 = v1 + X

            plot_line(ax, [v1, v2], "g-", lw=2)
            draw_marker(ax, v2, str(ht2))
            v1 = v2


def draw_paths_on_rectangle(ax, XYZ, paths):
    """
    Draw the non-intersecting paths of a domino tiling on rectangle.

    :param ax: an instance of matplotlib's axes.
    :param XYZ: X, Y for the usual xy-axis, Z for dir(45).
    :param paths: list of paths.
    """
    X, Y, Z = XYZ
    for i, path in enumerate(paths):
        start = -0.5 * Y if i == 0 else (2 * i - 1.5) * Y
        v1 = start
        draw_marker(ax, v1, str(path[0]))

        ind = 0
        while ind < len(path) - 1:
            ht1 = path[ind]
            ht2 = path[ind + 1]
            if ht1 < ht2:
                v2 = v1 + Z
                ind += 1
            elif ht1 == ht2:
                if 0 < i < len(paths) - 1:
                    v2 = v1 + 2 * X
                    ind += 2
                else:
                    v2 = v1 + X
                    ind += 1
            else:
                v2 = v1 + Z.conjugate()
                ind += 1

            plot_line(ax, [v1, v2], "g-", lw=2)
            draw_marker(ax, v2, str(ht2))
            v1 = v2


def draw_lozenge(ax, vertices, type):
    codes = [Path.MOVETO] + 3 * [Path.LINETO] + [Path.CLOSEPOLY]
    coords = [(x * sq3 / 2, y - x / 2) for x, y in vertices]
    coords.append(coords[0])

    if type == "T":
        color = (0.678, 0.847, 1)

    elif type == "L":
        color = (0.314, 0.188, 0.475)

    else:
        color = (1, 0.569, 0.459)

    patch = PathPatch(Path(coords, codes), facecolor=color, ec="k")
    ax.add_patch(patch)


def draw_domino(ax, vertices, type):
    codes = [Path.MOVETO] + 3 * [Path.LINETO] + [Path.CLOSEPOLY]
    coords = vertices
    coords.append(coords[0])

    if type == "v1":
        color = (0.433, 1, 0.76)

    elif type == "v2":
        color = (0.93, 0.8, 0.91)

    elif type == "h1":
        color = (1, 0.476, 0.56)

    else:
        color = (0.455, 0.64, 0.976)

    patch = PathPatch(Path(coords, codes), facecolor=color, ec="k")
    ax.add_patch(patch)
