# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Compute the reflection table of minimal roots of a Coxeter group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script computes the reflection table of minimal roots of a Coxeter group
as discovered by Brink and Howlett [1]. All computations are done in the ring
of algebraic integers in the cyclotomic field, which is isomorphic to Z[x]/Φ(x)
for some cyclotomic polynomial Φ(x), hence only arithmetic of integers are involved.
This approach has the advantage that the computation is exact and floating rounding
errors can be avoided.

The main part of this script is the function `get_reflection_table`, whose input is a
Coxeter matrix (a symmetric matrix with integer entries and the diagonals are all 1)
and the output is a 2d array. The rows of this array is indexed by the minimal roots
and columns are indexed by the simple reflections.

For example:
>>> cox_mat = [[1, 3, 4],
               [3, 1, 3],
               [4, 3, 1]]
>>> table = get_reflection_table(cox_mat)
>>> table
>>> array([[-1, 3, 4],
           [3, -1, 5],
           [6, 5, -1],
           [1, 0, None],
           [4, None, 0],
           [None, 2, 1],
           [2, None, 6]], dtype=object)

Let α_i be the i-th minimal root and s_j be the reflection by the j-th simple root, then

1. table[i][j] = -1 if and only if s_j(α_i) is a negative root. This happens only
   when α_i is also a simple root and i = j.
2. table[i][j] = None if and only if s_j(α_i) is a positive root but not minimal.
3. table[i][j] = k (k >= 0) if and only if s_j(α_i) is the k-th minimal root.

So there are 7 minimal roots for the (3, 4, 3) triangle group.

The two classes `IntPolynomial` and `AlgebraicInteger` are mainly for handling arithmetic
of algebraic integers in cyclotomic fields (they are the coefficients of a root as a linear
combination of simple roots).

For the cases that there are infinities in the Coxeter matrix, simply replace them with -1.
For example for the Coxeter group

    G = <s, t | s^2 = t^2 = 1>

The Coxeter matrix of G is [[1, +inf], [+inf, 1]], replace +inf with -1 one get
[[1, -1], [-1, 1]], hence

>>> cox_mat = [[1, -1], [-1, 1]]
>>> table = get_reflection_table(cox_mat)
>>> table
>>> array([[-1, None],
           [None, -1]], dtype=object)

References:

    [1]. B. Brink and R. Howlett, A fniteness property and an automatic structure
         for Coxeter groups, Math. Ann. 296 (1993), 179-190.

    [2]. Bill Casselman's articles about Coxeter groups at

            "https://www.math.ubc.ca/~cass/research/publications.html"

:copyright (c) 2019 by Zhao Liang.
"""
from collections import defaultdict, deque
from copy import copy
from itertools import zip_longest
import numpy as np


def decompose(n):
    """Decompose an integer `n` into a product of primes.
       The result is stored in a dict {prime: exponent}.
       This function is used for generating cyclotomic polynomials.
    """
    n = abs(n)
    primes = defaultdict(int)
    # factor 2
    while n % 2 == 0:
        primes[2] += 1
        n = n // 2
    # odd prime factors
    for i in range(3, int(n**0.5) + 1, 2):
        while n % i == 0:
            primes[i] += 1
            n = n // i
    # if n itself is prime
    if n > 2:
        primes[n] += 1
    return primes


def discard_trailing_zeros(a):
    """Discard traling zeros in an array `a`.
    """
    i = len(a) - 1
    while (i > 0 and a[i] == 0):
        i -= 1
    return a[:i+1]


class IntPolynomial(object):

    """An `IntPolynomial` is a polynomial with integer coefficients. It's represented by a
       tuple of integers and can be initialized either by an integer or by an iterable that
       can be converted to a tuple of integers.
       Note trailing zeros are discarded when initialing.
    """

    def __init__(self, coef=0):
        if isinstance(coef, int):
            self.coef = (coef,)
        else:
            self.coef = discard_trailing_zeros(tuple(coef))
        # degree of this polynomial
        self.D = len(self.coef) - 1

    def __str__(self):
        return "IntPolynomial" + str(self.coef)

    def __getitem__(self, items):
        return self.coef[items]

    def __bool__(self):
        """Check whether this is a zero polynomial. Note a non-zero constant
           is not a zero polynomial.
        """
        return self.D > 0 or self[0] != 0

    def __neg__(self):
        return IntPolynomial(-x for x in self)

    def valid(self, g):
        """Check input for polynomial operations.
        """
        if not isinstance(g, (int, IntPolynomial)):
            raise ValueError("Only integers and IntPolynomials are allowed for polynomial operations.")
        if isinstance(g, int):
            g = IntPolynomial(g)
        return g

    def __add__(self, g):
        """Add a polynomial or an integer.
        """
        g = self.valid(g)
        return IntPolynomial(x + y for x, y in zip_longest(self, g, fillvalue=0))

    __iadd__ = __radd__ = __add__

    def __sub__(self, g):
        g = self.valid(g)
        return IntPolynomial(x - y for x, y in zip_longest(self, g, fillvalue=0))

    __isub__ = __sub__

    def __rsub__(self, g):
        return -self + g

    def __eq__(self, g):
        if not isinstance(g, (int, IntPolynomial)):
            return False
        return not bool(self - g)

    def __mul__(self, g):
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
        """Return the monomial a*x**n.
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


class AlgebraicInteger(object):

    """An algebraic integer is a root of an irreducible monic polynomial with integer coefficients.
       It's represented by two `IntPolynomial`s　`base` and `poly`: `base` is an irreducible monic
       polynomial, which determines the algebraic number field F (F = Q(α) and α is any root of `base`)
       that our `AlgebraicInteger`s lie in. In this program `base` is always a cyclotomic polynomial,
       so α is a primitive n-th root of unity and the ring of algebraic integers in F equals Z[α]
       (see any textbook on algebraic number theory). Any algebraic integer in Z[α] can be represented
       by a second `IntPolynomial` `poly`.
    """

    def __init__(self, base, p):
        """`base` is an instance of `IntPolynomial`, it must be irreducible and monic.
           But we do not check it here since we always use a cyclotomic polynomial for it.
           `p` can be either an integer of an instance of `IntPolynomial`.
        """
        self.base = base
        if isinstance(p, int):
            p = IntPolynomial(p)
        self.poly = p % self.base

    def __str__(self):
        return "AlgebraicInteger" + "(base={}, poly={})".format(self.base, self.poly)

    def __hash__(self):
        """The hash of an `AlgebraicInteger` is simply the hash of the tuple of its coefficients.
        """
        return hash(self.poly.coef)

    def __eq__(self, beta):
        """For speed considerations we always assume `beta` is an (algebraic) integer
           in the same cyclotomic field.
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


class Root(object):

    def __init__(self, coords=(), index=None, mat=None):
        """`coords`: coefficients of this root as a linear combination of simple roots.
           `index`: an integer.
           `mat`: matrix of the reflection of this root.
        """
        self.coords = coords
        self.index = index
        self.mat = mat
        # reflection by simple roots: {s_i(α), i=0, 1, ...}
        self.reflections = [None] * len(self.coords)

    def __eq__(self, other):
        if isinstance(other, Root):
            return all(self.coords == other.coords)
        return False


def is_identity(M):
    """Check if a matrix `M` is the identity matrix. Here `M` is assumed to be a
       square numpy ndarray and its entries are integers or `AlgebraicIntegers`
       with the same base (so they lie in the same number field).
    """
    n = len(M)
    return (M == np.eye(n, dtype=int)).all()


def get_cartan_matrix(cox_mat):
    """`cox_mat` is the Coxeter matrix with entries m[i][j].
       Return the Cartan matrix with entries -2*cos(PI/m[i][j]).
    """
    M = np.array(cox_mat, dtype=np.int)
    C = np.zeros_like(M).astype(object)  # the Cartan matrix
    rank = len(M)
    m = np.lcm.reduce(2 * M.ravel())  # all entries of the Cartan matrix lie in the m-th cyclotomic field
    b = IntPolynomial.cyclotomic(m)
    # diagonal entries
    for i in range(rank):
        C[i][i] = AlgebraicInteger(b, 2)
    # non-diagonal entries
    for i in range(rank):
        for j in range(i):
            z = [0] * m
            k = 2 * M[i][j]
            if k > 0:
                z[m // k] = -1
                z[m - m // k] = -1
                zeta = AlgebraicInteger(b, IntPolynomial(z))
                C[i][j] = C[j][i] = zeta
            else:
                C[i][j] = C[j][i] = AlgebraicInteger(b, -2)
    return C, b


def get_simple_reflection(C, k):
    """Return the reflection matrix for the k-th simple root.
       Here `C` is the Cartan matrix.
    """
    S = np.eye(len(C), dtype=object)
    S[k] -= C[k]
    return S


def get_reflection_table(cox_mat):
    """Get the reflection table of minimal roots of a Coxeter group.
       `cox_mat` is the Coxeter matrix of a Coxeter group.
       Return a 2d array `table` whose rows are indexed by the set of
       minimal roots and columns are indexed by the simple reflections.
    """
    M = np.array(cox_mat, dtype=np.int)  # Coxeter matrix
    if not (M == M.T).all():
        raise ValueError("A symmetric matrix is expected")

    C, base = get_cartan_matrix(M)  # Cartan matrix
    rank = len(M)
    R = [get_simple_reflection(C, k) for k in range(rank)]  # simple reflections
    max_order = np.amax(M)
    # a tricky way to store the set of m_ij's in the Coxeter matrix
    mset = 0
    for k in M.ravel():
        if k > 2:
            mset |= (1 << k)

    # a root is in the queue if and only if its coords are known but its reflections are not.
    queue = deque()
    # a root is appended to the list when all its information are known
    roots = []
    count = 0  # current number of minimal roots
    MINUS = Root(index=-1)  # the negative root

    # generate all simple roots
    for i in range(rank):
        coords = [AlgebraicInteger(base, 0) if k != i else AlgebraicInteger(base, 1) for k in range(rank)]
        s = Root(coords=coords, index=count, mat=R[i])
        s.reflections = [None if k != i else MINUS for k in range(rank)]
        queue.append(s)
        roots.append(s)
        count += 1

    # search from the bottom of the root graph to find all other minimal roots of depth >= 2
    while queue:
        alpha = queue.popleft()
        for i in range(rank):
            if alpha.reflections[i] is None:
                beta = Root(coords=np.dot(R[i], alpha.coords))

                # if beta is already a known minimal root.
                # Note the trap here: don't use "if beta in roots:" !
                for r in roots:
                    if beta == r:
                        alpha.reflections[i] = r
                        r.reflections[i] = alpha
                        break

                # beta is a new root, is it minimal?
                # it's is minimal iff its reflection and s_i generate a finite group
                else:
                    is_minroot = False
                    S = np.dot(alpha.mat, R[i])
                    X = S
                    for j in range(2, max_order + 1):
                        X = np.dot(S, X)
                        if is_identity(X) and ((1 << j) & mset != 0):
                            is_minroot = True
                            break

                    # beta is minimal
                    if is_minroot:
                        alpha.reflections[i] = beta
                        beta.reflections[i] = alpha
                        beta.mat = np.dot(R[i], S)
                        beta.index = count
                        count += 1
                        queue.append(beta)
                        roots.append(beta)
                        print("Current number of minimal roots: {}".format(len(roots)), end="\r")
    print("\n{} minimal roots in total".format(len(roots)))
    # finally put all reflection information into a 2d array
    table = np.zeros((len(roots), rank)).astype(object)
    for alpha in roots:
        k = alpha.index
        for i, beta in enumerate(alpha.reflections):
            symbol = beta.index if beta is not None else None
            table[k][i] = symbol

    return table
