from .polynomial import IntPolynomial


class AlgebraicInteger(object):

    """An algebraic integer is a root of an irreducible monic polynomial with
       integer coefficients. It's represented by two `IntPolynomial`s　`base`
       and `poly`: `base` is an irreducible monic polynomial, which determines
       the algebraic number field F (F = Q(α) and α is any root of `base`)
       that our `AlgebraicInteger`s lie in. In this program `base` is always a
       cyclotomic polynomial, so α is a primitive n-th root of unity and the
       ring of algebraic integers in F equals Z[α] (see any textbook on algebraic
       number theory). Any algebraic integer in Z[α] can be represented by a
       second `IntPolynomial` `poly`.
    """

    def __init__(self, base, p):
        """`base` is an instance of `IntPolynomial`, it must be irreducible
           and monic. But we do not check it here since we will always use a
           cyclotomic polynomial for it. `p` can be either an integer of an
           instance of `IntPolynomial`.
        """
        self.base = base
        if isinstance(p, int):
            p = IntPolynomial(p)
        self.poly = p % self.base

    def __str__(self):
        return "AlgebraicInteger" + "(base={}, poly={})".format(self.base, self.poly)

    def __hash__(self):
        """The hash of an `AlgebraicInteger` is simply the hash of its coefficients.
        """
        return hash(self.poly.coef)

    def __eq__(self, beta):
        """For speed considerations we always assume `beta` is an (algebraic)
           integer in the same cyclotomic field.
        """
        if isinstance(beta, int):
            return self.poly == beta
        return self.poly == beta.poly

    def __neg__(self):
        return AlgebraicInteger(self.base, -self.poly)

    def __add__(self, beta):
        if isinstance(beta, int):
            return AlgebraicInteger(self.base, self.poly + beta)
        return AlgebraicInteger(self.base, self.poly + beta.poly)

    __iadd__ = __radd__ = __add__

    def __sub__(self, beta):
        if isinstance(beta, int):
            return AlgebraicInteger(self.base, self.poly - beta)
        return AlgebraicInteger(self.base, self.poly - beta.poly)

    __isub__ = __sub__

    def __rsub__(self, beta):
        return -self + beta

    def __mul__(self, beta):
        if isinstance(beta, int):
            return AlgebraicInteger(self.base, self.poly * beta)
        return AlgebraicInteger(self.base, self.poly * beta.poly)

    __imul__ = __rmul__ = __mul__
