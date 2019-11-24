# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Compute the reflection table of minimal roots of a Coxeter group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This script computes the reflection table of minimal roots of a Coxeter
group as discovered by Brink and Howlett [1]. All computations are done
in the ring of algebraic integers in the cyclotomic field which is
isomorphic to Z[x]/Φ(x) for some cyclotomic polynomial Φ(x), hence only
arithmetic of integers are involved. This approach has the advantage that
the computation is exact and floating rounding errors can be avoided.

The main part of this script is the function `get_reflection_table` whose
input is a Coxeter matrix (a symmetric matrix with integer entries and the
diagonals are all 1) and the output is a 2d array. The rows of this array are
indexed by the minimal roots and columns are indexed by the simple reflections.

For example the triangle group (3, 4, 3):
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

Let α_i be the i-th minimal root and s_j be the reflection by the j-th simple
root, then

1. table[i][j] = -1 if and only if s_j(α_i) is a negative root. This happens
   only when α_i is also a simple root and i = j.
2. table[i][j] = None if and only if s_j(α_i) is a positive root but not minimal.
3. table[i][j] = k (k >= 0) if and only if s_j(α_i) is the k-th minimal root.

So there are 7 minimal roots for this group.

For the cases that there are infinities in the Coxeter matrix, simply replace
them with -1. For example for the infinite dihedral group

    G = <s, t | s^2 = t^2 = 1>

The Coxeter matrix of G is [[1, +inf], [+inf, 1]], replace +inf with -1 one get
[[1, -1], [-1, 1]], hence

>>> cox_mat = [[1, -1], [-1, 1]]
>>> table = get_reflection_table(cox_mat)
>>> table
>>> array([[-1, None],
           [None, -1]], dtype=object)

So the only minimal roots of G are the two simple roots.

References:

    [1]. B. Brink and R. Howlett, A fniteness property and an automatic structure
         for Coxeter groups, Math. Ann. 296 (1993), 179-190.

    [2]. Bill Casselman's articles about Coxeter groups at

            "https://www.math.ubc.ca/~cass/research/publications.html"
"""
from collections import deque
import numpy as np
from .integer import lcm
from .polynomial import IntPolynomial
from .algebraic import AlgebraicInteger
from .root import Root


def is_identity(M):
    """Check if a matrix `M` is the identity matrix. Here `M` is assumed to be a
       square numpy ndarray and its entries are integers or `AlgebraicIntegers`
       with the same base (so they lie in the same number field).
    """
    n = len(M)
    return (M == np.eye(n, dtype=int)).all()


def get_cartan_matrix(cox_mat):
    """`cox_mat` is the Coxeter matrix with entries m[i][j],
       return the Cartan matrix with entries -2*cos(PI/m[i][j]),
       note the entries are all algebraic integers!
    """
    M = np.array(cox_mat, dtype=np.int)
    C = np.zeros_like(M).astype(object)  # the Cartan matrix
    rank = len(M)
    # all entries of the Cartan matrix lie in the m-th cyclotomic field
    m = 2
    for k in 2 * M.ravel():
        m = lcm(m, k)
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

                else:
                    # beta is a new root, is it minimal?
                    # it's is minimal iff its reflection and s_i generate a finite group
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
