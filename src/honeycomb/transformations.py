import numpy as np
from geometry import Geometry
from helpers import infinite


class Mobius(object):
    
    def __init__(self, matrix=np.eye(2)):
        self.matrix = np.eye(2).astype(np.complex)
        self.matrix[:] = matrix
        self.matrix /= np.sqrt(np.linalg.det(self.matrix))

    def __getitem__(self, item):
        return self.matrix.__getitem__(item)

    def __repr__(self):
        return "Mobius{}".format(str(self.matrix))

    def inverse(self):
        a, b, c, d = self.matrix.ravel()
        return Mobius([[d, -b],
                       [-c, a]])  

    def __mul__(self, other):
        if not isinstance(other, Mobius):
            raise ValueError("A Mobius transformation is expected.")
        else:
            return Mobius(np.dot(self.matrix, other.matrix))

    @classmethod
    def from_three_points(cls, z1, z2, z3):
        if infinite(z1):
            return cls([[ 0,  z3 - z2],
                        [-1,     z3  ]])

        elif infinite(z2):
            return cls([[1, -z1],
                        [1, -z3]])

        elif infinite(z3):
            return cls([[-1,     z1  ],
                        [ 0,  z1 - z2]])

        else:
            return cls([[z2 - z3, -z1 * (z2 - z3)],
                        [z2 - z1, -z3 * (z2 - z1)]])

    @classmethod
    def from_triple_to_triple(cls, triple_z, triple_w):
        M1 = cls.from_three_points(*triple_z)
        M2 = cls.from_three_points(*triple_w)
        return M2.inverse() * M1

    @classmethod
    def scale(cls, c):
        return cls([[c, 0],
                    [0, 1]])

    @classmethod
    def isometry(cls, geom, angle, point):
        rot = complex(np.cos(angle), np.sin(angle))

        if geom == Geometry.Euclidean:
            return cls([[rot, point],
                        [ 0,    1  ]])
        
        if geom == Geometry.Hyperbolic:
            return cls([[          rot          ,     point],
                        [point.conjugate() * rot,       1  ]])
        
        if geom == Geometry.Spherical:
            return cls([[          rot           ,    point],
                        [-point.conjugate() * rot,      1  ]])

    @classmethod
    def parabolic(cls, geom, p1, p2):
        M1 = cls.isometry(geom, 0, -p1)        
        M2 = cls.isometry(geom, 0, M1(p2))
        return M1.inverse() * M2 * M1
        
    @classmethod
    def elliptic(cls, geom, fixed, angle):
        M1 = cls.isometry(geom, 0, -fixed)
        M2 = cls.isometry(geom, angle, 0)
        return M1.inverse() * M2 * M1
        
    @classmethod
    def hyperbolic(cls, geom, fixed, scale):
        M1 = cls.isometry(geom, 0, -fixed)
        M2 = cls.scale(scale)
        M3 = cls.isometry(geom, 0, fixed)
        return M3 * M2 * M1

    def __call__(self, p):
        a, b, c, d = self.matrix.ravel()

        if infinite(p):
            return a / c
        else:
            return (a * p + b) / (c * p + d)
