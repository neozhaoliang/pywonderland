import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from .palette import palette
from .vector import Vec2
from .transform import triangle_to_cartesian, D2, D3
from .marker import Marker

sq3 = 3**0.5


SQUARE = [Vec2(0, 0), Vec2(1, 0), Vec2(1, 1), Vec2(0, 1)]
TRIANGLE = [Vec2(0, 0), Vec2(1, 0), Vec2(0.5, sq3 / 2)]
TRIANGLE_FLIP = [Vec2(0, 0), Vec2(0.5, sq3 / 2), Vec2(-0.5, sq3 / 2)]
HEXAGON = [
    Vec2(0, 0),
    Vec2(1, 0),
    Vec2(1.5, sq3 / 2),
    Vec2(1, sq3),
    Vec2(0, sq3),
    Vec2(-0.5, sq3 / 2),
]
HEXAGON_CENTER = sum(HEXAGON) / 6


def plot_square(xy, type, **kwargs):
    vertices = [v + xy for v in SQUARE]
    color = palette[type]
    poly = Polygon(vertices, closed=True, color=color, ec="k", lw=1)
    plt.gca().add_patch(poly)
    if kwargs.get("marker", False):
        Marker().transform_by_group_element(D2[type]).translate(
            Vec2(xy.x + 0.5, xy.y + 0.5)
        ).plot("k", lw=0.8)


def plot_triangle(xy, type, **kwargs):
    if type % 2 == 0:
        vertices = [v + xy for v in TRIANGLE]
    else:
        vertices = [v + xy for v in TRIANGLE_FLIP]
    color = palette[type]
    poly = Polygon(vertices, closed=True, color=color, ec="k", lw=1)
    plt.gca().add_patch(poly)

    if kwargs.get("marker", False):
        marker = Marker().scale(0.8).transform_by_group_element(D3[type])
        if type % 2 == 0:
            marker.translate(Vec2(xy.x + 0.5, xy.y + 0.5 / sq3))
        else:
            marker.translate(Vec2(xy.x, xy.y + 1 / sq3))
        marker.plot("k", lw=0.8)


def plot_hexagon(xy, **kwargs):
    vertices = [v + xy for v in HEXAGON]
    center = sum(vertices) / 6
    for i in range(6):
        tri = Polygon(
            [center, vertices[i], vertices[(i + 1) % 6]],
            closed=True,
            lw=0,
            color=palette[i],
        )
        plt.gca().add_patch(tri)
        if kwargs.get("marker", False):
            Marker().scale(0.8).transform_by_group_element(D3[i]).translate(
                (center + vertices[i] + vertices[(i + 1) % 6]) / 3
            ).plot("k", lw=0.8)
    poly = Polygon(vertices, closed=True, color="none", ec="k", lw=1)
    plt.gca().add_patch(poly)


def plot_square_tiling(imin, imax, jmin, jmax, **kwargs):
    for i in range(imin, imax):
        for j in range(jmin, jmax):
            xy = Vec2(i, j)
            k = (i % 2, j % 2)
            if k == (0, 0):
                type = 0
            if k == (1, 0):
                type = 1
            if k == (0, 1):
                type = 3
            if k == (1, 1):
                type = 2
            plot_square(xy, type, **kwargs)


def plot_triangle_tiling(imin, imax, jmin, jmax, **kwargs):
    for i in range(imin, imax):
        for j in range(jmin, jmax):
            xy = triangle_to_cartesian(i, j)
            k = (i - j) % 3
            if k == 0:
                type1, type2 = 0, 1
            elif k == 1:
                type1, type2 = 4, 3
            else:
                type1, type2 = 2, 5

            plot_triangle(xy, type1, **kwargs)
            plot_triangle(xy, type2, **kwargs)


def plot_hexagon_tiling(imin, imax, jmin, jmax, **kwargs):
    for i in range(imin, imax):
        for j in range(jmin, jmax):
            xy = triangle_to_cartesian(i, j)
            if (i - j) % 3 == 0:
                plot_hexagon(xy, **kwargs)
