"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Perfectly random lozenge tiling of a hexagon using
Propp-Wilson's "coupling from the past" algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import random
from .cftp import MonotoneMarkovChain


class LozengeTiling(MonotoneMarkovChain):

    r"""
    This class builds the "monotone" Markov chain structure on the set
    of lozenge tilings of an (a x b x c) hexagon. A tiling is represented
    by c+2 pairwise non-intersecting paths where the 0-th and (c+1)-th
    paths are fixed and are used for bounding the intermediate c paths.

    For a path system s, its k-th path s[k] starts at (k - 0.5) * dir(90),
    moves to the next vertex along (-30) or (+30) directions in each step,
    until it reaches the right vertical side of the hexagon.

    +y (+90 deg)
    |  ____
    | /    \
    |/      \
    |        \
    |         |
    |         |
    O\        |
      \      /
       \____/ 
        \
         +x (-30 deg)

    Each site has coordinates (x, y) where x is the shift along the (-30 deg)
    direction, y is the shift along the (+90 deg) direction. To find the affine
    transformation M that maps this to the cartesian coordinates, we will need

        M * (1, 0) = (sqrt(3)/2, -1/2)
        M * (0, 1) = (0, 1)

    Hence M is given by M * (x, y) = (sqrt(3)/2 * x, y - x/2)
    """

    def __init__(self, size):
        """
        :size: a tuple of three integers, these are the side lengths
        of the hexagon.
        """
        self.size = size

    def min_max_states(self):
        """
        Return the minimum and maximum tilings. From a bird's view,
        the minimum tiling is the one that correspondes to a room filled
        full of boxes and the maximum tiling is the one that correspondes
        to an empty room.
        """
        a, b, c = self.size
        s0 = [
            [max(j - a, 0) if k == 0 else k + min(j, b) for j in range(a + b + 1)]
            for k in range(c + 2)
        ]
        s1 = [
            [c + 1 + min(j, b) if k == c + 1 else k + max(j - a, 0) for j in range(a + b + 1)]
            for k in range(c + 2)
        ]
        return s0, s1

    def new_random_update(self):
        """
        Return a new update operation.
        An operation is specified by a tuple of three integers (k, j, dy):
        1. k for choosing a random path in the path system (excluding the
           two auxiliary paths, hence the index of the path lies between 1 and c)
        2. j for choosing a random site inside this path (excluding the two ends
           of this path, hence the index of the site lies between 1 and a + b - 1)
        3. dy for choosing a random flip (up or down)
        """
        a, b, c = self.size
        return (
            random.randint(1, c),  # a random path
            random.randint(1, a + b - 1),  # a random position in this path
            random.randint(0, 1),
        )  # a random direction (up or down)

    def update(self, state, operation):
        """Update a state by a random update operation.
        """
        s = state
        k, j, dy = operation
        # try to push up
        if dy == 1:
            if s[k][j - 1] == s[k][j] < s[k][j + 1] < s[k + 1][j]:
                s[k][j] += 1
        # try to push down
        else:
            if s[k - 1][j] < s[k][j - 1] < s[k][j] == s[k][j + 1]:
                s[k][j] -= 1

    def get_tiles(self, state):
        """
        Return the vertices of the lozenges in the tiling corresponding
        to a given path system `state`.
        """
        s = state
        a, b, c = self.size
        verts = {"L": [], "R": [], "T": []}
        for k in range(c + 1):  # loop over the paths from bottom to top
            for j in range(1, a + b + 1):  # loop over the inner sites
                if k > 0:
                    if s[k][j] == s[k][j - 1]:
                        #        (-1, 0)
                        #          |\
                        #          | \ (0, 0)
                        # (-1, -1) |  |
                        #           \ |
                        #            \|
                        #          (0, -1)
                        verts["L"].append(
                            [
                                (j + dx, s[k][j] + dy)
                                for dx, dy in [(0, 0), (-1, 0), (-1, -1), (0, -1)]
                            ]
                        )
                    else:
                        #           (0, 0)
                        #            /|
                        #           / |
                        # (-1, -1) |  | (0, -1)
                        #          | /
                        #          |/
                        #        (-1, -2)
                        verts["R"].append(
                            [
                                (j + dx, s[k][j] + dy)
                                for dx, dy in [(0, 0), (-1, -1), (-1, -2), (0, -1)]
                            ]
                        )

                for l in range(s[k][j] + 1, s[k + 1][j]):
                    #         (0, 0)
                    #           /\
                    # (-1, -1) /  \ (1, 0)
                    #          \  /
                    #           \/
                    #         (0, -1)
                    verts["T"].append(
                        [
                            (j + dx, l + dy)
                            for dx, dy in [(0, 0), (-1, -1), (0, -1), (1, 0)]
                        ]
                    )
        return verts
