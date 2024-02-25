from fractions import Fraction

import numpy as np


def normalize(v):
    """
    Normalize a vector v.
    """
    return np.array(v) / np.linalg.norm(v)


def hdot(v, w):
    """
    Compute the hyperbolic dot product of two vectors v and w.
    """
    return np.dot(v[:-1], w[:-1]) - v[-1] * w[-1]


def is_ideal(v):
    """
    Check if a point v is ideal.
    """
    return np.isclose(hdot(v, v), 0)


def hnormalize(v):
    if is_ideal(v):
        return normalize(v[:-1])
    return v / np.sqrt(-hdot(v, v))


def get_coxeter_matrix(coxeter_diagram):
    """
    Get the Coxeter matrix from a given coxeter_diagram.
    The Coxeter matrix is square and entries are all integers,
    it describes the relations between the generators of the symmetry group.
    Here is the math: suppose two mirrors m_i, m_j form an angle p/q
    where p,q are coprime integers, then the two generator reflections
    about these two mirrors r_i, r_j satisfy (r_ir_j)^p = 1.

    Example:
    >>> coxeter_diagram = (3, 2, Fraction(5, 2))
    >>> get_coxeter_matrix(coxeter_diagram)
    >>> [[1, 3, 2],
         [3, 1, 5],
         [2, 5, 1]]

    Note that in general one cannot recover the Coxeter diagram from
    the Coxeter matrix since a star polytope may have the same Coxeter
    matrix with a convex one.
    """
    if len(coxeter_diagram) == 3:
        a12, a13, a23 = coxeter_diagram
        M = [[1, a12, a13], [a12, 1, a23], [a13, a23, 1]]
    elif len(coxeter_diagram) == 6:
        a12, a13, a14, a23, a24, a34 = coxeter_diagram
        M = [
            [1, a12, a13, a14],
            [a12, 1, a23, a24],
            [a13, a23, 1, a34],
            [a14, a24, a34, 1],
        ]
    else:
        raise ValueError("Three or six inputs are expected.")

    return np.array(M, dtype=int)


def get_point_from_distance(
    M,
    d,
    geometry,
    normalized=True,
):
    """
    Given the normal vectors of the mirrors stored as row vectors in `M`
    and a tuple of non-negative floats `d`, compute the vector `v` whose
    distance vector to the mirrors is `d` and choose whether to return
    its normalized version.
    """
    if geometry in ("spherical", "euclidean"):
        p = np.linalg.solve(M, d)
        if normalized:
            p = normalize(p)
    else:
        N = M.copy()
        N[:, -1] *= -1
        p = np.linalg.solve(N, d)
        if normalized:
            p = hnormalize(p)
    return p


def get_spherical_mirrors(coxeter_matrix):
    C = -np.cos(np.pi / coxeter_matrix)
    M = np.zeros_like(C)

    M[0, 0] = 1
    M[1, 0] = C[0, 1]
    M[1, 1] = np.sqrt(1 - M[1, 0] * M[1, 0])
    M[2, 0] = C[0, 2]
    M[2, 1] = (C[1, 2] - M[1, 0] * M[2, 0]) / M[1, 1]
    M[2, 2] = np.sqrt(abs(1 - M[2, 0] * M[2, 0] - M[2, 1] * M[2, 1]))
    if len(coxeter_matrix) == 4:
        M[3, 0] = C[0, 3]
        M[3, 1] = (C[1, 3] - M[1, 0] * M[3, 0]) / M[1, 1]
        M[3, 2] = (C[2, 3] - M[2, 0] * M[3, 0] - M[2, 1] * M[3, 1]) / M[2, 2]
        M[3, 3] = np.sqrt(
            abs(1 - M[3, 0] * M[3, 0] - M[3, 1] * M[3, 1] - M[3, 2] * M[3, 2])
        )
    return M


def get_euclidean_mirrors(coxeter_matrix):
    C = -np.cos(np.pi / coxeter_matrix)
    M = np.zeros_like(C)

    M[0, 0] = 1
    M[1, 0] = C[0, 1]
    M[1, 1] = np.sqrt(1 - M[1, 0] * M[1, 0])
    M[2, 0] = C[0, 2]
    M[2, 1] = (C[1, 2] - M[1, 0] * M[2, 0]) / M[1, 1]

    if len(coxeter_matrix) == 3:
        M[2, 2] = 1
    else:
        M[2, 2] = np.sqrt(abs(1 - M[2, 0] * M[2, 0] - M[2, 1] * M[2, 1]))
        M[3, 0] = C[0, 3]
        M[3, 1] = (C[1, 3] - M[1, 0] * M[3, 0]) / M[1, 1]
        M[3, 2] = (C[2, 3] - M[2, 0] * M[3, 0] - M[2, 1] * M[3, 1]) / M[2, 2]
        M[3, 3] = 1

    return M


def get_hyperbolic_mirrors(coxeter_matrix):
    """
    Get reflection mirrors for the 2D hyperbolic case.
    """
    C = -np.cos(np.pi / coxeter_matrix)
    inf_indices = np.where(coxeter_matrix == -1)
    C[inf_indices] = -1
    M = np.zeros_like(C)
    M[0, 0] = 1
    M[1, 0] = C[1, 0]
    M[1, 1] = np.sqrt(1 - M[1, 0] * M[1, 0])
    M[2, 0] = C[2, 0]
    M[2, 1] = (C[2, 1] - M[2, 0] * M[1, 0]) / M[1, 1]
    M[2, 2] = -np.sqrt(abs(M[2, 0] * M[2, 0] + M[2, 1] * M[2, 1] - 1))
    return M


def get_hyperbolic_honeycomb_mirrors(coxeter_matrix):
    """
    Get reflection mirrors for the 3D hyperbolic honeycomb case.
    """
    C = -np.cos(np.pi / coxeter_matrix)
    M = np.zeros_like(C)
    M[0, 0] = 1
    M[1, 0] = C[1, 0]
    M[1, 1] = np.sqrt(1 - M[1, 0] * M[1, 0])
    M[2, 0] = C[2, 0]
    M[2, 1] = (C[2, 1] - M[2, 0] * M[1, 0]) / M[1, 1]
    M[2, 2] = np.sqrt(abs(1 - M[2, 0] * M[2, 0] - M[2, 1] * M[2, 1]))
    M[3, 0] = C[3, 0]
    M[3, 1] = (C[3, 1] - M[3, 0] * M[1, 0]) / M[1, 1]
    M[3, 2] = (C[3, 2] - M[3, 0] * M[2, 0] - M[3, 1] * M[2, 1]) / M[2, 2]
    M[3, 3] = -np.sqrt(
        abs(M[3, 0] * M[3, 0] - M[3, 1] * M[3, 1] - M[3, 2] * M[3, 2] - 1)
    )
    return M


def project_affine(v):
    """
    Project a point in R^3 to a z=1 plane. We assume the z-component of
    v is already 1.
    """
    return v[:-1]


def project_poincare(v):
    """
    Project a point in H^n to H^{n-1}.
    It's the projection from hyperboloid to Poincare's disk.
    """
    if is_ideal(v):
        return normalize(v[:-1])
    return v[:-1] / (1 + v[-1])


def get_geometry_type(pqr):
    """
    Get the geometry type.
    """
    s = sum(Fraction(1, x) if x != -1 else 0 for x in pqr)
    if s > 1:
        return "spherical"
    if s == 1:
        return "euclidean"
    return "hyperbolic"


def is_degenerate(cox_mat, active):
    """
    Check if a 3d tiling defined by a triangle group
    (p, q, r) is degenerate.
    """
    p, q, r = cox_mat[0, 1], cox_mat[0, 2], cox_mat[1, 2]
    m0, m1, m2 = active

    # if no mirrors are active then it's degenerate
    if not any(active):
        return True
    # if p, q, r are all equal to 2 they must be all active
    if p == 2 and q == 2 and r == 2:
        return not all(active)
    # so at least one of p, q, r is > 2 and at least one mirror is active
    else:
        # if at least two of p, q, r are > 2 then it's not degenerate
        if (p > 2 and q > 2) or (p > 2 and r > 2) or (q > 2 and r > 2):
            return False
        # so exactly two of p, q, r are equal to 2
        elif p == 2 and q == 2:
            if not m0:
                return True
            else:
                return not any([m1, m2])
        elif p == 2 and r == 2:
            if not m1:
                return True
            else:
                return not any([m0, m2])
        else:
            if not m2:
                return True
            else:
                return not any([m0, m1])


# -------------------------------
# LaTeX formatting functions


def export_latex_array(words, symbol=r"s", cols=4):
    r"""
    Export a list words to latex array format.
    `cols` is the number of columns of the output latex array.

    Example: words = [(0, 1), (1, 2, 3) ...]
    Return: \begin{array}
            &s_0s_1 & s_1s_2s_3 & ... &\\
            ...
            \end{array}
    """

    def to_latex(word):
        return "".join(symbol + "_{{{}}}".format(i) for i in word)

    latex = ""
    for i, word in enumerate(words):
        if i > 0 and i % cols == 0:
            latex += r"\\" + "\n"
        latex += to_latex(word)
        if i % cols != cols - 1:
            latex += "&"

    return r"\begin{{array}}\n{{{}}}{}\n\end{{array}}".format("l" * cols, latex)


def pov_vector(v):
    """
    Convert a vector to POV-Ray format. e.g. (x, y, z) --> <x, y, z>.
    """
    return "<{}>".format(", ".join(str(x) for x in v))


def pov_vector_list(vectors):
    """
    Convert a list of vectors to POV-Ray format, e.g.
    [(x, y, z), (a, b, c), ...] --> <x, y, z>, <a, b, c>, ...
    """
    return ", ".join(pov_vector(v) for v in vectors)
