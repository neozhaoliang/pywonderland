import numpy as np


class Vector(object):

    def __init__(self, array=(0, 0, 0, 0)):
        self.vector = np.zeros(4, dtype=np.float)
        self.vector[0: len(array)] = array
        
    def __getitem__(self, item):
        return self.vector.__getitem__(item)
      
    def __setitem__(self, key, item):
        self.vector[key] = item 

    def __repr__(self):
        return "Vector({}, {}, {}, {})".format(*self)

    def __complex__(self):
        return complex(self[0], self[1])

    def norm(self):
        return np.linalg.norm(self.vector)

    def normalize(self):
        self.vector /= self.norm()

    def conjugate(self):
        x, y, z, w = self
        return Vector([-x, -y, -z, w])

    def __add__(self, other):
        return Vector(self.vector + other.vector)

    def __sub__(self, other):
        return Vector(self.vector - other.vector)

    def inverse(self):
        return self.conjugate() / (self.norm() * self.norm())

    def dot(self, other):
        return np.dot(self.vector, other.vector)

    def cross(self, other):
        return Vector(np.cross(self[:3], other[:3]))

    def rotate_xy(self, angle, center=complex(0, 0)):
        """Rotate in the xy-plane about a center."""
        u = complex(self) - center
        u *= complex(np.cos(angle), np.sin(angle))
        u += center
        return Vector([u.real, u.imag, self[2], self[3]])

    def rotate_about_axis(self, axis, angle):
        """
        Rotate current vector about a given axis.
        Formula from https://en.wikipedia.org/wiki/Rotation_matrix
        """
        axis.normalize()
        x, y, z = axis[:3]
        s, c = np.sin(angle), np.cos(angle)
        t = 1 - c
        mat = np.array([[c + t*x*x, t*x*y - s*z, t*x*z + s*y],
                        [t*x*y + s*z, c + t*y*y, t*y*z - s*x],
                        [t*x*z - s*y, t*y*z + s*x, c + t*z*z]])
        return Vector(np.dot(mat, self[:3]))



class Circle(object):

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius


class Sphere(object):

    def __init__(self, center, radius, normal):
        self.center = center
        self.radius = radius
        self.normal = normal
