import numpy as np
from enums import Geometry


class Mobius(object):

    def __init__(self, mat):
        self.mat = np.array(mat).astype(np.complex)

    def __str__(self):
        return str(self.mat)

    def __mul__(self, M):
        if isinstance(M, (int, float, complex)):
            return Mobius(self.mat * M)
        else:
            return Mobius(np.dot(self.mat, M.mat))

    def normalize(self):
        det = np.sqrt(np.linalg.det(self.mat))
        self.mat /= det
        return self

    @staticmethod
    def identity():
        return Mobius([[1, 0],
                       [0, 1]])

    @staticmethod
    def scale(c):
        return Mobius([[c, 0],
                       [0, 1]])

    @staticmethod
    def from_isometry(g, angle, P, ):
        T = complex(np.cos(angle), np.sin(angle))
        if g == Geometry.hyperbolic:
            return Mobius([[T, P],
                           [P.conjugate() * T, 1]])
        elif g == Geometry.euclidean:
            return Mobius([[T, P],
                           [0, 1]])
        elif g == Geometry.spherical:
            return Mobius([[T, P],
                           [P.conjugate() * T, 1]])
        else:
            raise ValueError("invalid geometry type")

    def inverse(self):
        return Mobius([[self.mat[1, 1], -self.mat[0, 1]],
                       [-self.mat[1, 0], self.mat[0, 0]]]).normalize()

    def act(self, z):
        return (self.mat[0, 0]*z + self.mat[0, 1]) / (self.mat[1, 0]*z + self.mat[1, 1])

    @staticmethod
    def from_geodesic(g, p1, p2):
        T = Mobius.from_isometry(g, 0, -p1)
        p2_by_T = T.act(p2)

        S = Mobius.from_isometry(g, 0, p2_by_T)
        return T.inverse() * S * T

    @staticmethod
    def hyperbolic(g, fixed, scale):
        T = Mobius.from_isometry(g, 0, -fixed)
        S = Mobius.scale(scale)
        T_inv = Mobius.from_isometry(g, 0, fixed)
        return T_inv * S * T

    @staticmethod
    def hyperbolic2(g, fixed, p, offset):
        T = Mobius.from_isometry(g, 0, -fixed)
        eNorm = abs(T.act(p))

        if g == Geometry.spherical:
            sNorm = e2sNorm(eNorm) + offset
            scale = s2eNorm(sNorm) / eNorm
        elif g == Geometry.euclidean:
            scale = (eNorm + offset) / eNorm
        elif g == Geometry.hyperbolic:
            hNorm = e2hNorm(eNorm) + offset
            scale = h2eNorm(hNorm) / eNorm
        else:
            raise ValueError("invald geometry type")

        return Mobius.hyperbolic(g, fixed, scale)
