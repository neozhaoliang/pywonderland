"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This file contains a single `IntPolynomial` class for handling
arithmetic of polynomials with integer coefficients
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from itertools import zip_longest as lzip
from copy import copy
from integers import prime_factors


class IntPolynomial(object):

    def __init__(self, coef=0):
        """
        An `IntPolynomial` can be initialized either by an integer, or by any iterable
        that can be converted to a list of integers.
        The trailing zeros in the coefficients are also trimmed when its initialized.
        Note all operations here also work for floating coefficients, but we restrict
        to integer case for easy debug when doing algebraic integer ring arithmetics.
        """
        if isinstance(coef, int):
            self.coef = (coef,)
        elif hasattr(coef, "__iter__") or hasattr(coef, "__getitem__"):
            coef = tuple(coef)
            if not all(isinstance(x, int) for x in coef):
                raise ValueError("Non-integer encountered in coefficients: {}".format(coef))
            self.coef = self.trim(coef)
        else:
            raise ValueError("cannot initialize a polynomial by this input: {}".format(coef))
        # degree of this polynomial
        self.D = len(self.coef) - 1

    @staticmethod
    def trim(arr):
        """Discard trailing zeros in an array."""
        i = len(arr) - 1
        while (i > 0 and arr[i]== 0):
            i -= 1
        return arr[:i + 1]

    def __str__(self):
        return self.__class__.__name__ + str(self.coef)

    __repr__ = __str__

    def __getitem__(self, items):
        return self.coef.__getitem__(items)

    def __len__(self):
        return len(self.coef)

    def __bool__(self):  # if f
        """
        Check if this a zero polynomial, note a polynomial of degree 0 with a non-zero
        constant term is not a zero polynomial.
        """
        return self.D > 0 or self.coef[0] != 0

    def __neg__(self):  # -f
        return self.__class__(-x for x in self.coef)

    @classmethod
    def convert(cls, other):
        """
        Try to convert an object `other` to an `IntPolynomial.` Here `other` can be
        any object that can yield a list of integers, i.e. `other` implements the
        interface `__iter__` or `__getitem__`. This is because later in this program
        we want to add/multiply algebraic integers with `IntPolynomial`s.
        """
        if not isinstance(other, cls):
            try:
                other = cls(other)
            except:
                raise ValueError("This input is not supported for polynomial operations")
        return other

    def __add__(self, other):  # f + g
        other = self.convert(other)
        return self.__class__(x + y for x, y in lzip(self, other, fillvalue=0))

    __iadd__ = __radd__ = __add__

    def __sub__(self, other):  # f - g
        other = self.convert(other)
        return self.__class__(x - y for x, y in lzip(self, other, fillvalue=0))

    __isub__ = __sub__

    def __rsub__(self, other):  # g - f
        return -self + other

    def __eq__(self, other):  # f == g
        """Only `int` and `IntPolynomial` are allowed for comparison."""
        if isinstance(other, (int, self.__class__)):
            return not bool(self - other)
        else:
            return False

    def __mul__(self, other):  # f * g
        other = self.convert(other)
        d1, d2 = self.D, other.D
        result = [0] * (d1 + d2 + 1)
        for i in range(d1 + 1):
            for j in range(d2 + 1):
                result[i + j] += self[i] * other[j]
        return self.__class__(result)

    __imul__ = __rmul__ = __mul__

    @classmethod
    def monomial(cls, n, a):
        """Return the monomial a*x^n."""
        coef = [0] * (n + 1)
        coef[n] = a
        return cls(coef)

    def __divmod__(self, other):  # divmod(f, g)
        other = self.convert(other)
        if other[other.D] != 1:
            raise ValueError("The divisor must be a monic polynomial")

        d1 = self.D
        d2 = other.D
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
            f -= m * other

        return q, f

    def __mod__(self, other):  # f % g
        return divmod(self, other)[1]

    def __floordiv__(self, other):  # f // g
        return divmod(self, other)[0]

    @classmethod
    def cyclotomic(cls, n):
        r"""
        Return the cyclotomic polynomial \Phi_n(x) for the n-th primitive root of unity:

            \Phi_n(x) = \prod (x^{n/d}-1)^{\mu(d)},

        where \mu(d) is the Mobius function:
        \mu(d) = 0 iff d contains a square factor,
        \mu(d) = 1 iff d is a product of even number of different primes,
        \mu(d) = -1 iff d is a product of odd number of different primes.

        Examples:
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
        primes = list(prime_factors(n).keys())
        num_square_free_factors = 1 << len(primes)
        for k in range(num_square_free_factors):
            d = 1
            for i in range(len(primes)):
                if (k & (1 << i)) != 0:
                    d *= primes[i]
            m = cls.monomial(n//d, 1) - 1
            b = bin(k).count("1")
            if b % 2 == 0:
                f *= m
            else:
                g *= m
        return f // g


def test():
    """test polynomial arithmetics"""
    f = IntPolynomial((1, 1, 0))
    g = IntPolynomial((0, 1, 3, 3, 1))
    print("f = {}".format(f))
    print("g = {}".format(g))
    print("degree of f and g: {}, {}".format(f.D, g.D))
    print("f + 1: {}".format(f + 1))
    print("1 - g: {}".format(1 - g))
    print("2 * g: {}".format(2 * g))
    print("f + g: {}".format(f + g))
    print("f * g: {}".format(f * g))
    print("divmod(g, f): {}".format(divmod(g, f)))
    print("f == (1, 1): {}".format(f == (1, 1)))
    print("f == IntPolynomial((1, 1)): {}".format(f == IntPolynomial((1, 1))))
    for m in (8, 12, 14, 105):
        f = IntPolynomial.cyclotomic(m)
        print("{}-th cyclotomic polynomial: {}".format(m, f))

if __name__ == "__main__":
    test()
