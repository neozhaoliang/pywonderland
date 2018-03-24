# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Perfectly Random Sampling of Lozenge Tilings by
Propp-Wilson's "coupling from the past"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

reference: see the blog post
  https://possiblywrong.wordpress.com/2018/02/23/coupling-from-the-past/
"""
import random
from tqdm import tqdm


def coupling_from_the_past(mc, desc):
    """
    Run cftp on a finite monotone Markov chain `mc`.
    Return a state of `mc` sampled from stationary distribution.
    """
    bar = tqdm(desc=desc, unit=" steps")
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
                bar.update(1)
            if rng_next is None:
                rng_next = random.getstate()
        if lower == upper:
            break
        else:
            updates.insert(0, (rng_next, 2**len(updates)))
    random.setstate(rng_next)
    bar.close()
    return upper

  
class LozengeTiling(object):
    """
    A lozenge tiling of a hexagon of size (a x b x c) can be
    viewed in two ways:
    1. A set of stacked boxes in a 3D room that satisfies
       a descending rule (also called a restricted plane partition).
    2. A set of non-intersecting lattice paths.

    We will run cftp on the space of all lozenge tilings of a given hexagon
    using the second representation, and visualize the result using the first way.
    """
    def __init__(self, size):
        """size: a tuple of three positive integers [a, b, c]."""
        self.size = tuple(size)
        # paths: a 2D list consists of c+2 1D lists.
        # the first and the last lists are used as bounding paths,
        # only the 1-th to the c-th lists corresponde to the actual non-intersecting
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
                random.randint(1, a + b - 1),
                random.randint(0, 1))

    def update(self, u):
        """Try to update current paths."""
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
        """Return the min and the max states of the monotone Markov chain."""
        s0 = LozengeTiling(self.size)
        s1 = LozengeTiling(self.size)
        a, b, c = self.size
        s0.paths = [[max(j-a, 0) if k == 0 else k+min(j, b)
                     for j in range(a+b+1)] for k in range(c+2)]
        s1.paths = [[c+1+min(j, b) if k == c+1 else k+max(j-a, 0)
                     for j in range(a+b+1)] for k in range(c+2)]
        return s0, s1

    def tiles(self):
        """Return the vertices of the lozenges of each type."""
        a, b, c = self.size
        # use three lists to hold the three types of lozenges.
        verts = [[], [], []]
        for k in range(c+1):
            for j in range(1, a+b+1):
                if k > 0:
                    if self.paths[k][j] == self.paths[k][j-1]:  # down
                        verts[0].append([(j+dx, self.paths[k][j]+dy) for dx, dy in
                                         ((0, 0), (-1, 0), (-1, -1), (0, -1))])                        
                    else:  # up
                        verts[1].append([(j+dx, self.paths[k][j]+dy) for dx, dy in 
                                         ((0, 0), (-1, -1), (-1, -2), (0, -1))])                
                for l in range(self.paths[k][j]+1, self.paths[k+1][j]):
                    verts[2].append([(j+dx, l+dy) for dx, dy in
                                     ((0, 0), (-1, -1), (0, -1), (1, 0))])                    
        return verts

    def run_cftp(self):
        return coupling_from_the_past(self, desc="Running cftp on a {}x{}x{} hexagon".format(*self.size))
