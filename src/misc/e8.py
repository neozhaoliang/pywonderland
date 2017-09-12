# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~
The E8 picture
~~~~~~~~~~~~~~

This script draws the picture of E8 projected to its Coxeter plane.
For a detailed discussion of the math see Humphreys's book

    Reflection Groups and Coxeter Groups, section 17, chapter 3.
"""

from itertools import product, combinations
import cairocffi as cairo
import numpy as np
from palettable.colorbrewer.qualitative import Set1_8


# --- step one: compute all roots and edges ---

# there are 240 roots in the root system,
# mutiply them by a factor 2 to be handy for computations.
roots = []

# roots of the form (+-1, +-1, 0, 0, 0, 0, 0, 0),
# signs can be chosen independently and the two non-zeros can be anywhere.
for i, j in combinations(range(8), 2):
    for x, y in product([-2, 2], repeat=2):
        v = np.zeros(8)
        v[i] = x
        v[j] = y
        roots.append(v)

# roots of the form 1/2 * (+-1, +-1, ..., +-1).
# signs can be chosen indenpendently except that there must be an even numer of -1s.
for v in product([-1, 1], repeat=8):
    if sum(v) % 4 == 0:
        roots.append(v)
roots = np.array(roots).astype(np.int)


# connect a root to its nearest neighbors,
# two roots are connected if and only if they form an angle of pi/3.
edges = []
for i, r in enumerate(roots):
    for j, s in enumerate(roots[i+1:], i+1):
        if np.sum((r - s)**2) == 8:
            edges.append([i, j])


# --- Step two: compute a basis of the Coxeter plane ---

# a set of simple roots listed by rows of 'delta'
delta = np.array([[1, -1, 0, 0, 0, 0, 0, 0],
                  [0, 1, -1, 0, 0, 0, 0, 0],
                  [0, 0, 1, -1, 0, 0, 0, 0],
                  [0, 0, 0, 1, -1, 0, 0, 0],
                  [0, 0, 0, 0, 1, -1, 0, 0],
                  [0, 0, 0, 0, 0, 1, 1, 0],
                  [-.5, -.5, -.5, -.5, -.5, -.5, -.5, -.5],
                  [0, 0, 0, 0, 0, 1, -1, 0]])
# the Dynkin diagram:
# 1---2---3---4---5---6---7
#                 |
#                 8
# where vertex i is the i-th simple root.

# the cartan matrix:
cartan = np.dot(delta, delta.transpose())

# now we split the simple roots into two disjoint sets I and J
# such that the simple roots in each set are pairwise orthogonal.
# It's obvious to see how to find such a splitting given the Dynkin graph above:
# I = [1, 3, 5, 7] and J = [2, 4, 6, 8]
# since roots are not connected by an edge if and only if they are orthogonal.
# Then a basis of the Coxeter plane is given by
# u = sum (c[i] * delta[i]) for i in I
# v = sum (c[j] * delta[j]) for j in J
# where c is an eigenvector for the minimal
# eigenvalue of the Cartan matrix.
eigenvals, eigenvecs = np.linalg.eigh(cartan)

# The eigenvalues returned by eigh() are in ascending order
# and the eigenvectors are listed by columns.
c = eigenvecs[:, 0]
u = np.sum([c[i] * delta[i] for i in [0, 2, 4, 6]], axis=0)
v = np.sum([c[j] * delta[j] for j in [1, 3, 5, 7]], axis=0)

# Gram-Schimdt u, v and normalize them to unit vectors.
u /= np.linalg.norm(u)
v = v - np.dot(u, v) * u
v /= np.linalg.norm(v)


# --- step three: project to the Coxeter plane ---
roots_2d = [(np.dot(u, x), np.dot(v, x)) for x in roots]

# sort these projected vertices by their modulus in the coxter plane,
# each successive 30 vertices form one ring in the resulting pattern,
# assign these 30 vertices a same color.
colorlist = Set1_8.mpl_colors
vertex_colors = np.zeros((len(roots), 3))
modulus = np.linalg.norm(roots_2d, axis=1)
ind_array = modulus.argsort()
for i in range(8):
    for j in ind_array[30*i : 30*(i+1)]:
        vertex_colors[j] = colorlist[i]


# --- step four: render to png image ---
image_size = 600
# the axis lie between [-extent, extent] x [-extent, extent]
extent = 2.4
linewidth = 0.0018
markersize = 0.05

surface = cairo.ImageSurface(cairo.FORMAT_RGB24, image_size, image_size)
ctx = cairo.Context(surface)
ctx.scale(image_size/(extent*2.0), -image_size/(extent*2.0))
ctx.translate(extent, -extent)
ctx.set_source_rgb(1, 1, 1)
ctx.paint()

for i, j in edges:
    x1, y1 = roots_2d[i]
    x2, y2 = roots_2d[j]
    ctx.set_source_rgb(0.2, 0.2, 0.2)
    ctx.set_line_width(linewidth)
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()

for i in range(len(roots)):
    x, y = roots_2d[i]
    color = vertex_colors[i]
    grad = cairo.RadialGradient(x, y, 0.0001, x, y, markersize)
    grad.add_color_stop_rgb(0, *color)
    grad.add_color_stop_rgb(1, *color/2)
    ctx.set_source(grad)
    ctx.arc(x, y, markersize, 0, 2*np.pi)
    ctx.fill()

surface.write_to_png('e8-pattern.png')
