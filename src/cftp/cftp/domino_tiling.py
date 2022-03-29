"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Perfectly random domino tiling of a rectangle using
Propp-Wilson's "coupling from the past" algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import random
from .cftp import MonotoneMarkovChain


def generate_path(k, n, offset=0, flip=False):
    r"""A helper function for generating a path consists of n steps like this:

       -----
      /     \
     /       \
    /         \

    (k steps upward and k steps downward at the two sides)
    when flip=True it's turned up-side-down

    \         /
     \       /
      \     /
       -----

    """
    # necessarily k <= n / 2
    k = min(k, n // 2)
    if flip:
        return [max(i + k - n, 0) - min(i, k) + offset for i in range(n + 1)]

    return [min(i, k) - max(i + k - n, 0) + offset for i in range(n + 1)]


class DominoTiling(MonotoneMarkovChain):

    """
    This class builds the "monotone" Markov chain structure on the set
    of domino tilings of an (a x b) rectangle (both a, b are even). A
    tiling is represented by m+2 pairwise non-intersecting paths where
    m = b/2 and the 0-th and (m+1)-th paths are fixed and are used for
    bounding the intermediate m paths.
    """

    def __init__(self, size):
        """
        :param size: (width, height) of the rectangle.
        """
        a, b = size
        assert a % 2 == b % 2 == 0, \
            "The width and height of the rectangle must both be even integers"
        self.size = size

    def min_max_states(self):
        """
        The minimum state is the path system in which each path goes
        downward as deep as possible, while the maximum state is the
        path system in which each path goes upward as high as possible.
        (of course all paths in a system must have no intersections)
        """
        a, b = self.size
        m = b // 2
        s0 = [
            [2 * m + 1] * (a + 1) if k == m + 1 else generate_path(k - 1, a, 2 * k - 1, True)
            for k in range(m + 2)
        ]
        s1 = [
            [0] * (a + 1) if k == 0 else generate_path(m + 1 - k, a, 2 * k - 1)
            for k in range(m + 2)
        ]
        return s0, s1

    def new_random_update(self):
        """
        Generate a random operation:
        1. Choose a random path with index in [1, m] (note the first path and the
           last path are always fixed)
        2. Choose an interior vertex on this path. (note the two ends of each path
           are also fixed)
        3. Choose a random direction (up/down) and try to push the path along this
           direction at this vertex.
        """
        a, b = self.size
        m = b // 2
        return (
            random.randint(1, m),
            random.randint(1, a - 1),
            random.randint(0, 1)
        )

    def update(self, state, operation):
        s = state
        k, j, dy = operation
        if dy == 0:  # push up
            # if three successvie vertices have the same height, does the middle
            # one lies inside a horizontal domino, or it lies on the border of two
            # adjacent dominoes? We can only push the path in the former case.
            if s[k][j - 1] == s[k][j] == s[k][j + 1] < s[k + 1][j] - 1:
                # We start a search towards the left to check which case we are in.
                # A horizontal domino always covers two vertices, so if there are
                # an odd number of successive vertices align on the left of this
                # vertex (including this one) and they all have the same height,
                # then this vertex is inside a horizontal domino.
                count = 0
                ind = j
                while (ind >= 1 and s[k][ind] == s[k][ind - 1]):
                    ind -= 1
                    count += 1
                if count % 2 == 1:
                    s[k][j] += 1

            # else if this is a 'valley', we push it upward
            elif s[k][j - 1] > s[k][j] < s[k][j + 1] < s[k + 1][j]:
                s[k][j] += 1

        else:  # push down
            if s[k][j - 1] == s[k][j] == s[k][j + 1] > s[k - 1][j] + 1:
                count = 0
                ind = j
                while (ind >= 1 and s[k][ind] == s[k][ind - 1]):
                    ind -= 1
                    count += 1
                if count % 2 == 1:
                    s[k][j] -= 1

            # else if this is a 'peak', we push it downward
            elif s[k][j - 1] < s[k][j] > s[k][j + 1] > s[k - 1][j]:
                s[k][j] -= 1

    def get_tiles(self, state):
        """
        Get vertices of all the dominoes in the tiling given by a set
        of non-intersecting paths `state`.

        Here the rectangle is placed on an infinitely large white/black
        checkerboard, there are four types of dominoes:
        1. Two horizontal types |W B| and |B W|.
        2. Two vertical types |W| and |B|.
                              |B|     |W|
        """
        s = state
        a, b = self.size
        m = b // 2
        verts = {"v1": [], "v2": [], "h1": [], "h2": []}

        for k in range(1, m + 1):
            j = 1
            while j <= a:
                if s[k][j - 1] == s[k][j]:
                    # a horizontal edge inside a horizontal domino
                    # (-1, 0)   (0, 0)   (1, 0)
                    #   --------------------
                    #   |         |        |
                    #   --------------------
                    # (-1, -1)           (1, -1)
                    verts["h1"].append(
                        [
                            (j + dx, s[k][j] + dy)
                            for dx, dy in [(-1, 0), (-1, -1), (1, -1), (1, 0)]
                        ]
                    )
                    j += 2

                elif s[k][j - 1] < s[k][j]:
                    # an upward edge inside a vertical domino
                    # (-1, 0) ---- (0, 0)
                    #         |  |
                    #         | /|
                    #         |/ |
                    #         |  |
                    # (-1, -2)---- (0, -2)
                    verts["v1"].append(
                        [
                            (j + dx, s[k][j] + dy)
                            for dx, dy in [(0, 0), (-1, 0), (-1, -2), (0, -2)]
                        ]
                    )
                    j += 1

                else:
                    # a downward edge inside a vertical domino
                    # (-1, 1) ---- (0, 1)
                    #         |  |
                    #         |\ |
                    #         | \| (0, 0)
                    #         |  |
                    # (-1, -1)---- (0, -1)
                    verts["v2"].append(
                        [
                            (j + dx, s[k][j] + dy)
                            for dx, dy in [(0, -1), (-1, -1), (-1, 1), (0, 1)]
                        ]
                        )
                    j += 1

        # finally collect all horizontal dominoes that have no edge inside them
        for k in range(m + 1):
            for j in range(1, a + 1):
                for l in range(s[k][j] + 1, s[k + 1][j]):
                    count = 0
                    ind = j - 1
                    while ind >= 0 and s[k][ind] < l < s[k + 1][ind]:
                        ind -= 1
                        count += 1
                    if count % 2 == 1:
                        verts["h2"].append(
                            [
                                (j + dx, l + dy)
                                for dx, dy in [(-1, 0), (-1, -1), (1, -1), (1, 0)]
                            ]
                        )

        return verts
