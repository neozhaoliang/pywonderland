import numpy as np
from utils import (Geometry, isinfinite, e2snorm, s2enorm, e2hnorm,
                   h2enorm)


class Mobius(object):

    """
    A Mobius transformation is a complex function of the form
    z --> (a*z+b) / (c*z+d) which can be represented as a 2x2 matrix
    [[a, b],
     [c, d]].
    """

    def __init__(self, mat):
        """`mat` must have shape 2x2."""
        self.mat = np.array(mat).astype(np.complex)

    def __str__(self):
        return str(self.mat)

    def __mul__(self, M):
        """
        The composition of two Mobius transformations is the product of their matrices.
        """
        return Mobius(np.dot(self.mat, M.mat))

    def __call__(self, z):
        """Apply this Mobius transformation to a complex number z."""
        a, b, c, d = self.mat.ravel()
        if isinfinite(z):
            return a / c
        else:
            return (a*z + b) / (c*z + d)

    @staticmethod
    def identity():
        """Return the identity transformation."""
        return Mobius([[1, 0],
                       [0, 1]])

    @staticmethod
    def scale(c):
        """Return the scaling transformation."""
        return Mobius([[c, 0],
                       [0, 1]])

    def normalize(self):
        """
        Rescale the components of the matrix so that its determinant ad - bc = 1.
        """
        det = np.sqrt(np.linalg.det(self.mat))
        self.mat /= det
        return self

    @staticmethod
    def isometry(g, theta, a):
        """
        g: must be one of Geometry.spherical, Geometry.euclidean, Geometry.hyperbolic.
        theta: an angle in [0, 2*pi]
        a: a complex number in the unit disk.

        Return the unique Mobius transformation that firstly rotates around
        the origin with angle `theta`, and then translates the origin to `a`.

        In Euclidean geometry it's simply
        z --> exp(theta*1j) * z + a.
        All isometries of the Euclidean plane are of this form.

        In hyperbolic geometry (the Poincare disk model) it's
        z --> exp(theta*1j) * (z + b) / (b.conjugate() * z + 1)
        where b = a * exp(-theta*1j).
        All isometries of the Poincare disk are of this form.

        In spherical geometry all isometries are of the form (SU(2))
        z --> (a*z + b) / (-b.conjugate() * z + a.conjugate())
        where |a|^2 + |b|^2 = 1.
        In this case 
        """
        rot = complex(np.cos(theta), np.sin(theta))
        if g == Geometry.euclidean:
            return Mobius([[rot, a],
                           [ 0,  1]])

        elif g == Geometry.hyperbolic:
            return Mobius([[rot, a],
                           [a.conjugate() * rot, 1]])

        elif g == Geometry.spherical:
            return Mobius([[rot, a],
                           [-a.conjugate() * rot, 1]])

        else:
            raise ValueError("invalid type for geometry.")

    def inverse(self):
        """return the inverse transformation."""
        a, b, c, d = self.mat.ravel()
        return Mobius([[d, -b],
                       [-c, a]]).normalize()

    @staticmethod
    def geodesic(g, p1, p2):
        """
        p1, p2: two complex numbers.
        return the unique Mobius transformation that translates
        p1 to p2 along the geodesic line in geometry g.
        
        This transformation is conjugate with a translation z --> z + a.
        """
        T = Mobius.isometry(g, 0, -p1)        
        S = Mobius.isometry(g, 0, T(p2))
        return T.inverse() * S * T

    @staticmethod
    def three_points(z1, z2, z3):
        """
        Return the unique Mobius transformation that maps z1 to 0,
        z2 to one and z3 to infinity.
        """
        if isinfinite(z1):
            return Mobius([[ 0,  z3 - z2],
                           [-1,     z3  ]])

        elif isinfinite(z2):
            return Mobius([[1, -z1],
                           [1, -z3]])

        elif isinfinite(z3):
            return Mobius([[-1,     z1  ],
                           [ 0,  z1 - z2]])

        else:
            return Mobius([[z2 - z3, -z1 * (z2 - z3)],
                           [z2 - z1, -z3 * (z2 - z1)]])

    @staticmethod
    def disc_to_upper_plane():
        """Return the conformal mapping that maps the unit disc to the upper plane."""
        return Mobius.three_points(-1j, 1, 1j)

    @staticmethod
    def triple_to_triple(triple_z, triple_w):
        """
        Return the unique Mobius transformation that maps (z1, z2, z3) to (w1, w2, w3).
        """
        M1 = Mobius.three_points(*triple_z)
        M2 = Mobius.three_points(*triple_w)
        return M2.inverse() * M1

    @staticmethod
    def elliptic(g, p, theta):
        """
        Return the elliptic Mobius transformation whose fixed point is `p` and 
        rotates around `p` with angle `theta`.
        A Mobius transformation is called elliptic if and only if it is
        conjugate to a rotation z --> exp^{theta*1j} * z.
        """
        T = Mobius.isometry(g, 0, -p)
        S = Mobius.isometry(g, theta, 0)
        return T.inverse() * S * T

    @staticmethod
    def hyperbolic(g, fixed, scale):
        """
        Return the hyperbolic Mobius transformation whose fixed point is `fixed` and
        scaling `scale`.
        A Mobius transformation is called hyperbolic if and only if it is
        conjugate to a dilation z --> k*z.
        """
        M1 = Mobius.isometry(g, 0, -fixed)
        M2 = Mobius.scale(scale)
        M3 = Mobius.isometry(g, 0, fixed)
        return M3 * M2 * M1

    @staticmethod
    def hyperbolic2(g, fixed, point, offset):
        """
        A variation of the `hyperbolic` function above, return the hyperbolic transformation
        that moves `point` along the geodesic line with distance `offset`.
        """
        M1 = Mobius.isometry(g, 0, -fixed)
        eradius = abs(M1(point))

        if g == Geometry.spherical:
            sradius = e2snorm(eradius) + offset
            scale = s2norm(sradius) / eradius

        elif g == Geometry.euclidean:
            scale = (eradius + offset) / eradius

        elif g == Geometry.hyperbolic:
            hradius = e2hnorm(eradius) + offset
            scale = h2enorm(hradius) / eradius

        else:
            raise ValueError("invalid geometry type.")
        return Mobius.hyperbolic(g, fixed, scale)
