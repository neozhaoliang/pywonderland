# -*- coding: utf-8 -*-

"""
This short script illustrates you how Wilson's algorithm works.
"""

import random
from itertools import product
import matplotlib.pyplot as plt


def grid_graph(*size):
    
    def neighbors(v):
        neighborhood = []
        for i in range(len(size)):
            for dx in [-1, 1]:
                w = list(v)
                w[i] += dx
                if 0 <= w[i] < size[i]:
                    neighborhood.append(tuple(w))
        return neighborhood
        
    return {v: neighbors(v) for v in product(*map(range, size))}


width, height = 48, 36
G = grid_graph(width, height)
root = random.choice(G.keys())
tree = set([root]) 
parent = dict() 

for vertex in G:
    v = vertex
    while v not in tree:
        neighbor = random.choice(G[v])
        parent[v] = neighbor
        v = neighbor

    v = vertex
    while v not in tree:
        tree.add(v)   
        v = parent[v]

fig = plt.figure(figsize=(4.8, 3.6), dpi=100)
ax = fig.add_axes([0, 0, 1, 1], aspect=1)
ax.axis('off')
ax.axis([-1, width, -1, height])

for key, item in parent.items():
    a, b = key
    x, y = item
    ax.plot([a, x], [b, y], 'k-', lw=3)

x, y = root
ax.plot(x, y, 'ro', ms=7)
plt.savefig('ust_{}x{}.png'.format(width, height))
