import numpy as np

from .vector import Vec2


def reflect_about_line(p, normal, offset=0):
    """
    Reflects a point p about a line defined by a normal vector and an offset.
    """
    return p - 2 * (np.dot(p, normal) - offset) * normal


def triangle_to_cartesian(x, y):
    """Converts a vertex in the triangle lattice to cartesian coordinates.
    The origin is at the bottom left corner of a regular triangle.
    The two basis vectors are Vec2(1, 0) and Vec2(1/2, sqrt(3)/2).
    """
    return Vec2(x + y / 2, y * 3**0.5 / 2)


def get_dihedral_group_elements(n):
    """Returns the elements of the dihedral group D_n as a list of functions.
    For the affine A_1 (D_inf) we only return the first four elements.
    """
    assert n in (-1, 2, 3), "Only dihedral groups for n=-1, 2 or 3 are supported."
    if n == -1:
        n1 = Vec2(1, 0)
        n2 = Vec2(1, 0)
        offset1 = -1
        offset2 = 1
    else:
        n1 = Vec2(0, 1)
        theta = np.pi / n
        n2 = Vec2(np.sin(theta), -np.cos(theta))
        offset1 = offset2 = 0

    s0 = lambda p: Vec2(p)
    s1 = lambda p: reflect_about_line(p, n1, offset1)
    s2 = lambda p: reflect_about_line(p, n2, offset2)
    s2s1 = lambda p: s2(s1(p))
    s1s2s1 = lambda p: s1(s2s1(p))
    s1s2 = lambda p: s1(s2(p))
    if n in (-1, 2):
        return [s0, s2, s2s1, s1]
    else:
        return [s0, s2, s2s1, s1s2s1, s1s2, s1]


D_inf = get_dihedral_group_elements(-1)
D2 = get_dihedral_group_elements(2)
D3 = get_dihedral_group_elements(3)
