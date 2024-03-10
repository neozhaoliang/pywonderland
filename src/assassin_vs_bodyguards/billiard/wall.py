import numpy as np
import matplotlib.pyplot as plt

from .vector import Vec2
from .transform import reflect_about_line


class Wall:

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.dir = (p2 - p1).normalize()
        self.normal = Vec2(-self.dir.y, self.dir.x)
        self.offset = np.dot(self.p1, self.normal)

    def reflect(self, point):
        return reflect_about_line(point, self.normal, self.offset)

    def on_positive_side(self, point):
        """Check if a point lies on the same side of the wall as the room."""
        return np.dot(point, self.normal) >= self.offset

    def intersect(self, A, B):
        """Compute the intersection of the wall with the line segment AB.
        Return None if there is no intersection.
        """
        n1 = self.normal
        k1 = np.dot(self.p1 - A, n1) / np.dot(B - A, n1)
        if 0 <= k1 <= 1:
            n2 = (B - A).perpendicular()
            k2 = np.dot(A - self.p1, n2) / np.dot(self.p2 - self.p1, n2)
            if 0 <= k2 <= 1:
                return A + k1 * (B - A)
        return None

    def plot(self, *args, **kwargs):
        """Plot the wall."""
        plt.plot([self.p1.x, self.p2.x], [self.p1.y, self.p2.y], *args, **kwargs)
