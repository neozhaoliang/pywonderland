class Root(object):

    """Class for holding the data of a root in the root system of a Coxeter group.
    """

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
        """Check if two roots are equal, assuming they are in the same root syste.
        """
        if isinstance(other, Root):
            return all(self.coords == other.coords)
        return False
