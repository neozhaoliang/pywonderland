"""
A class for handling matrices with algebraic integer entries.
"""
import numpy as np
from integers import lcm
from algebraic_integers import AlgebraicInteger as aint
from polynomial import IntPolynomial as intpoly


class Matrix(object):

    def __init__(self, base, mat):
        """
        `base`: a monic irreducible polynomic in Z[x].
        `mat`:  a symmetric 2d matrix whose entries are algebraic integers.
        """
        self.base = base
        self.M = mat
        self.dim = len(mat)

    def __str__(self):
        return str(self.M)

    def __getitem__(self, items):
        return self.M.__getitem__(items)

    def __mul__(self, other):
        """
        Multiply with another matrix or a vector of algebraic integers.
        """
        if isinstance(other, Matrix) and self.base == other.base:
            return Matrix(self.base, np.dot(self.M, other.M))
        else:
            return np.dot(self.M, other)

    def is_identity(self):
        """Check whether this is the identity matrix."""
        for i in range(self.dim):
            # diagonal elements == 1
            a = self[i][i]
            if a.p != 1:
                return False
            # non-diagonal elements == 0
            for j in range(i):
                a = self[i][j]
                if a != 0:
                    return False
        return True

    @classmethod
    def cartan_matrix(cls, coxeter_matrix):
        M = coxeter_matrix
        dim = len(M)

        # C is the Cartan matrix
        C = np.zeros_like(M).astype(object)

        # m is the lcm of all 2*m[i][j]'s,
        # all entries of the Cartan matrix are cyclotomic integers
        # in the m-th cyclotomic field.
        m = 2
        for i in range(dim):
            for j in range(i):
                m = lcm(m, 2 * M[i][j])

        # b is the m-th cyclotomic polynomial.
        b = intpoly.cyclotomic(m)

        # diagonal entries in the Cartan matrix.
        for i in range(dim):
            C[i][i] = aint(b, 2)

        # non-diagonal entries in the Cartan matrix.
        for i in range(dim):
            for j in range(i):
                # C[i][j] = -(zeta_{2*mij} + zeta^{-1}_{2*mij})
                # zeta_{2*mij} = zeta_m^{m/(2*mij)}
                z = [0] * m
                mij2 = 2 * M[i][j]
                if mij2 > 0:
                    z[m // mij2] = -1
                    z[m - m // mij2] = -1
                    zeta = aint(b, z)
                    C[i][j] = C[j][i] = zeta
                else:
                    C[i][j] = C[j][i] = aint(b, -2)

        return cls(b, C)

    @classmethod
    def reflection_matrix(cls, C, k):
        """
        Return a matrix R whose (i,j)-entry is the coefficient of the
        simple root a_i in the action of r_k on another simple root a_j:
        r_ka_j = a_j - C[k][j]a_k.
        """
        dim = C.dim
        R = np.zeros_like(C.M).astype(object)
        b = C.base

        for j in range(dim):
            if j == k:
                for i in range(dim):
                    if i == k:
                        R[i][j] = aint(b, -1)
                    else:
                        R[i][j] = aint(b, 0)
            else:
                for i in range(dim):
                    if i == j:
                        R[i][j] = aint(b, 1)
                    elif i == k:
                        R[i][j] = -C[k][j]
                    else:
                        R[i][j] = aint(b, 0)
        return cls(b, R)


def test():
    symmat = [[1, 3, 2],
              [3, 1, 7],
              [2, 7, 1]]

    cox = Matrix.cartan_matrix(symmat)
    print(cox)
    ref = Matrix.reflection_matrix(cox, 1)
    print(ref)
    b = intpoly.cyclotomic(84)
    intlist = [aint(b, 1) for _ in range(3)]
    print(cox * intlist)


if __name__ == "__main__":
    test()
