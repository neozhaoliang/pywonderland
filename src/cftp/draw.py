# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt


# directions of the three axis.
X = np.exp(1j * np.pi * 7 / 6)
Y = np.exp(1j * np.pi * 11 / 6)
Z = np.exp(1j * np.pi / 2)

# colors of the faces.
TOP_COLOR = (1, 0, 0)
LEFT_COLOR = (0, 1, 1)
RIGHT_COLOR = (0.75, 0.5, 0.25)

# three faces of the unit cube at (0, 0).
TOP = np.array([(0, 0), (np.sqrt(3) * 0.5, 0.5), (0, 1), (-np.sqrt(3) * 0.5, 0.5), (0, 0)])
LEFT = np.array([(0, 0), (-np.sqrt(3) * 0.5, 0.5), (-np.sqrt(3) * 0.5, -0.5), (0, -1), (0, 0)])
RIGHT = np.array([(0, 0), (np.sqrt(3) * 0.5, 0.5), (np.sqrt(3) * 0.5, -0.5), (0, -1), (0, 0)])

def topface(ax):
    face = plt.Polygon(TOP, fc=TOP_COLOR, ec='k', lw=1)
    return ax.add_patch(face)

def leftface(ax):
    face = plt.Polygon(LEFT, fc=LEFT_COLOR, ec='k', lw=1)
    return ax.add_patch(face)

def rightface(ax):
    face = plt.Polygon(RIGHT, fc=RIGHT_COLOR, ec='k', lw=1)
    return ax.add_patch(face)


def draw_tiling(T):
    """
    Draw the lozenge tiling `T` with matplotlib.
    """
    fig = plt.figure(figsize=(5, 5), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1], aspect=1)
    a, b, c = T.size
    ax.axis([-b-0.5, a+0.5, -a-0.5, c+2])
    ax.axis("off")

    # floor
    for i in range(a):
        for j in range(b):
            floor = topface(ax)
            shift = i * Y + j * X
            floor.set_xy(TOP + (shift.real, shift.imag))

    # left wall
    for i in range(b):
        for j in range(c):
            left_wall = rightface(ax)
            shift = i * X + j * Z - Y + Z
            left_wall.set_xy(RIGHT + (shift.real, shift.imag))

    # right wall
    for i in range(a):
        for j in range(c):
            right_wall = leftface(ax)
            shift = i * Y + j * Z - X + Z
            right_wall.set_xy(LEFT + (shift.real, shift.imag))

    # cubes
    pp = T.to_plane_partition()
    for i, x in enumerate(pp):
        for j, val in enumerate(x):
            for k in range(val):
                shift = i * Z + j * X + k * Y + Z
                floor = topface(ax)
                floor.set_xy(TOP + (shift.real, shift.imag))
                left_wall = rightface(ax)
                left_wall.set_xy(RIGHT + (shift.real, shift.imag))
                right_wall = leftface(ax)
                right_wall.set_xy(LEFT + (shift.real, shift.imag))

    fig.savefig("lozenge_tiling.png")
