"""
Penrose Cooling Process

This script draws a rhombus tiling with a mix of chaotic and quasicrystal patterns 
by applying different types of flips to distinct regions of a generalized Penrose tiling.

Learned from Thomas Fernique:
Gallery: https://lipn.univ-paris13.fr/~fernique/gallery.html#penrose1
Slides (Part 3): https://lipn.univ-paris13.fr/~fernique/info/bielefeld.pdf

My further explanation of the process:

1. We generate a generalized Penrose tiling using de Bruijn's grid method, storing all vertices and 
   their connections.
2. Each vertex `v` can have neighbors in 10 possible directions, spaced 36 degrees apart 
   in a circular arrangement. Not all vertices have 10 neighbors, but any neighbor must 
   lie in one of these directions.

            0
         9     1
       8         2
       7         3
         6     4
            5

3. Rhombuses in the generalized Penrose tiling satisfy the alternation condition (AC). For a 
   fat rhombus, fixing a pair of parallel edges defines a strip; within this strip, the next 
   fat rhombus encountered on either side must be symmetric (not translated) relative to 
   the first. The same applies to thin rhombuses. Note that tiles on the boundary of the tiling 
   may not satisfy the AC due to the finite size of the tiling region.
4. At a flippable vertex (where a flip is possible), exactly two fat rhombuses and one thin 
   rhombus, or one fat rhombus and two thin rhombuses, meet. The two rhombuses with the same
   shape (e.g. both fat or both thin) are symmetric, so they look TTˉ. By searching along either side,
   flips can be categorized as good, neutral, or bad (see Thomas’s slides, pages 34–35).
5. We apply two rounds of flips to the tiling. In the first round, the left 3/4 part is randomly flipped, 
   resulting in a chaotic state. In the second round, only good or neutral flips are applied to the same
   3/4 region, with the flipping probability gradually increasing from left to right. This process
   transitions the image from chaos to a quasicrystal pattern.
"""

import numpy as np
import itertools
from typing import Dict, Union
import random
import tqdm
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from sortedcontainers import SortedDict
from loguru import logger


# number of lines in each grid family
LINE_RANGE = 50

# Draw the tiling within the rectangular region defined by
# (-bbox[0], bbox[0]) × (-bbox[1], bbox[1])
bbox = (120, 30)
plt.gcf().set_size_inches(*bbox)

# Directions of the five grids in 2D space
theta = 2 * np.pi * np.arange(5) / 5
uv = np.column_stack((np.cos(theta), np.sin(theta)))

FAT_COLOR = "lightskyblue"
THIN_COLOR = "orangered"
EDGE_COLOR = "black"


def get_probability_round_one(x):
    """Return a triple of probabilities for flipping good/neutral/bad vertices"""
    w = bbox[0]
    a = (x + w) / (2 * w)
    if a < 3 / 4:
        return [1 - a, 1, 1]
    else:
        return [0, 0, 0]


def get_probability_round_two(x):
    """Return a triple of probabilities for flipping good/neutral/bad vertices"""
    w = bbox[0]
    a = (x + w) / (2 * w)
    if a < 3 / 4:
        return [0, a * 4 / 3, a * 4 / 3]
    else:
        return [0, 0, 0]


def opposite(e: int):
    """Return the opposite edge of e."""
    return (e + 5) % 10


class Vertex:

    def __init__(self, coords):
        self.coords = np.array(coords, dtype=int)
        self.edges = SortedDict()
        self.is_free = True

    def __str__(self):
        data = ", ".join(self.coords)
        return f"Vertex({data})"

    __repr__ = __str__

    def add_edge(self, e: int, vertex):
        self.edges[e] = vertex
        vertex.edges[opposite(e)] = self

    def proj(self):
        """Project the vertex to 2D space."""
        return np.dot(self.coords, uv)

    def has_neighbor(self, k: int):
        return k % 10 in self.edges

    def get_neighbor(self, k: int):
        return self.edges[k % 10]

    def move_along(self, e: int):
        """
        Given a direction e (ranging from 0 to 9), adjust current vertex's
        coordinates in the 5D space such that its 2D projection corresponds to
        the current vertex's neighbor in the e-th direction.
        """
        if e % 2 == 0:
            self.coords[e // 2] += 1
        else:
            self.coords[opposite(e) // 2] -= 1

    def order(self):
        """Check if this vertex has exactly three neighbors.
        If so, return them in the order (i, j, k) such that
        the angles between (i, j) and (j, k) are equal.
        """
        assert len(self.edges) == 3
        for i in self.edges.keys():
            i3 = (i + 3) % 10
            i4 = (i + 4) % 10
            i6 = (i + 6) % 10
            i7 = (i + 7) % 10
            if self.has_neighbor(i3) and self.has_neighbor(i7):
                return i3, i, i7
            elif self.has_neighbor(i4) and self.has_neighbor(i6):
                return i4, i, i6

        raise ValueError("Vertex is not flippable")

    def flippable(self):
        return self.is_free and len(self.edges) == 3

    def flip(self):
        triple = self.order()
        for e in triple:
            self.move_along(e)

        e1, e2, e3 = triple
        v1 = self.get_neighbor(e1)
        v2 = self.get_neighbor(e2)
        v3 = self.get_neighbor(e3)

        n1 = v1.get_neighbor(e2)
        n2 = v2.get_neighbor(e3)
        n3 = v3.get_neighbor(e1)
        n1.add_edge(e3, self)
        n2.add_edge(e1, self)
        n3.add_edge(e2, self)

        v1.edges.pop(opposite(e1))
        v2.edges.pop(opposite(e2))
        v3.edges.pop(opposite(e3))

        for e in [e1, e2, e3]:
            self.edges.pop(e)
        return self

    def search_rhombus(self, d, x, y):
        if not self.has_neighbor(x):
            return False

        # find the first edge towards y or against y.
        k = next(
            (
                k
                for k in (x + d * np.arange(1, 5, dtype=int)) % 10
                if self.has_neighbor(k)
            ),
            None,
        )
        if k is None:
            return False

        vk = self.get_neighbor(k)
        if k == y or k == opposite(2 * x - y):
            return vk.has_neighbor(x)
        else:
            return vk.search_rhombus(d, x, y)

    def freeze(self):
        """Check if the vertex is free."""
        edges = self.edges.keys()
        for x, y in zip(edges, np.roll(edges, -1)):
            vx = self.get_neighbor(x)
            vy = self.get_neighbor(y)
            self.is_free = (
                (y - x) % 10 <= 4
                and vy.search_rhombus(1, x, y)
                and vx.search_rhombus(-1, y, x)
                and self.search_rhombus(-1, x, opposite(y))
                and self.search_rhombus(1, y, opposite(x))
            )
            if not self.is_free:
                break
        return self

    def quality(self):
        """Measure the quality of the vertex."""
        _, j, _ = self.order()
        depth = 10
        d1, d2 = 1, -1
        a1 = next(i for i in range(1, 5) if self.has_neighbor((j + i * d1) % 10))
        a2 = next(i for i in range(1, 5) if self.has_neighbor((j + i * d2) % 10))
        v1 = self.get_neighbor((j + a1 * d1) % 10)
        v2 = self.get_neighbor((j + a2 * d2) % 10)

        def aux(d, v, b, depth):
            if depth == 0:
                return 1
            a = next(i for i in range(1, 5) if v.has_neighbor((j + i * d) % 10))
            if a == b:
                return 1  # Identical tile found
            elif a == 5 - b:
                return 0  # Symmetric tile found

            vl = v.get_neighbor((j + a * d) % 10)
            return aux(d, vl, b, depth - 1)  # Continue the search

        return aux(d1, v1, a1, depth) + aux(d2, v2, a2, depth)


def compute_rhombus(
    tiling: Dict[tuple[int], Vertex],
    shifts: Union[list[float], tuple[float], np.ndarray],
    r: int,
    s: int,
    kr: int,
    ks: int,
):
    """
    Compute the coordinates of the four vertices of the rhombus corresponding
    to the intersection point of the kr-th line in the r-th grid and the ks-th
    line in the s-th grid. Here, r, s, kr, and ks are integers satisfying the
    conditions: 0 <= r < s <= 5 and -LINE_RANGE <= kr, ks <= LINE_RANGE.

    The intersection point is determined as the solution to a 2x2 linear system:

        | uv[r][0]  uv[r][1] |   | x |   | shifts[r] |   | kr |
        |                    | @ |   | + |           | = |    |
        | uv[s][0]  uv[s][1] |   | y |   | shifts[s] |   | ks |

    Additionally, vertices falling outside the specified bounding box (bbox)
    are filtered out.
    """
    M = uv[[r, s], :]
    intersect_point = np.linalg.solve(M, [kr - shifts[r], ks - shifts[s]])
    index = np.ceil(uv @ intersect_point + shifts).astype(int)
    vertices = [
        np.dot(index, uv)
        for index[r], index[s] in [
            (kr, ks),
            (kr + 1, ks),
            (kr + 1, ks + 1),
            (kr, ks + 1),
        ]
    ]
    if all(np.max(np.absolute(vertices), axis=0) <= bbox):
        coords = [
            tuple(index)
            for index[r], index[s] in [
                (kr, ks),
                (kr + 1, ks),
                (kr + 1, ks + 1),
                (kr, ks + 1),
            ]
        ]
        v1, v2, v3, v4 = [tiling.setdefault(c, Vertex(c)) for c in coords]

        er = (2 * r) % 10
        es = (2 * s) % 10
        v1.add_edge(er, v2)
        v2.add_edge(es, v3)
        v4.add_edge(er, v3)
        v1.add_edge(es, v4)


def generate_tiling(
    shifts: Union[list[float], tuple[float], np.ndarray], line_range: int
):
    tiling = {}
    bar = tqdm.tqdm(desc="Generating vertices", unit=" vertices")

    # Iterate through all intersections of lines from different grid families.
    for r, s in itertools.combinations(range(5), 2):
        for kr, ks in itertools.product(range(-line_range, line_range + 1), repeat=2):
            compute_rhombus(tiling, shifts, r, s, kr, ks)
            bar.update(len(tiling) - bar.n)

    return list(tiling.values())  # Return the list of vertices


def draw_tiling(tiling: list[Vertex], fname: str):
    ax = plt.gca()
    ax.clear()
    ax.axis("off")
    ax.axis([-bbox[0], bbox[0], -bbox[1], bbox[1]])
    ax.set_aspect("equal")

    for v in tiling:
        inds = list(v.edges.keys())
        for x, y in zip(inds, np.roll(inds, -1)):
            if v.get_neighbor(x).has_neighbor(y) and v.get_neighbor(y).has_neighbor(x):
                A = v.proj()
                B = v.get_neighbor(x).proj()
                C = v.get_neighbor(x).get_neighbor(y).proj()
                D = v.get_neighbor(y).proj()
                if (y - x) % 10 in (2, 3):
                    color = FAT_COLOR
                else:
                    color = THIN_COLOR
                poly = patches.Polygon(
                    [A, B, C, D],
                    closed=True,
                    fc=color,
                    ec=EDGE_COLOR,
                    lw=1,
                    joinstyle="round",
                    capstyle="round",
                )
                ax.add_patch(poly)
    plt.savefig(fname, bbox_inches="tight", transparent=True)


def main():
    shifts = [0.2] * 5
    tiling = generate_tiling(shifts, line_range=LINE_RANGE)
    logger.info(f"total number of vertices: {len(tiling)}")

    for v in tqdm.tqdm(tiling, desc="Freezing vertices"):
        v.freeze()

    count = 0
    for _ in tqdm.trange(200, desc="Flipping vertices round one"):
        random.shuffle(tiling)
        for v in tiling:
            if v.flippable():
                x, _ = v.proj()
                p = get_probability_round_one(x)[v.quality()]
                if np.random.random() < p:
                    v.flip()
                    count += 1

    for _ in tqdm.trange(100, desc="Flipping vertices round two"):
        random.shuffle(tiling)
        for v in tiling:
            if v.flippable():
                x, _ = v.proj()
                p = get_probability_round_two(x)[v.quality()]
                if np.random.random() < p:
                    v.flip()
                    count += 1

    logger.info(f"total number of flips: {count}")
    logger.info("Drawing the tiling")
    draw_tiling(tiling, f"penrose_cooling.png")


if __name__ == "__main__":
    main()
