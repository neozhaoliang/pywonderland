"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Assassin vs Bodyguards in a Room
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Click on the canvas and drag the mouse to see the trajectory.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backend_bases import MouseButton
from billiard import Room, polygon, Vec2


shape = "square"  # "square", "triangle", "hexagon"
click_point = Vec2(0, 0)

margin = 0.02
if shape == "square":
    bbox = [0, 1, 0, 1]
elif shape == "triangle":
    bbox = [-margin, 1 + margin, -margin, 3**0.5 / 2 + margin]
elif shape == "hexagon":
    bbox = [-0.5 - margin, 1.5 + margin, -margin, 3**0.5 + margin]


plt.gca().axis(bbox)
plt.gca().set_aspect("equal", adjustable="box")
plt.gca().axis("off")


def random_point_in_square():
    return Vec2(np.random.random(2))


def random_point_in_triangle():
    x, y = sorted(np.random.random(2))
    t, u = y - x, 1 - y
    return t * polygon.TRIANGLE[1] + u * polygon.TRIANGLE[2]


def random_point_in_hexagon():
    weights = np.random.random(6)
    weights /= weights.sum()
    return sum(w * v for w, v in zip(weights, polygon.HEXAGON))


# the trajectories before and after the guard, and to the target
(traj1,) = plt.plot([], [], "-", color="gray", lw=0.5)
(traj2,) = plt.plot([], [], linestyle="dashed", color="gray", lw=0.5)


def on_click(event):
    global click_point, room, assassin, guards, target
    if event.button is MouseButton.LEFT:
        if event.inaxes:
            click_point = Vec2(event.xdata, event.ydata)
            dir = (click_point - assassin).normalize()
            trajectory, index = room.fold_ray_into_room(assassin, dir, guards, target)
            if trajectory is not None:
                traj1.set_data(*zip(*trajectory[:index]))
                traj2.set_data(*zip(*trajectory[index - 1 :]))
                plt.gcf().canvas.draw()


plt.connect("button_press_event", on_click)
plt.connect("motion_notify_event", on_click)

room = Room(shape)
if shape == "triangle":
    assassin = random_point_in_triangle()
    target = random_point_in_triangle()
    polygon.plot_triangle(Vec2(0, 0), 0)

elif shape == "square":
    assassin = random_point_in_square()
    target = random_point_in_square()
    polygon.plot_square(Vec2(0, 0), 0)

elif shape == "hexagon":
    assassin = random_point_in_hexagon()
    target = random_point_in_hexagon()
    polygon.plot_hexagon(Vec2(0, 0))

guards = room.compute_guards_positions(assassin, target)
plt.plot(*assassin, "ro", markersize=8, markeredgecolor="k", lw=0.5)
plt.plot(*zip(*guards), "co", markersize=5, markeredgecolor="k", lw=0.5)
plt.plot(*target, "bo", markersize=8, markeredgecolor="k", lw=0.5)
plt.tight_layout()
plt.show()
