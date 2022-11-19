"""
~~~~~~~~~~~~~~
The E8 picture
~~~~~~~~~~~~~~

This script draws the picture of E8 projected to its Coxeter plane.
For a detailed discussion of the math see Bill Casselman's article

    "https://secure.math.ubc.ca/~cass/research/pdf/Element.pdf"

"""
from itertools import combinations, product

import numpy as np

try:
    import cairocffi as cairo
except ImportError:
    import cairo


COLORS = [
    (0.894, 0.102, 0.11),
    (0.216, 0.494, 0.72),
    (0.302, 0.686, 0.29),
    (0.596, 0.306, 0.639),
    (1.0, 0.5, 0),
    (1.0, 1.0, 0.2),
    (0.65, 0.337, 0.157),
    (0.97, 0.506, 0.75),
]



# --- step one: compute all roots and edges ---

# There are 240 roots in the root system,
# mutiply them by a factor 2 to be handy for computations.
roots = []

# Roots of the form (+-1, +-1, 0, 0, 0, 0, 0, 0),
# signs can be chosen independently and the two non-zeros can be anywhere.
for i, j in combinations(range(8), 2):
    for x, y in product([-2, 2], repeat=2):
        v = np.zeros(8)
        v[i] = x
        v[j] = y
        roots.append(v)

# Roots of the form 1/2 * (+-1, +-1, ..., +-1), signs can be chosen
# indenpendently except that there must be an even numer of -1s.
for v in product([-1, 1], repeat=8):
    if sum(v) % 4 == 0:
        roots.append(v)
roots = np.array(roots).astype(int)


# Connect a root to its nearest neighbors,
# two roots are connected if and only if they form an angle of pi/3.
edges = []
for i, r in enumerate(roots):
    for j, s in enumerate(roots[i + 1 :], i + 1):
        if np.sum((r - s) ** 2) == 8:
            edges.append([i, j])


# --- Step two: compute a basis of the Coxeter plane ---

# A set of simple roots listed by rows of 'delta'
delta = np.array(
    [
        [1, -1, 0, 0, 0, 0, 0, 0],
        [0, 1, -1, 0, 0, 0, 0, 0],
        [0, 0, 1, -1, 0, 0, 0, 0],
        [0, 0, 0, 1, -1, 0, 0, 0],
        [0, 0, 0, 0, 1, -1, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 0],
        [-0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5],
        [0, 0, 0, 0, 0, 1, -1, 0],
    ]
)

# Dynkin diagram of E8:
# 1---2---3---4---5---6---7
#                 |
#                 8
# where vertex i is the i-th simple root.

# The cartan matrix:
cartan = np.dot(delta, delta.transpose())

# get the simple reflection with respect to the basis Delta.
def get_reflection_matrix(ind):
    M = np.eye(8)
    M[ind, ind] = -1
    for k in range(8):
        if k != ind and cartan[k, ind] != 0:
            M[ind, k] = -cartan[k, ind]
    return M

# The distinct Coxeter element gamma
X = np.eye(8)
Y = np.eye(8)

for k in [0, 2, 4, 6]:
    X = X @ get_reflection_matrix(k)
    Y = Y @ get_reflection_matrix(k+1)

gamma = X @ Y
gamma_inv = Y @ X
I = np.eye(8)

# we can check that 2I + gamma + gamma_inv = (2I - cartan)^2
assert ((2*I + gamma + gamma_inv) == (2*I - cartan) @ (2*I - cartan)).all()

eigenvals, eigenvecs = np.linalg.eigh(cartan)

# The eigenvalues returned by eigh() are in ascending order
# and the eigenvectors are listed by columns.

# The eigenvectors for the min/max eigenvalues of the
# Cartan matrix form a basis of the Coxeter plane
u = eigenvecs[:, 0]
v = eigenvecs[:, -1]

u = np.dot(u, delta)
v = np.dot(v, delta)

u /= np.linalg.norm(u)
v /= np.linalg.norm(v)

# --- step three: project to the Coxeter plane ---
roots_2d = [(np.dot(u, x), np.dot(v, x)) for x in roots]

# Sort these projected vertices by their modulus in the coxter plane,
# every successive 30 vertices form one ring in the resulting pattern,
# assign these 30 vertices a same color.
vertex_colors = np.zeros((len(roots), 3))
modulus = np.linalg.norm(roots_2d, axis=1)
ind_array = modulus.argsort()
for i in range(8):
    for j in ind_array[30 * i : 30 * (i + 1)]:
        vertex_colors[j] = COLORS[i]


# --- step four: render to image ---
image_size = 600
# The axis lie between [-extent, extent] x [-extent, extent]
extent = 2.4
linewidth = 0.0018
markersize = 0.05

surface = cairo.SVGSurface("e8.svg", image_size, image_size)
ctx = cairo.Context(surface)
ctx.scale(image_size / (extent * 2.0), -image_size / (extent * 2.0))
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
    grad.add_color_stop_rgb(1, *color / 2)
    ctx.set_source(grad)
    ctx.arc(x, y, markersize, 0, 2 * np.pi)
    ctx.fill()

surface.finish()
