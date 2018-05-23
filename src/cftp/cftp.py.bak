# -*- coding: utf-8 -*-
r"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Perfectly Random Sampling of Lozenge Tilings by
Propp-Wilson's "coupling from the past"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

REFERENCES:
   
[1]. Blog post at
     "https://possiblywrong.wordpress.com/2018/02/23/coupling-from-the-past/"

[2]. Wilson's paper
     "Mixing times of lozenge tiling and card shuffling Markv chains".

A short introduction to the math and the code:

Consider this problem: let `M` be a finite irreducible Markov chain, `M` has
an unique stationary distribution `π`). How can one sample a random state in
`M` from `π`? The traditional approach is to pick an arbitrary initial state
`s0`, then run the chain for a sufficiently large number of times, with the
final state as the sample.

The problem with this approach is that it's an approximate sampling, not an
exact sampling: usually the distribution of the final state can be arbitrarily
close to `π`, but never exactly be `π`, also the number of runs needed to give
a nice approximation (called the mixing time) can be quite hard to analyze.

Propp and Wilson found an ingenious approach called "coupling from the past"
which gives an exact sampling. The idea is that instead of running one chain
to the future for a sufficiently long time, we run many different versions
of the chain from a sufficiently long past, using the same randomness to update
all chains in each step, and see if they are "coupled" at time 0, if so then
their common state at time 0 is an exact sampling from `π`, else we simply look
further back in the past and reuse the randomness to update the chains.

When `M` is "monotone" this computation can be simplified by just running two
versions of `M`: one starts from the maximal state and one from the minimal
state.

Now let `S` be the set of all lozenge tilings of an (axbxc) hexagon, how can
we pick a random tiling in `S` with uniform probability? The idea is if we
could make `S` an irreducible, aperiodic and monotone Markov chain (so the
stationary distribution is the uniform one), then "coupling from the past"
applies.

Note a lozenge tiling of a hexagon of size (axbxc) can be encoded as a set of
c paths: P = { p_1, p_2, ..., p_c }, where

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

    1. these paths lie in the skewed `ac`-plane.
    2. the i-th path p_i starts from (0, i), either moves up or moves down
       in each step, and ends at (a+b, b+i). (this is called a Gauss path)
    3. two different paths p_i and p_j do not have any points in common.
    (See Wilson's paper [2] for figures showing this correspondence)

We call such P a non-intersecting path system, or simply a path system.
The correspondence between lozenge tilings and path systems is one-to-one.

In our notation, P[k][j] is the "y-coordinate" of the j-th point of the k-th
path in P.

A partial order `<=` can be defined on the set of path systems: for two path
systems P and Q, P <= Q if and only if for all k and j, it holds that
P[k][j] <= Q[k][j]. The maximal element in this ordering is the one with all
its paths firstly move up b steps and then move down a steps, whereas the
minimal element is the one with all its paths firstly move down a steps and
then move up b steps.

The set of all path systems can also be endowed with a Markov chain structure,
the rule is:

    1. choose a uniformly random interior point in P. Let this point lie in the
       k-th path p_k and be the j-th point of p_k.
    2. try to update P at P[k][j]: with probability 1/2 we try to "push up"
       P at P[k][j]: we increase P[k][j] by 1, and with probability 1/2 we
       try to "push down" P at P[k][j]: we decrease P[k][j] by 1. If after
       this operation P is still valid, i.e. still being non-intersecting,
       then we succeeded and got a new path system, otherwise we leave P
       remain untouched.

It's easy to see this Markov chain is irreducible and aperiodic.

Note: in the `ac`-plane, `a` is the x-axis and `c` is the y-axis. For a path p,
each step in p either moves up (in the b-direction where b = a + c) or moves 
down (in the a-direction). If it moves up then the x and y coordinates are both
increased by 1, if it moves down then only the x coordinate is increased by 1.
For all path systems, their 0-th and (c+1)-th paths are the same and are used
for auxiliary purpose.
"""
import random
from tqdm import tqdm


def run_cftp(mc):
    """
    Sample a random state in a Markov chain `mc` from its stationary
    distribution using monotone CFTP.
    """
    bar = tqdm(desc="Running cftp", unit=" steps")
    updates = [(random.getstate(), 1)]
    while True:
        s0, s1 = mc.min_max_states
        rng_next = None
        for rng, steps in updates:
            random.setstate(rng)
            for _ in range(steps):
                u = mc.new_random_update()
                mc.update(s0, u)
                mc.update(s1, u)
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


class LozengeTiling(object):
    """
    This class builds the "monotone" Markov chain structure on the set
    of lozenge tilings of an (axbxc) hexagon. A tiling is represented
    by c+2 paths (the 0-th and (c+1)-th path are fixed and are used for
    auxiliary purpose).
    """

    def __init__(self, a, b, c):
        """a, b, c: size of the hexagon."""
        self.size = (a, b, c)

    @property
    def min_max_states(self):
        """Return the minimal and maximal states of the Markov chain."""
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

    def update(self, s, u):
        """Update a state `s` by a random update operation `u`."""
        k, j, dy = u
        # try to push up
        if dy == 1:
            if (s[k][j - 1] == s[k][j] < s[k][j + 1] < s[k + 1][j]):
                s[k][j] += 1
        # try to push down
        else:
            if (s[k - 1][j] < s[k][j - 1] < s[k][j] == s[k][j + 1]):
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
                        verts["L"].append([(j + dx, s[k][j] + dy) for dx, dy in
                                           [(0, 0), (-1, 0), (-1, -1), (0, -1)]])
                    else:
                        verts["R"].append([(j + dx, s[k][j] + dy) for dx, dy in
                                           [(0, 0), (-1, -1), (-1, -2), (0, -1)]])
                for l in range(s[k][j] + 1, s[k + 1][j]):
                    verts["T"].append([(j + dx, l + dy) for dx, dy in
                                       [(0, 0), (-1, -1), (0, -1), (1, 0)]])
        return verts