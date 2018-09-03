"""
A single class for handling arithmetic of algebraic integers.
An algebraic integer is a complex number which is a root of
a monic polynomial in Z[x]. For a subfield F in the complex number
field, the algebraic integers in F form a ring. When F is generated
by a primitive root of unity then this ring equals Z[a], and F is
called a cyclotomic field. Here we only consider operations on
algebraic numbers in cyclotomic fields.
"""
from polynomial import IntPolynomial as intpoly


class AlgebraicInteger(object):
    """
    An algebraic integer is represented by two `IntPolynomials`:
    The first is called `base`, which is a monic irreducible polynomial
    in Z[x]. If `a` is one of its root then Z[a] is the algebraic integer
    ring in Q(a)/Q (this holds in our cyclotomic field case), so any element
    in Z[a] can be represented by a second polynomial in Z[x] which has degree
    <= the degree of `base`.
    """

    def __init__(self, base=(0, 1), p=0):
        """
        `p` and `base` are objects that can be converted to IntPolynomials,
        and `base` must be monic and irreducible. It's the caller's
        responsibility to make sure these requirements are satisfied.
        """
        base = intpoly.convert(base)
        p = intpoly.convert(p)
        self.base = base
        self.p = p % base

    def __str__(self):
        return self.__class__.__name__ + \
               "(" + str(self.p) + " in " + \
               "Z[x]/" + str(self.base) + ")"

    __repr__ = __str__

    def __getitem__(self, items):
        return self.p.__getitem__(items)

    def __eq__(self, other):
        """Comparison is restricted to only algebraic integers."""
        if not isinstance(other, self.__class__):
            return False
        return self.base == other.base and self.p == other.p

    def __bool__(self):
        return not self.p

    def __neg__(self):
        return AlgebraicInteger(self.base, -self.p)

    def convert(self, other):
        """
        Try to convert an object `other` to an `IntPolynomial`.
        If `other` is an algebraic integer then it's also required that
        it has the same base.
        """
        if isinstance(other, self.__class__) and self.base != other.base:
            raise ValueError("An algebraic integer with the same base is required")
        try:
            other = intpoly.convert(other)
        except:
            raise TypeError("Operation not supported for this type")
        return other

    def __add__(self, other):
        other = self.convert(other)
        return self.__class__(self.base, self.p + other)

    __iadd__ = __radd__ = __add__

    def __sub__(self, other):
        other = self.convert(other)
        return self.__class__(self.base, self.p - other)

    def __mul__(self, other):
        other = self.convert(other)
        return self.__class__(self.base, self.p * other)

    __imul__ = __rmul__ = __mul__


def test():
    """test algebraic integer arithmetics"""
    b = intpoly.cyclotomic(12)
    a1 = AlgebraicInteger(b, (0, 1))  # ε
    a2 = AlgebraicInteger(b, (0, 1, 1))  # ε + ε^2
    print("a1: {}".format(a1))
    print("a2: {}".format(a2))
    print("a1 + a2: {}".format(a1 + a2))
    print("a1 - a2: {}".format(a1 - a2))
    print("a1 * a2: {}".format(a1 * a2))


if __name__ == "__main__":
    test()
