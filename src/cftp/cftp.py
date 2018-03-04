# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Perfectly random sampling of lozenge tilings
by Propp-Wilson's "coupling from the past"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

reference: see the blog post
  https://possiblywrong.wordpress.com/2018/02/23/coupling-from-the-past/
"""
import random
from draw import draw_tiling


def coupling_from_the_past(mc):
    """
    Run cftp on a finite monotone Markov chain `mc`.
    Return a state of `mc` sampled from stationary distribution.
    """
    updates = [(random.getstate(), 1)]
    while True:
        lower, upper = mc.min_max_states
        rng_next = None
        for rng, steps in updates:
            random.setstate(rng)
            for _ in range(steps):
                u = mc.random_update()
                lower.update(u)
                upper.update(u)
            if rng_next is None:
                rng_next = random.getstate()
        if lower == upper:
            break
        else:
            updates.insert(0, (rng_next, 2**len(updates)))
    random.setstate(rng_next)
    return upper


class LozengeTiling(object):
    """
    A lozenge tiling of a hexagon of size (a x b x c) can be
    viewed in two ways:
    1. A set of stacked boxes in a 3D room that satisfies
       a descending rule (also called a restricted plane partition).
    2. A set of non-intersecting lattice paths.

    We will run cftp on the space of all lozenge tilings of a given hexagon
    using the second representation, and view the result using the first way.
    """
    def __init__(self, size):
        """size: a tuple of three positive integers [a, b, c]."""
        self.size = tuple(size)
        a, b, c = size
        # paths: a 2D list consists of c+2 lists.
        # the first and last lists are used as bounding paths,
        # only the 1-th to c-th list correspondes to the actual non-intersecting
        # path system that represents the lozenge tiling.
        self.paths = None

    def __eq__(self, other):
        return self.paths == other.paths

    def random_update(self):
        """
        Return a random position (to be updated) and a 
        random operation (push up or push down).
        """
        a, b, c = self.size
        return (random.randint(1, c),
                random.randint(1, a+b-1),
                random.randint(0, 1))

    def update(self, u):
        """
        Try to update current paths.
        """
        a, b, c = self.size
        k, j, direction = u

        if direction == 1:  # push up
            if (self.paths[k][j-1] == self.paths[k][j]
                < self.paths[k][j+1] < self.paths[k+1][j]):
                self.paths[k][j] += 1

        else:  # push down
            if (self.paths[k-1][j] < self.paths[k][j-1]
                < self.paths[k][j] == self.paths[k][j+1]):
                self.paths[k][j] -= 1

    @property
    def min_max_states(self):
        """
        Return the min and max states of the Markov chain.
        """
        s0 = LozengeTiling(self.size)
        s1 = LozengeTiling(self.size)
        a, b, c = self.size
        s0.paths = [[max(j-a, 0) if k == 0 else k+min(j, b)
                     for j in range(a+b+1)] for k in range(c+2)]
        s1.paths = [[c+1+min(j, b) if k == c+1 else k+max(j-a, 0)
                     for j in range(a+b+1)] for k in range(c+2)]
        return s0, s1

    def to_plane_partition(self):
        """
        Convert the path system to a plane partition for drawing.
        The representation of the returned plane partition here is
        a bit different from the usual one: the rows of the list
        are the horizontal layers of the boxes.
        """
        a, b, c = self.size
        result = []
        for path in self.paths[1:-1]:
            pp = []
            binary = [path[i+1] - path[i] for i in range(len(path) - 1)]
            ht = 0
            for x in binary:
                if x == 1 and ht < a:
                    pp.append(a-ht)
                else:
                    ht += 1
            result.append(pp)
        return result[::-1]

      
def main(size):
    mc = LozengeTiling(size)
    T = coupling_from_the_past(mc)
    draw_tiling(T)
    
    
if __name__ == "__main__":
    main((20, 20, 20))
