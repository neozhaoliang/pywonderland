import numpy as np
from .cline import CLine
from . import utils


class Mobius(np.ndarray):

    """A Mobius transformation is represented as a 2x2 complex matrix
        |a, b|
        |c, d|
    with a*d - b*c = 1
    """

    def __new__(cls, data=(1, 0, 0, 1)):
        """Create a Mobius transformation. `data` must be an iterable
        that can be converted into a 2x2 invertible matrix.
        """
        m = np.array(data, dtype=complex).reshape(2, 2).view(cls)
        det = m.det
        assert utils.nonzero(det), \
            "Cannot initialize a Mobius transformation with a singular matrix"
        m /= np.sqrt(det)
        return m

    def __str__(self):
        a, b, c, d = np.round(self.abcd, 4)
        return f"({a}*z + {b}) / ({c}*z + {d})"

    def __call__(self, z):
        """Apply this transformation to a complex or a CLine.
        """
        a, b, c, d = self.abcd
        if np.isscalar(z):
            if utils.isinf(z):
                return utils.safe_div(a, c)

            return utils.safe_div(a * z + b, c * z + d)

        elif isinstance(z, CLine):
            return z.transform_by(self)

        raise TypeError("A complex or a CLine is expected")

    @property
    def abcd(self):
        """Return a, b, c, d as a 1d array.
        """
        return self.flatten()

    @property
    def det(self):
        return self[0, 0] * self[1, 1] - self[0, 1] * self[1, 0]

    @property
    def inv(self):
        """Return the inverse transformation.
        """
        a, b, c, d = self.abcd
        return Mobius([d, -b, -c, a])

    def get_classification(self):
        """Return the type of this Mobius transformation.

        tr M strictly complex: loxodromic
        |tr M| > 2: hyperbolic
        |tr M| < 2: elliptic
        otherwise: parabolic
        """
        tr = self.trace()
        if utils.nonzero(tr.imag):
            return "loxodromic"

        if utils.greater_than(abs(tr), 2):
            return "hyperbolic"

        if utils.less_than(abs(tr), 2):
            return "elliptic"

        return "parabolic"

    def get_fixed_points(self):
        """Return the two fixed points of this transformation.
        For the parabolic case there is only one fixed point,
        and it's returned twice.

        z = M(z)

        Fix M = ((a - d) +/- sqrt((Tr M)^2 - 4)) / (2 * c)
        """
        a, b, c, d = self.abcd
        tr = a + d
        x = a - d
        y = 2 * c
        z = np.sqrt(tr * tr - 4)
        return utils.safe_div(x + z, y), utils.safe_div(x - z, y)

    @classmethod
    def parabolic(cls, p, dist):
        """Return a parabolic transformation with fixed point `p`
        and conjugates to z --> z + dist. In disk model.

        :param p: must be an ideal point on the unit circle.
        :param dist: can be any positive number.
        """
        assert utils.equal(abs(p), 1), \
            "The fixed point of a parabolic transformation must be ideal."
        # use an isometry with the upper half space model to conjugate
        # on the pure translation `z --> z + dist`.
        T = cls.disk_to_uhs(p, 'to_inf')
        return T.inv @ cls([1, dist, 0, 1]) @ T

    @classmethod
    def elliptic(cls, p, angle):
        """Return an elliptic transformation with fixed point `p`
        and conjugates to the rotation `z --> e^{ia}z`. In disk model.

        :param p: must be a point inside the unit disk.
        :param angle: can be any real number.
        """
        assert utils.less_than(abs(p), 1), \
            "The fixed point of an elliptic transformation must be inside the disk."
        a = complex(np.cos(angle), np.sin(angle))
        T = cls.translation(p, 0)
        R = Mobius([a, 0, 0, 1])
        return T.inv @ R @ T

    @classmethod
    def translation(cls, p1, p2):
        """Return a (parabolic) pure translation that moves `p1` to `p2`.
        In disk model. Such a transformation has the form

        z --> (z + P) / (P.conjugate()*z + 1)

        We can substitute `p1` and `p2` to solve for `P`.

        :param p1, p2: points that are both inside the unit disk.
        """
        assert utils.less_than(abs(p1), 1) and utils.less_than(abs(p2), 1), \
            "Two points inside the unit disk are expected"
        A = p2 - p1
        B = p1 * p2
        P = (A + B * A.conjugate()) / (1 - utils.norm2(B))
        T = cls([1, P, P.conjugate(), 1])
        return T

    @classmethod
    def hyperbolic(cls, p1, p2, scale):
        """Return a hyperbolic transformation with fixed points `p1` and `p2`,
        and which conjugates to the scale `z --> s*z`. In disk model.

        :param p1, p2: points that are both ideal.
        :param scale: can be any positive number.
        """
        assert utils.equal(abs(p1), 1) and utils.equal(abs(p2), 1), \
            "The fixed points of a hyperbolic transformation must be both ideal"

        T = cls([-p1.conjugate() * 1j, 1j, -p2.conjugate(), 1])
        m = cls([scale, 0, 0, 1])
        return T.inv @ m @ T

    @classmethod
    def disk_to_uhs(cls, p, option='to_inf'):
        """Return an isometry that maps the disk model to the
        upper half space model, which also maps an ideal point
        `p` to the infinity.
        """
        q = p.conjugate()
        if option == 'to_inf':
            return cls([1j * q, 1j, -q, 1])
        else:
            raise ValueError(f"unknow option: {option}")
