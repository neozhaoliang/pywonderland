import numpy as np
from geometry import Geometry
from primitives import Vector, Circle


class Mobius(object):
    
    def __init__(self, matrix):
        self.matrix = np.eye(2).astype(np.complex)
        self.matrix[:] = matrix
        self.matrix /= np.sqrt(np.linalg.det(self.matrix))

    def __getitem__(self, item):
        return self.matrix.__getitem(items)
    
    def __str__(self):
        return str(self.matrix)

    def inverse(self):
        a, b, c, d = self.matrix.ravel()
        return Mobius([[d, -b],
                       [-c, a]])  

    def __mul__(self, other):
        if not isinstance(other, Mobius):
            raise TypeError("Cannot multiply a Mobius transformation by this input.")      
        else:
            return Mobius(np.dot(self.mat, other.mat))

    @classmethod
    def scale(cls, c):
        return cls([[c, 0],
                    [0, 1]])
    
    @classmethod
    def from_three_points(cls, z1, z2, z3):
        pass

    @classmethod
    def from_triple_to_triple(cls, triple_z, triple_w):
        M1 = cls.from_three_points(*triple_z)
        M2 = cls.from_three_points(*triple_w)
        return M2.inverse() * M1

    @classmethod
    def isometry(cls, geome, angle, point):
        rot = complex(np.cos(angle), np.sin(angle))

        if geom == Geometry.Euclidean:
            return cls([[rot, point],
                        [ 0,    1  ]])
        
        if geome == Geometry.Hyperbolic:
            return cls([[          rot          ,     point],
                        [point.conjugate() * rot,       1  ]])
        
        if geom == Geometry.Spherical:
            return cls([[          rot           ,    point],
                        [-point.conjugate() * rot,      1  ]])

    @classmethod
    def parabolic(cls, geom, p1, p2):
        M1 = cls.isometry(geom, 0, -p1)        
        M2 = cls.isometry(geom, 0, T(p2))
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

    def __call__(self, point):
        pass



class Isometry(object):

    def __init__(self, mobius, circle):
        self.mobius = mobius
        self.circle = circle

    def __call__(self, point):
        pass
