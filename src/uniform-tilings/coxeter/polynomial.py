"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for handling arithmetic of polynomials in Z[x]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from itertools import zip_longest as lzip
from copy import copy
from .integer import decompose


class IntPolynomial(object):

    """
    A class for handling arithmetic of polynomials with integer coefficients.
    A polynomial is represented by a tuple of integers and can be initialized
    either by an integer or by an iterable that yields a tuple of integers.
    Note trailing zeros are discarded at the initializing stage.
    """

    def __init__(self, coef=0):
        if isinstance(coef, int):
            self.coef = (coef,)
        else:
            self.coef = self.discard_trailing_zeros(tuple(coef))
        # degree of this polynomial
        self.D = len(self.coef) - 1

    @staticmethod
    def discard_trailing_zeros(arr):
        """
        Discard traling zeros in an array.
        """
        i = len(arr) - 1
        while (i > 0 and arr[i] == 0):
            i -= 1
        return arr[:i+1]

    def __str__(self):
        return "IntPolynomial" + str(self.coef)

    def __getitem__(self, items):
        return self.coef[items]

    def __bool__(self):
        """
        Check whether this polynomial is zero.
        """
        return self.D > 0 or self[0] != 0

    def __neg__(self):
        return IntPolynomial(-x for x in self)

    @staticmethod
    def valid(g):
        """
        Check input for polynomial operations.
        """
        if not isinstance(g, (int, IntPolynomial)):
            raise ValueError("type {} not supported for polynomial operations".format(type(g)))
        if isinstance(g, int):
            g = IntPolynomial(g)
        return g

    def __add__(self, g):  # f + g
        """
        Addition with another polynomial or an integer.
        """
        g = self.valid(g)
        return IntPolynomial(x + y for x, y in lzip(self, g, fillvalue=0))

    __iadd__ = __radd__ = __add__

    def __sub__(self, g):  # f - g
        g = self.valid(g)
        return IntPolynomial(x - y for x, y in lzip(self, g, fillvalue=0))

    __isub__ = __sub__

    def __rsub__(self, g):
        return -self + g

    def __eq__(self, g):  # f == g
        if not isinstance(g, (int, IntPolynomial)):
            return False
        return not bool(self - g)

    def __mul__(self, g):  # f * g
        g = self.valid(g)
        d1, d2 = self.D, g.D
        h = [0] * (d1 + d2 + 1)
        for i in range(d1 + 1):
            for j in range(d2 + 1):
                h[i + j] += self[i] * g[j]
        return IntPolynomial(h)

    __imul__ = __rmul__ = __mul__

    @classmethod
    def monomial(cls, n, a):
        """
        Return the monomial a*x^n.
        """
        coef = [0] * (n + 1)
        coef[n] = a
        return cls(coef)

    def __divmod__(self, g):
        g = self.valid(g)
        d1 = self.D
        d2 = g.D
        if g[d2] != 1:
            raise ValueError("The divisor must be a monic polynomial")

        if d1 < d2:
            return IntPolynomial(0), self

        # if the divisor is a constant 1
        if d2 == 0:
            return self, IntPolynomial(0)

        f = copy(self)
        q = 0
        while f.D >= d2:
            m = self.monomial(f.D - d2, f[f.D])
            q += m
            f -= m * g

        return q, f

    def __mod__(self, g):
        return divmod(self, g)[1]

    def __floordiv__(self, g):
        return divmod(self, g)[0]

    @classmethod
    def cyclotomic(cls, n):
        r"""
        Return the cyclotomic polynomial \Phi_n(x) for the n-th primitive root of unity:

            \Phi_n(x) = \prod (x^{n/d}-1)^{\mu(d)},

        where d runs over all divisors of n and \mu(d) is the Mobius function:
        \mu(d) = 0 iff d contains a square factor.
        \mu(d) = 1 iff d is a product of even number of different primes.
        \mu(d) = -1 iff d is a product of odd number of different primes.

        Example:
        >>> f = IntPolynomial.cyclotomic(8)
        >>> f
        >>> IntPolynomial(1, 0, 0, 1)

        >>> f = IntPolynomial.cyclotomic(12)
        >>> f
        >>> IntPolynomial(1, 0, -1, 0, 1)
        """
        if n == 1:
            return cls((-1, 1))
        f = 1
        g = 1
        primes = list(decompose(n).keys())
        num_square_free_factors = 1 << len(primes)
        for k in range(num_square_free_factors):
            d = 1
            for i, e in enumerate(primes):
                if (k & (1 << i)) != 0:
                    d *= e
            m = cls.monomial(n // d, 1) - 1
            b = bin(k).count("1")
            if b % 2 == 0:
                f *= m
            else:
                g *= m
        return f // g
