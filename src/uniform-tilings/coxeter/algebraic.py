"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for handling algebraic integers in cyclotomic fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As pointed out by Casselman, any root in the root system can be expressed
as a linear combination of simple roots with coefficients in the algebraic
integer ring of a cyclotomic field. We can use this fact to avoid floating
arithmetic in the process of searching for minimal roots.
"""
from .polynomial import IntPolynomial


class AlgebraicInteger(object):

    """
    An algebraic integer is a root of an irreducible monic polynomial with
    integer coefficients. It's represented by two `IntPolynomial`s: `base`
    and `poly`: `base` is an irreducible monic polynomial determines the
    algebraic number field F (F = Q(α) and α is any root of `base`) that
    our `AlgebraicInteger`s lie in. In this program `base` is always a
    cyclotomic polynomial, so α is a primitive n-th root of unity and the
    ring of algebraic integers in F equals Z[α] (see any textbook on algebraic
    number theory). Any algebraic integer in Z[α] can be represented by a
    second polynomial `poly`.
    """

    def __init__(self, base, p):
        """
        :param base: an instance of `IntPolynomial`, it must be irreducible and
            monic. But we do not check it here since we will always use a cyclotomic
            polynomial for it.

        :param p: an integer or an instance of `IntPolynomial`.
        """
        self.base = base
        if isinstance(p, int):
            p = IntPolynomial(p)
        self.poly = p % self.base

    def __str__(self):
        return "AlgebraicInteger" + "(base={}, poly={})".format(self.base, self.poly)

    def __hash__(self):
        """
        The hash of an algebraic integer is simply the hash of its coefficients.
        """
        return hash(self.poly.coef)

    def __eq__(self, beta):
        if isinstance(beta, int):
            return self.poly == beta
        if isinstance(beta, AlgebraicInteger):
            return self.poly == beta.poly
        return False

    def __neg__(self):
        return AlgebraicInteger(self.base, -self.poly)

    def __add__(self, beta):
        if isinstance(beta, int):
            return AlgebraicInteger(self.base, self.poly + beta)
        if isinstance(beta, AlgebraicInteger):
            return AlgebraicInteger(self.base, self.poly + beta.poly)
        raise ValueError(
            "type {} not supported for algebraic integer arithmetic".format(type(beta))
        )

    def __sub__(self, beta):
        return self + (-beta)

    def __rsub__(self, beta):
        return -self + beta

    def __mul__(self, beta):
        if isinstance(beta, int):
            return AlgebraicInteger(self.base, self.poly * beta)
        if isinstance(beta, AlgebraicInteger):
            return AlgebraicInteger(self.base, self.poly * beta.poly)
        raise ValueError(
            "type {} not supported for algebraic integer arithmetic".format(type(beta))
        )

    __isub__ = __sub__

    __iadd__ = __radd__ = __add__

    __imul__ = __rmul__ = __mul__
