from dataclasses import dataclass, field
import numpy as np
import sympy as sp


Qsym = sp.zeros(4)
Qsym[0, 1] = Qsym[1, 0] = sp.Rational(1, 2)
Qsym[2, 2] = Qsym[3, 3] = -1
Qnp = np.array(Qsym).astype(np.float64)


def reflect_numpy(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    return u + 2.0 * (u @ Qnp @ v) * v


def reflect_sympy(u: sp.Matrix, v: sp.Matrix) -> sp.Matrix:
    uv = (u * Qsym * v.T)[0]
    return sp.simplify(u + 2 * uv * v)


@dataclass(frozen=True)
class Circle:
    v_numpy: np.ndarray
    v_sympy: sp.Matrix = field(default=None, repr=False)

    def _key(self):
        """Get a hashable key for the circle.
        Since the same circle may be generated multiple times by different
        reflection paths, and floating-point errors cause them to be very
        close to each other, we need a looser threshold to determine
        whether two circles are identical.
        """
        eps = 1e-12
        digits = 8
        if np.all(np.abs(self.v_numpy) < eps):
            return (0, 0, 0, 0)

        for x in self.v_numpy:
            if abs(x) >= eps:
                v = self.v_numpy / abs(x)
                if x < 0:
                    v = -v
                return tuple(np.round(v, digits))

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        if not isinstance(other, Circle):
            return NotImplemented
        return self._key() == other._key()

    def reflect(self, other, do_sympy=True):
        new_np = reflect_numpy(self.v_numpy, other.v_numpy)
        new_sym = None
        if do_sympy and self.v_sympy is not None and other.v_sympy is not None:
            new_sym = reflect_sympy(self.v_sympy, other.v_sympy)
        return Circle(v_numpy=new_np, v_sympy=new_sym)

    def to_geometry(self):
        bhat, b, bx, by = self.v_numpy
        if abs(b) < 1e-14:
            return ("line", (bhat * bx) / 2.0, (bhat * by) / 2.0, -by, bx)
        return ("circle", bx / b, by / b, b)
