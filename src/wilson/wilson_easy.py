'''
A pseudocode style implementation of Wilson's uniform spanning tree algorithm on a 2d grid.

Reference:

"Generating random spanning trees more quickly than the cover time", David Bruce Wilson.

'''

import random
import cairo
from itertools import product


def grid_graph(*size):

    def neighbors(v):
        neighborhood = []
        for i in range(len(size)):
            for dx in [-1,1]:
                w = list(v)
                w[i] += dx
                if 0 <= w[i] < size[i]:
                    neighborhood.append(tuple(w))
        return neighborhood

    return {v: neighbors(v) for v in product(*map(range, size))}


def uniform_spanning_tree(graph):
    '''
    Use a loop-erased random walk to pick a random spanning tree
    among all trees with uniform probability.
    '''
    root = random.choice(graph.keys())
    parent = {root: None}
    tree = set([root])

    for vertex in graph:
        v = vertex
        while v not in tree:
            neighbor = random.choice(graph[v])
            parent[v] = neighbor
            v = neighbor

        v = vertex
        while v not in tree:
            tree.add(v)
            v = parent[v]
    return parent


def random_maze(gridsize, imagesize):
    m, n = gridsize
    W, H = imagesize
    G = grid_graph(m, n)
    tree = uniform_spanning_tree(G)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    cr = cairo.Context(surface)
    cr.scale(W/(m+1.0), -H/(n+1.0))
    cr.translate(1, -n)
    cr.set_source_rgb(0, 0, 0)
    cr.paint()

    cr.set_line_cap(2)
    cr.set_line_width(0.5)
    cr.set_source_rgb(1, 1, 1)


    for v, w in tree.items():
        if w is not None:
            cr.move_to(v[0], v[1])
            cr.line_to(w[0], w[1])
            cr.stroke()
    surface.write_to_png('wilson{}x{}.png'.format(m, n))


if __name__ == '__main__':
    random_maze(gridsize=(80, 60), imagesize=(600, 450))
