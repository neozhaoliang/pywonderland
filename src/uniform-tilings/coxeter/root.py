"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for holding the data of a root of a Coxeter group
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""


class Root(object):
    def __init__(self, coords=(), index=None, mat=None):
        """
        :param coords : coefficients of this root as a linear combination of simple roots.
        :param index : an integer, the index of this root.
        :param mat: matrix of the reflection of this root.
        """
        self.coords = coords
        self.index = index
        self.mat = mat
        # reflection by simple roots: {s_i(α), i=0, 1, ...}
        self.reflections = [None] * len(self.coords)

    def __eq__(self, other):
        """
        Check if two roots are equal, assume they are in the same root system.
        """
        if isinstance(other, Root):
            return all(self.coords == other.coords)
        return False
