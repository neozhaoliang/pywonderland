# -*- coding: utf-8 -*-
r"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Perfectly random lozenge tiling of a hexagon using
Propp-Wilson's "coupling from the past" algorithm
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This program samples a random lozenge tiling of a
(a x b x c) hexagon from the uniform distribution.
In the code a lozeng tiling is represented by a path
system consists of (c+2) non-intersecting paths in the
ac-plane, where the i-th path (i=0, 1, ..., c+1) starts
at (0, i), moves up (in direction b) or moves down
(in direction a) in each step and ends at (2a, c+i).

The updating rule of the Markov chain is: choose a random
path and a random position on this path, and try to push
up/down the path at this position. If the resulting path
system is not non-intersecting, i.e. does not represent a
tiling, then leave the path untouched.

      c/y-axis
            |    /\
            |   /  \
            | b/    \ a
            | /      \
            |/        \
            |          |
            |          |
          c |          | c
            |  x-axis  |
            |------    |
           O \        /
              \      /
             a \    / b
                \  /
                 \/
                  \
                   \
                   a-axis

REFERENCES:


[1]. Blog post at
     "https://possiblywrong.wordpress.com/2018/02/23/coupling-from-the-past/"

[2]. Wilson's paper
     "Mixing times of lozenge tiling and card shuffling Markv chains".

[3]. Häggström's book
     "Markov chains and algorithmic applications"

[4]. Book by David Asher Levin, Elizabeth Lee Wilmer, and Yuval Peres
     "Markov chains and mixing times".

"""
import random

from tqdm import tqdm


def run_cftp(mc):
    """
    Sample a random state in a finite, irreducible Markov chain from its
    stationary distribution using monotone CFTP.
    `mc` is a Markov chain object that implements the following methods:
        1. `new_random_update`: return a new random updating operation.
        2. `update`: update a state by an updating operation.
        3. `min_max_state`: return the minimum and maximum states.
    """
    bar = tqdm(desc="Running cftp", unit=" steps")

    updates = [(random.getstate(), 1)]
    while True:
        # run two versions of the chain from the two min, max states
        # in each round.
        s0, s1 = mc.min_max_states
        rng_next = None
        for rng, steps in updates:
            random.setstate(rng)
            for _ in range(steps):
                u = mc.new_random_update()
                mc.update(s0, u)
                mc.update(s1, u)
                bar.update(1)
            # save the latest random seed for future use.
            if rng_next is None:
                rng_next = random.getstate()
        # check if these two chains are coupled at time 0.
        if s0 == s1:
            break
        # if not coupled the look further back into the past.
        else:
            updates.insert(0, (rng_next, 2 ** len(updates)))

    random.setstate(rng_next)
    bar.close()
    return s0


class LozengeTiling(object):

    """
    This class builds the "monotone" Markov chain structure on the set
    of lozenge tilings of an (a x b x c) hexagon. A tiling is represented
    by c+2 pairwise non-intersecting paths, where the 0-th and (c+1)-th
    paths are fixed and are used for auxiliary purpose.
    """

    def __init__(self, size):
        """
        :size: a tuple of three integers, they are the side lengths of the hexagon.
        """
        self.size = size

    @property
    def min_max_states(self):
        """
        Return the minimum and maximum tilings. From a bird's view, the minimum
        tiling is the one that correspondes to a room filled full of boxes and
        the maximum tiling is the one that correspondes to an empty room.
        """
        a, b, c = self.size
        # min state that all paths move downward and then upward.
        # the tiling correspondes to a "full box" filled with cubes.
        s0 = [
            [max(j - a, 0) if k == 0 else k + min(j, b) for j in range(a + b + 1)]
            for k in range(c + 2)
        ]
        # max state that all paths move upward and then move downward.
        # the tiling correspondes to an "empty box" with no cubes.
        s1 = [
            [
                c + 1 + min(j, b) if k == c + 1 else k + max(j - a, 0)
                for j in range(a + b + 1)
            ]
            for k in range(c + 2)
        ]
        return s0, s1

    def new_random_update(self):
        """
        Return a new update operation.
        """
        a, b, c = self.size
        return (
            random.randint(1, c),  # a random path
            random.randint(1, a + b - 1),  # a random position in this path
            random.randint(0, 1),
        )  # a random direction (up or down)

    def update(self, s, u):
        """Update a state `s` by a random update operation `u`.
        """
        k, j, dy = u
        # try to push up
        if dy == 1:
            if s[k][j - 1] == s[k][j] < s[k][j + 1] < s[k + 1][j]:
                s[k][j] += 1
        # try to push down
        else:
            if s[k - 1][j] < s[k][j - 1] < s[k][j] == s[k][j + 1]:
                s[k][j] -= 1

    def get_tiles(self, s):
        """
        Return the vertices of the lozenges in the tiling defined by `s`.
        """
        a, b, c = self.size
        verts = {"L": [], "R": [], "T": []}
        for k in range(c + 1):
            for j in range(1, a + b + 1):
                if k > 0:
                    if s[k][j] == s[k][j - 1]:
                        verts["L"].append(
                            [
                                (j + dx, s[k][j] + dy)
                                for dx, dy in [(0, 0), (-1, 0), (-1, -1), (0, -1)]
                            ]
                        )
                    else:
                        verts["R"].append(
                            [
                                (j + dx, s[k][j] + dy)
                                for dx, dy in [(0, 0), (-1, -1), (-1, -2), (0, -1)]
                            ]
                        )
                for l in range(s[k][j] + 1, s[k + 1][j]):
                    verts["T"].append(
                        [
                            (j + dx, l + dy)
                            for dx, dy in [(0, 0), (-1, -1), (0, -1), (1, 0)]
                        ]
                    )
        return verts
