import numpy as np
import matplotlib.pyplot as plt

from .vector import Vec2
from .transform import reflect_about_line

size = 0.1
default_marker = [Vec2(-size, -size), Vec2(-size, size), Vec2(size, size)]


class Marker:
    """Draw markers in the polygons to help visualize the different lattices."""

    def __init__(self, pts=None):
        if pts is None:
            pts = default_marker
        self.points = pts

    def rotate(self, theta):
        theta = np.deg2rad(theta)
        c = np.cos(theta)
        s = np.sin(theta)
        R = np.array([[c, -s], [s, c]])
        self.points = [np.dot(R, z) for z in self.points]
        return self

    def reflect(self, normal, offset=0):
        self.points = [reflect_about_line(p, normal, offset) for p in self.points]
        return self

    def translate(self, v):
        self.points = [p + v for p in self.points]
        return self

    def scale(self, s):
        self.points = [p * s for p in self.points]
        return self

    def transform_by_group_element(self, g):
        self.points = [g(p) for p in self.points]
        return self

    def center(self):
        return sum(self.points, Vec2(0, 0)) / len(self.points)

    def plot(self, *args, **kwargs):
        x, y = zip(*self.points)
        plt.plot(x, y, *args, **kwargs)
