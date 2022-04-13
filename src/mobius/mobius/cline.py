import numpy as np
from . import utils


class CLine(np.ndarray):

    """
    Use a 2x2 complex Hermite matrix to represent a generalized
    circle (a straight line or a circle) in the extended complex plane.

    Such circles satisfy

        |z - center| = r

    Which can be expanded to

    (z * z.conj - z * center.conj - z.conj * center + center * center.conj - r^2) = 0

    Upon multiplication by a real number A, we have

        A * z * z.conj + B * z + C * z.conj + D = 0

    Where
    A is any real number
    B = -A * center.conj
    C = -A * center = B.conj
    D = A * center * center.conj - A * r^2
    """

    def __new__(cls, data=(1, 0, 0, 0)):
        return np.array(data, dtype=complex).reshape(2, 2).view(cls)

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
        a, b, c, d = self.abcd
        return CLine([d, -b, -c, a]) / self.det

    def get_classification(self):
        """
        Use the `det` to determine which type of shape this Cline is:

        A != 0:
            det < 0: Real Circle
            det = 0: Point Circle
            det > 0: Imaginary Circle
        A = 0:
            det < 0: Straight Line
            det = 0: Not a Circle
            det > 0: Impossible
        """
        det = self.det
        a, _, _, _ = self.abcd
        if utils.nonzero(a):
            if utils.less_than(det.real, 0):
                return "circle"
            elif utils.iszero(det.real):
                return "point"
            else:
                return "image_circle"

        else:
            if utils.less_than(det.real, 0):
                return "line"
            elif utils.iszero(det.real):
                return "not_circle"
            else:
                return "invalid"

    def get_params(self):
        """
        If this is a circle, return ('circle', center, radius)
            |z - center| = radius

        If this is a point, return ('point', center, 0)

        If this is a line, return ('line', normal, offset)
            normal.real * x + normal.imag * y = offset

        If this is an imaginary circle, return ('imag_circle', center, radius)
            |z - center| = radius, radius is complex

        Otherwise, return ('not_circle', None) or ('invalid', None)
        """
        a, b, c, d = self.abcd
        cline_type = self.get_classification()
        if cline_type == "circle":
            center = -c / a.real
            k = utils.norm2(center) - d.real / a.real
            radius = np.sqrt(k)
            return ("circle", center, radius)

        elif cline_type == "point":
            center = -c / a
            return ("point", center, 0)

        elif cline_type == "image_circle":
            raise NotImplementedError("imaginary circle encountered")

        elif cline_type == "line":
            return ("line", c, (-d / 2).real)

        else:
            return (cline_type, None, None)

    @classmethod
    def from_circle(cls, center, radius):
        center = complex(center)
        A = 1
        B = -center.conjugate()
        C = -center
        D = center * center.conjugate() - radius * radius
        return cls([A, B, C, D])

    @classmethod
    def from_line(cls, normal, offset):
        k = abs(normal)
        assert utils.nonzero(k), "Degenerate normal vector encountered"
        offset /= k
        normal /= k
        return cls([0, normal.conjugate(), normal, -offset * 2])

    def transform_by(self, M):
        """Return the CLine transformed by a given Mobius transformation.

            C' = M.inv.T * C * M.inv.conj
        """
        M_inv = M.inv
        M_inv_T = M_inv.T
        M_inv_conj = M_inv.conj()
        # make sure return a CLine, not a Mobius transformation.
        return CLine(M_inv_T) @ self @ CLine(M_inv_conj)

    def reflect(self, other):
        """Use `self` as mirror to reflect another complex or a CLine.
        """
        H = CLine([0, -1, 1, 0]) @ self
        if np.isscalar(other):
            x, y = H @ np.array([other.conjugate(), 1])
            return utils.safe_div(x, y)

        if isinstance(other, CLine):
            H_inv = H.inv
            return H_inv.T.conj() @ other @ H_inv

        raise TypeError("A complex or a CLine is expected")

    def __call__(self, other):
        return self.reflect(other)
