# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Perfectly Random Sampling of Lozenge Tilings by
Propp-Wilson's "coupling from the past"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

reference:
    [1]. Blog post at
       "https://possiblywrong.wordpress.com/2018/02/23/coupling-from-the-past/"
    [2]. Wilson's paper
       "Mixing times of lozenge tiling and card shuffling Markv chains".

"""
import random
from tqdm import tqdm


class LozengeTiling(object):
    r"""
    A lozenge tiling of a hexagon of size (axbxc) can be encoded as a set
    of c paths: P = { p_1, p_2, ..., p_c }, where

    1. these paths lie in the skewed `ac`-plane (see below).
    2. the i-th path p_i starts at (0, i), either moves up or moves down
       in each step, and ends at (a+b, b+i).
    3. two different paths p_i and p_j do not have any point in common.
    (See Wilson's paper [2] for figures showing this correspondence)

    We call such P a non-intersecting path system, or simply a path system.
    The correspondence between lozenge tilings and path systems is one-to-one.

    In our notation, P[k][j] is the "y-coordinate" of the j-th point of the
    k-th path in P.

    A partial order `<` can be defined on the set of path systems (hence the
    set of lozenge tilings): for two path systems P and Q, P <= Q if and only
    if for all k and j, it holds that P[k][j] <= Q[k][j]. The maximal element
    in this ordering is the one with all its paths firstly move up b steps and
    then move down a steps, whereas the minimal element is the one with all its
    paths firstly move down a steps and then move up b steps.

    The set of all path systems (hence the set of lozenge tilings) can also
    be endowed with a Markov chain structure, the rule is:
    1. choose a uniformly random interior point in P. Let this point lie in the
       k-th path p_k and be the j-th point of p_k.
    2. try to update P at P[k][j]: with probability 1/2 we try to "push up"
       P at P[k][j]: we increase P[k][j] by 1, and with probability 1/2 we
       try to "push down" P at P[k][j]: we decrease P[k][j] by 1. If after
       this operation P is still valid, i.e. still being non-intersecting,
       then we succeeded and got a new path system, otherwise we leave P
       remain untouched.

    It's easy to show this Markov chain is irreducible and aperiodic, hence
    its stationary distribution is the uniform one. More importantly, the
    evolving rule of this chain respects the partial ordering `<`: if P <= Q
    and we try to update P, Q using the same randomness (both pushing up or
    pushing down at the same position), and the resulting states are P' and Q',
    then it holds P' <= Q'. In this case we call this chain "monotone".

    Propp an Wilson's result is that for a monotone Markov chain if we run two
    versions of the chain simultaneously from the past, one starts from the
    minimal state and the other starts from the maximal state, and if these
    two chains are coupled together at time 0, then this coupling gives us a
    random sampling among all states from stationary distribution.

    The key ingredient to make the algorithm work correctly is that one must
    always reuse the same randomness when looking further to the past to
    re-run the chains.

    Note: in the `ac`-plane, where `a` is the x-axis and `c` is the y-axis,
    for a path p, each step in p either moves up (in the b-direction where
    b = a + c) or moves down (in the a-direction). If it moves up then the x
    and y coordinates are both increased by 1, else it moves down and only the
    x coordinate is increased by 1. For all path systems, their 0-th and
    (c+1)-th paths are the same and are used for auxiliary purpose.

            /\
        |  /  \
        | /    \
        |/      \
     y-axis      |
        |   /    |
      c |  /     |
        | / b    |
        |/       |
         \      /
        a \    /
           \  /
            \/
          x-axis

    """
    def __init__(self, size):
        """
        `size`: three integers that specify the side lengths of the hexagon.
        """
        self.size = size

    @property
    def min_max_states(self):
        """Return the minimal and maximal states of the Markov chain.
        The minimal state is the one with no boxes and the maximal
        state is the one full of boxes.
        """
        a, b, c = self.size
        s0 = [[max(j - a, 0) if k == 0 else k + min(j, b)
               for j in range(a + b + 1)] for k in range(c + 2)]
        s1 = [[c + 1 + min(j, b) if k == c + 1 else k + max(j - a, 0)
               for j in range(a + b + 1)] for k in range(c + 2)]
        return s0, s1

    def new_random_update(self):
        """Return a new update operation."""
        a, b, c = self.size
        return (random.randint(1, c),  # a random path
                random.randint(1, a + b - 1),  # a random position in this path
                random.randint(0, 1))  # a random direction (up or down)

    def update(self, u, s):
        """
        Update a state `s` by a random update operation `u`.
        """
        k, j, direction = u
        if direction == 1:  # push up
            if (s[k][j - 1] == s[k][j] < s[k][j + 1] < s[k + 1][j]):
                s[k][j] += 1
        else:  # push down
            if (s[k - 1][j] < s[k][j - 1] < s[k][j] == s[k][j + 1]):
                s[k][j] -= 1

    def run_cftp(self):
        """
        Return a state sampled from stationary distribution using monotone CFTP.
        """
        bar = tqdm(desc="Running cftp", unit=" steps")
        updates = [(random.getstate(), 1)]
        while True:
            s0, s1 = self.min_max_states
            rng_next = None
            for rng, steps in updates:
                random.setstate(rng)
                for _ in range(steps):
                    u = self.new_random_update()
                    self.update(u, s0)
                    self.update(u, s1)
                    bar.update(1)
                if rng_next is None:
                    rng_next = random.getstate()
            if s0 == s1:
                break
            else:
                updates.insert(0, (rng_next, 2**len(updates)))
        random.setstate(rng_next)
        bar.close()
        return s0

    def tiles(self, s):
        """
        Return the vertices of the lozenges in the tiling defined by `s`.
        """
        a, b, c = self.size
        verts = {"L": [], "R": [], "T": []}
        for k in range(c + 1):
            for j in range(1, a + b + 1):
                if k > 0:
                    if s[k][j] == s[k][j - 1]:
                        verts["L"].append([(j + dx, s[k][j] + dy) for dx, dy in
                                           [(0, 0), (-1, 0), (-1, -1), (0, -1)]])
                    else:
                        verts["R"].append([(j + dx, s[k][j] + dy) for dx, dy in
                                           [(0, 0), (-1, -1), (-1, -2), (0, -1)]])
                for l in range(s[k][j] + 1, s[k + 1][j]):
                    verts["T"].append([(j + dx, l + dy) for dx, dy in
                                       [(0, 0), (-1, -1), (0, -1), (1, 0)]])
        return verts
