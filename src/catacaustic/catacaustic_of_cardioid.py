"""
Compute the catacaustic of the cardioid and draw it with matplotlib. The result is a nephroid.

Full explanation: https://pywonderland.com/catacaustics
"""

import numpy as np
import matplotlib.pyplot as plt
from sympy import *

t, X, Y = symbols("t X Y")
x = (2 * cos(t) + cos(2 * t)) / 3
y = (2 * sin(t) + sin(2 * t)) / 3
C = Matrix([x, y])  # curve
light_source = Matrix([S("-1/3", evaluate=False), 0])  # The light source is at the cusp (-1/3, 0).
l = C - light_source  # incident ray at (x, y)
dx, dy = diff(x, t), diff(y, t)  # tangent vector at (x, y)
n = Matrix([dy, -dx])  # normal vector at (x, y)
r = simplify(l - 2 * l.dot(n) * n / n.dot(n))  # reflected ray at (x, y)

# equations of the envelope: F = 0 and dF = 0
F = (Y - y) * r[0] - (X - x) * r[1]
dF = diff(F, t)

# solve the envelope
result = solve((F, dF), X, Y)

# simplify the result. The option "method=groebner" is the key to get a good expression!
X = trigsimp(result[X], method="groebner")
Y = trigsimp(result[Y], method="groebner")

# draw the cardioid and the envelope
T = np.linspace(0, 2 * np.pi, 500)
curve_x = np.array([x.subs(t, ti) for ti in T])
curve_y = np.array([y.subs(t, ti) for ti in T])
ray_x = np.array([r[0].subs(t, ti) for ti in T]) * 100
ray_y = np.array([r[1].subs(t, ti) for ti in T]) * 100
catacaustic_x = np.array([X.subs(t, ti) for ti in T])
catacaustic_y = np.array([Y.subs(t, ti) for ti in T])

plt.xlim(-0.6, 1.1)
plt.ylim(-1, 1)
plt.plot(curve_x, curve_y, label="cardioid")
plt.plot(catacaustic_x, catacaustic_y, label="nephroid", color=(1, 0, 1))

color = (0.8, 0.4, 0)
for i in range(0, len(T), 5):
    plt.plot(
        [light_source[0], curve_x[i]],
        [light_source[1], curve_y[i]],
        lw=0.5,
        color=color,
    )
    plt.plot(
        [curve_x[i], curve_x[i] + ray_x[i]],
        [curve_y[i], curve_y[i] + ray_y[i]],
        lw=0.5,
        color=color,
    )

plt.plot(light_source[0], light_source[1], "o", color="yellow", label="light source")
plt.title("Catacaustic of the cardioid")
plt.gca().set_aspect("equal")
plt.legend()
plt.savefig("caustics_matplotlib.svg", bbox_inches="tight")
