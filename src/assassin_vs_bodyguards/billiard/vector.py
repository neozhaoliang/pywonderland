import numpy as np


class Vec2(np.ndarray):

    def __new__(cls, *args):
        obj = np.empty(2).view(cls)
        if len(args) == 1:
            obj[:] = args[0]
        else:
            obj[:] = args

        return obj

    def normalize(self):
        self /= np.linalg.norm(self)
        return self

    @property
    def x(self):
        return self[0]

    @property
    def y(self):
        return self[1]

    def perpendicular(self):
        return Vec2(-self.y, self.x)

    def midpoint(self, other):
        return (self + other) / 2

    def length(self):
        return np.linalg.norm(self)
